"""Prototype data-team agent: the model writes Python, a sandboxed kernel runs it.

Unlike the RAG bot, model-generated code is executed here, so the guards stack:
host-side static check -> audit hook and read-only SQLite inside the kernel ->
every number in the final answer must appear in a cell output. This is a
standalone prototype, not wired into grounded_rag/api_server. The kernel is not
an OS-level sandbox: native code in numpy/pandas is not seen by the audit hook.
"""
import ast
import os
import re
import sqlite3
import sys
import tempfile
import time
from dataclasses import asdict,dataclass,field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from queue import Empty

import nbformat
import psutil
import requests
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec
from nbformat import v4

from .rag_answer import chat,numbers

ROOT=Path(__file__).resolve().parents[1]
DB_PATH=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
OUTPUT_DIR=ROOT/'runtime/notebook_agent'
DEFAULT_MODEL='qwen3:4b-instruct-2507-q4_K_M'
MAX_CELLS=8;MAX_MODEL_CALLS=12;MAX_IDLE_TURNS=4;CELL_TIMEOUT=30;TOTAL_TIMEOUT=300;MAX_TOKENS=900;LOAD_TIMEOUT=420
MEMORY_LIMIT=1_500_000_000;MAX_OUTPUT_CHARS=200_000;OBSERVED_CHARS=1800;OLD_OBSERVED_CHARS=400

STEP_SCHEMA={'type':'object','properties':{'thought':{'type':'string','maxLength':300},'code':{'type':'string'},
    'done':{'type':'boolean'},'answer':{'type':'string','maxLength':800}},
    'required':['thought','code','done','answer'],'additionalProperties':False}

ALLOWED_IMPORTS={'pandas','numpy','sqlite3','matplotlib'}
FORBIDDEN_NAMES={'exec','eval','compile','open','getattr','setattr','delattr','globals','locals','vars','input','breakpoint',
    'help','exit','quit','memoryview','get_ipython','os','sys','subprocess','socket'}
FORBIDDEN_ATTRS={'system','popen','spawn','os','sys','io','subprocess','socket','ctypes','ctypeslib','compat','builtins','f2py','testing',
    'connect','executescript','enable_load_extension','load_extension','set_authorizer','backup','iterdump','create_function','create_aggregate',
    'load','save','savez','savez_compressed','loadtxt','savetxt','genfromtxt','fromfile','tofile','memmap','fromregex','DataSource','eval','query','ExcelWriter','HDFStore'}
ALLOWED_READ_TO={'read_sql','read_sql_query','to_datetime','to_numeric','to_string','to_dict','to_list','to_numpy','to_frame','to_period','to_timestamp','to_timedelta'}
SQL_WRITE=re.compile(r'(?is)(?:^|;)\s*(?:insert\s+(?:or\s+\w+\s+)?into|update\s+\S+\s+set|delete\s+from|replace\s+into|drop\s+(?:table|view|index|trigger)|alter\s+table|create\s+(?:temp|temporary|table|view|index|trigger|unique|virtual)|attach\s|detach\s|vacuum\b|reindex\b)')


def forbidden_attr(name):
    return name.startswith('_') or name in FORBIDDEN_ATTRS or (bool(re.match(r'(read|to)_',name)) and name not in ALLOWED_READ_TO)


def check_code(code):
    """Return why the code must not run; empty means it may reach the kernel."""
    try:tree=ast.parse(code)
    except (SyntaxError,ValueError,RecursionError,MemoryError) as exc:
        if re.search(r'(?m)^\s*[!%?]',code):return ['Không dùng lệnh shell hoặc magic (!, %, ?).']
        return [f'Lỗi cú pháp: {exc}']
    issues=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            modules=[alias.name for alias in node.names]
        elif isinstance(node,ast.ImportFrom):
            modules=['.'*node.level+(node.module or '')]+[f'{node.module}.{alias.name}' for alias in node.names]
        elif isinstance(node,ast.Name):
            modules=[]
            if node.id in FORBIDDEN_NAMES or node.id.startswith('__'):issues.append(f'Không được dùng tên {node.id}.')
        elif isinstance(node,ast.Attribute):
            modules=[]
            if forbidden_attr(node.attr):issues.append(f'Không được dùng thuộc tính .{node.attr}.')
        elif isinstance(node,ast.Constant) and isinstance(node.value,str):
            modules=[]
            if '__' in node.value:issues.append('Chuỗi không được chứa __.')
            if SQL_WRITE.search(node.value):issues.append('Chỉ được đọc dữ liệu; câu lệnh ghi SQL bị từ chối.')
        else:modules=[]
        for module in modules:
            parts=module.split('.')
            if parts[0] not in ALLOWED_IMPORTS:issues.append(f'Không được import {module}; chỉ dùng {", ".join(sorted(ALLOWED_IMPORTS))}.')
            elif any(forbidden_attr(part) for part in parts[1:]):issues.append(f'Không được import {module}.')
    return list(dict.fromkeys(issues))


# Runs once inside the kernel before any generated code. The audit hook cannot be
# removed afterwards and keeps working when the static check above is bypassed.
BOOTSTRAP=r'''
def _boot(db_uri,workspace,mpl_dir):
    import os,sys
    import numpy as np,pandas as pd,sqlite3
    import matplotlib
    import matplotlib.pyplot as plt
    ip=get_ipython();ip.automagic=False
    def no_shell(*args,**kwargs):raise PermissionError('shell bị chặn')
    ip.system=ip.system_raw=ip.system_piped=ip.getoutput=no_shell
    pd.set_option('display.max_columns',50,'display.width',170,'display.max_rows',80,'display.float_format','{:.4f}'.format)
    conn=sqlite3.connect(db_uri,uri=True)
    allowed={sqlite3.SQLITE_SELECT,sqlite3.SQLITE_READ,33}  # 33 = SQLITE_RECURSIVE
    def authorize(action,arg1,arg2,database,trigger):
        if action in allowed:return sqlite3.SQLITE_OK
        if action==sqlite3.SQLITE_FUNCTION and arg2!='load_extension':return sqlite3.SQLITE_OK
        if action==sqlite3.SQLITE_PRAGMA and arg1=='table_info':return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY
    conn.set_authorizer(authorize)
    norm=lambda path:os.path.normcase(os.path.abspath(path))
    write_roots=(norm(workspace),)
    read_roots=write_roots+(norm(mpl_dir),norm(sys.prefix),norm(sys.base_prefix))
    denied=('socket.connect','socket.bind','socket.getaddrinfo','socket.gethostbyname','socket.gethostbyaddr','socket.sendto','socket.sendmsg',
            'subprocess.','os.system','os.exec','os.fork','os.spawn','os.posix_spawn','os.startfile','ctypes.dlopen','ctypes.dlsym','ctypes.call_function','urllib.','http.client.',
            'ftplib.','smtplib.','poplib.','imaplib.','webbrowser.','winreg.','sqlite3.connect','sqlite3.enable_load_extension',
            'sqlite3.load_extension','os.remove','os.rename','os.rmdir','os.mkdir','shutil.')
    write_flags=os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_APPEND|os.O_TRUNC
    inside=lambda path,roots:any(path==root or path.startswith(root+os.sep) for root in roots)
    def guard(event,args):
        if event.startswith(denied):raise PermissionError(f'sandbox chặn {event}')
        if event=='open':
            path,mode,flags=args
            if not isinstance(path,(str,bytes,os.PathLike)):return
            path=norm(os.fsdecode(path))
            if path==norm(os.devnull):return
            writes=any(c in mode for c in 'wax+') if isinstance(mode,str) else bool(flags and flags&write_flags)
            if not inside(path,write_roots if writes else read_roots):raise PermissionError(f'sandbox chặn truy cập tệp {path}')
    sys.addaudithook(guard)
    return pd,np,plt,sqlite3,conn
'''


@dataclass
class Cell:
    code:str
    status:str
    text:str=''
    outputs:list=field(default_factory=list)
    seconds:float=0.0
    thought:str=''


@dataclass
class RunResult:
    question:str
    status:str
    answer:str
    model:str
    cells:list
    model_calls:int
    seconds:float
    notebook:str=''
    rejected_answer:str=''
    error:str=''

    @property
    def evidence(self):
        return '\n'.join(cell.text for cell in self.cells if cell.status=='ok')

    def summary(self):
        data=asdict(self);data['cell_count']=len(self.cells)
        for cell in data['cells']:cell.pop('outputs')
        return data


def clean_output(text):
    return re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',text)


def clip(text,limit):
    return text if len(text)<=limit else text[:limit]+f'\n...[cắt bớt {len(text)-limit} ký tự]'


def output_text(output):
    if output['output_type']=='stream':return ''.join(output['text'])
    if output['output_type']=='error':
        trace=clean_output('\n'.join(output['traceback']))
        return f"{output['ename']}: {clean_output(output['evalue'])}\n{trace[-700:]}"
    data=output.get('data',{})
    if 'image/png' in data:return '[đã vẽ biểu đồ]'
    text=data.get('text/plain','')
    return ''.join(text) if isinstance(text,list) else text


class SandboxKernel:
    """One throwaway kernel: read-only DB, temp cwd, no secrets in its environment."""

    def __init__(self,db_path=DB_PATH,output_dir=OUTPUT_DIR):
        self.db_path=Path(db_path).resolve();self.mpl_dir=Path(output_dir).resolve()/'.matplotlib'
        self.km=self.client=None;self.count=0

    def __enter__(self):
        self.mpl_dir.mkdir(parents=True,exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='nbagent-',ignore_cleanup_errors=True)
        self.workspace=Path(self.tmp.name)
        self.start();return self

    def __exit__(self,*exc):
        self.stop();self.tmp.cleanup()

    def environment(self):
        env={key:os.environ[key] for key in ('SYSTEMROOT','WINDIR','TEMP','TMP') if key in os.environ}
        return env|{'PATH':str(Path(sys.executable).parent),'USERPROFILE':str(self.workspace),'HOME':str(self.workspace),
            'IPYTHONDIR':str(self.workspace/'.ipython'),'MPLCONFIGDIR':str(self.mpl_dir),'MPLBACKEND':'module://matplotlib_inline.backend_inline',
            'PYTHONNOUSERSITE':'1','PYTHONIOENCODING':'utf-8','PYDEVD_DISABLE_FILE_VALIDATION':'1'}

    def start(self):
        self.km=KernelManager()
        self.km._kernel_spec=KernelSpec(display_name='notebook-agent',language='python',
            argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}','--HistoryManager.enabled=False','--IPKernelApp.ip=127.0.0.1'])
        self.km.connection_file=str(self.workspace/f'kernel-{time.time_ns()}.json')
        self.km.start_kernel(cwd=str(self.workspace),env=self.environment())
        self.client=self.km.client();self.client.start_channels();self.client.wait_for_ready(timeout=60)
        uri=self.db_path.as_uri()+'?mode=ro'
        boot=BOOTSTRAP+f'pd,np,plt,sqlite3,conn=_boot({uri!r},{str(self.workspace)!r},{str(self.mpl_dir)!r});del _boot\n'
        cell=self.execute(boot,60,silent=True)
        if cell.status!='ok':raise RuntimeError(f'Kernel bootstrap failed: {cell.text}')

    def stop(self):
        if self.client:self.client.stop_channels()
        if self.km and self.km.has_kernel:self.km.shutdown_kernel(now=True)
        self.km=self.client=None

    def memory(self):
        try:
            process=psutil.Process(self.km.provisioner.pid)
            return sum(item.memory_info().rss for item in [process,*process.children(recursive=True)])
        except (psutil.Error,AttributeError,TypeError):return 0

    def execute(self,code,timeout,silent=False):
        started=time.monotonic();deadline=started+timeout;checked=started
        message_id=self.client.execute(code,silent=silent,store_history=not silent,allow_stdin=False)
        outputs=[];size=0;status='ok'
        while True:
            now=time.monotonic()
            if now>=deadline:status='timeout';break
            if now-checked>=.5:
                checked=now
                if self.memory()>MEMORY_LIMIT:status='memory';break
            try:message=self.client.get_iopub_msg(timeout=min(deadline-now,.5))
            except Empty:
                if not self.km.is_alive():status='crashed';break
                continue
            if message['parent_header'].get('msg_id')!=message_id:continue
            kind=message['msg_type']
            if kind=='status' and message['content']['execution_state']=='idle':break
            if kind in ('stream','display_data','execute_result','error'):
                if kind=='error':status='error'
                if size<MAX_OUTPUT_CHARS:
                    output=v4.output_from_msg(message);outputs.append(output);size+=len(output_text(output))
        text=clean_output('\n'.join(filter(None,(output_text(item) for item in outputs))))
        return Cell(code=code,status=status,text=clip(text,MAX_OUTPUT_CHARS),outputs=outputs,seconds=round(time.monotonic()-started,2))

    def run(self,code,timeout=CELL_TIMEOUT):
        """Run one cell; a hung or oversized kernel is killed and replaced."""
        cell=self.execute(code,timeout)
        if cell.status in ('timeout','memory','crashed'):
            reason={'timeout':f'quá {timeout} giây','memory':'quá giới hạn bộ nhớ','crashed':'kernel bị dừng'}[cell.status]
            self.stop();self.start()
            cell.text=f'{cell.text}\n[Ô bị dừng: {reason}. Kernel đã khởi động lại, mọi biến đã mất.]'.strip()
        self.count+=1;return cell


def table_summary(db_path):
    conn=sqlite3.connect(Path(db_path).resolve().as_uri()+'?mode=ro',uri=True)
    try:
        names=[row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view') ORDER BY name")]
        return '\n'.join(f"{name}({','.join(row[1] for row in conn.execute(f'PRAGMA table_info({name})'))})" for name in names)
    finally:conn.close()


SYSTEM="""Bạn là chuyên viên dữ liệu của shop bán đồ công nghệ giả lập. Trả lời câu hỏi bằng cách viết Python chạy trong Jupyter rồi đọc kết quả.
Dữ liệu từ 2025-10 đến 2026-09, tiền là đồng VND. Bảng và cột:
{tables}
monthly_pnl mỗi tháng một dòng, month dạng 'YYYY-MM': net_revenue=doanh thu thuần, net_cogs=giá vốn, net_units=số đơn vị bán ròng, gross_profit=lãi gộp, operating_expenses=chi phí vận hành, operating_profit_before_interest_tax=lãi hoạt động trước lãi vay và thuế, order_count=số đơn, return_units=số đơn vị hoàn, refunds=tiền hoàn, purchases_received=giá trị hàng nhập nhận, operating_cash_flow_assuming_cash_settlement=dòng tiền hoạt động, target_revenue=mục tiêu doanh thu.
financial_ledger mỗi dòng một giao dịch, kind là 'sale' hoặc 'return'; dòng 'return' có revenue và cost âm, nên doanh thu ròng là SUM(revenue) không lọc kind. Bán ròng theo nhóm hàng thì nối products qua sku.
monthly_pnl đã có sẵn target_revenue, không cần nối monthly_targets để lấy mục tiêu doanh thu.
Biến có sẵn, không tạo lại: conn (SQLite chỉ đọc), pd, np, plt, sqlite3. Đọc bằng pd.read_sql(sql, conn). Không gọi sqlite3.connect, không đọc/ghi tệp, không dùng mạng, shell, os; chỉ import pandas, numpy, sqlite3, matplotlib.
Mỗi lượt trả đúng một JSON:
- Chưa có kết quả: thought là kế hoạch ngắn, code là một ô Python in kết quả bằng print, done=false, answer rỗng.
- Đã thấy kết quả trong output: code rỗng, done=true, answer là câu trả lời tiếng Việt.
Quy tắc: Chỉ lấy số từ output, chép nguyên con số, không tính nhẩm. Tự tính phần trăm hoặc chênh lệch trong code rồi print. Làm tròn đúng như câu hỏi yêu cầu. Nếu output báo lỗi, đọc lỗi và sửa code. Lịch sử các ô đã chạy nằm trong history."""

DATE_TOKENS=re.compile(r'\d{4}-\d{2}(?:-\d{2})?|\d{1,2}/\d{4}|tháng\s+\d{1,2}(?!\d)(?:\s+năm\s+\d{4}|/\d{4})?|quý\s+\d|năm\s+\d{4}|\bq\d\b')
NUMBER_TOKEN=re.compile(r'(?<!\w)(\d+(?:[.,]\d+)*)(?:\s*(triệu|trieu|tỷ|ty|nghìn|nghin))?')
UNIT={'triệu':1_000_000,'trieu':1_000_000,'tỷ':1_000_000_000,'ty':1_000_000_000,'nghìn':1000,'nghin':1000}


def unsupported_numbers(answer,evidence):
    """Numbers in the answer absent from the evidence, allowing only the rounding shown."""
    known={abs(value) for value in numbers(evidence)};missing=[]
    for match in NUMBER_TOKEN.finditer(DATE_TOKENS.sub(' ',answer.lower())):
        raw=match[1];grouped=re.fullmatch(r'\d{1,3}(?:[.,]\d{3})+',raw)
        places=0 if grouped or not re.search(r'[.,]',raw) else len(re.split(r'[.,]',raw)[-1])
        tolerance=Decimal('0.5')*Decimal(10)**-places*UNIT.get(match[2],1)
        value=next(iter(numbers(match[0])),None)
        if value is not None and not any(abs(item-value)<=tolerance for item in known):missing.append(match[0])
    return missing


SINGLE_INT=re.compile(r'\s*(-?\d+)(?:\.0+)?\s*')


def exact_from_output(answer,cell):
    """The printed number when the answer only got its scale wrong (3.276634 triệu for 3276634000), else empty."""
    match=SINGLE_INT.fullmatch(cell.text or '') if cell.status=='ok' else None
    if not match:return ''
    written=[re.sub(r'\D','',token[1]).rstrip('0') for token in NUMBER_TOKEN.finditer(DATE_TOKENS.sub(' ',answer.lower()))]
    return f'{int(match[1]):,}'.replace(',','.') if match[1].lstrip('-').rstrip('0') in written else ''


def last_error(cells):
    """First line of the newest failed cell, so a retry is told what went wrong."""
    return next((cell.text.strip().splitlines()[0][:200] for cell in reversed(cells) if cell.status!='ok' and cell.text.strip()),'')


def default_model():
    return os.getenv('AGENT_CODE_MODEL',DEFAULT_MODEL)


def warm_model(model):
    """Loading can take minutes on 8 GB RAM, far beyond chat()'s read timeout."""
    url=os.getenv('OLLAMA_BASE_URL','http://127.0.0.1:11435').rstrip('/')+'/api/chat'
    options=dict(num_ctx=6144,num_gpu=int(os.getenv('OLLAMA_NUM_GPU','99')))  # must equal chat()'s, or Ollama reloads
    requests.post(url,json=dict(model=model,messages=[],keep_alive='10m',options=options),timeout=(5,LOAD_TIMEOUT)).raise_for_status()


def history_payload(cells):
    history=[]
    for index,cell in enumerate(cells):
        limit=OBSERVED_CHARS if index>=len(cells)-2 else OLD_OBSERVED_CHARS
        history.append(dict(cell=index+1,code=clip(cell.code,1200),status=cell.status,output=clip(cell.text,limit)))
    return history


def save_notebook(result,output_dir=OUTPUT_DIR):
    cells=[v4.new_markdown_cell(f'# Câu hỏi\n\n{result.question}\n\nModel: `{result.model}`. Dữ liệu mô phỏng, kết nối SQLite chỉ đọc.')]
    executed=0
    for cell in result.cells:
        if cell.thought:cells.append(v4.new_markdown_cell(f'**Kế hoạch:** {cell.thought}'))
        if cell.status=='refused':
            refused=v4.new_output('stream',name='stderr',text=cell.text)
            cells.append(v4.new_code_cell(cell.code,outputs=[refused],metadata=dict(agent_status='refused')));continue
        executed+=1
        cells.append(v4.new_code_cell(cell.code,execution_count=executed,outputs=cell.outputs,metadata=dict(agent_status=cell.status,seconds=cell.seconds)))
    final=result.answer or result.error or '(Không có câu trả lời đã xác minh.)'
    rejected=f'\n\nCâu trả lời bị từ chối vì số không có trong output: {result.rejected_answer}' if result.rejected_answer else ''
    cells.append(v4.new_markdown_cell(f'# Trả lời ({result.status})\n\n{final}{rejected}\n\n{len(result.cells)} ô, {result.model_calls} lượt gọi model, {result.seconds} giây.'))
    notebook=v4.new_notebook(cells=cells,metadata=dict(language_info=dict(name='python'),kernelspec=dict(name='python3',display_name='Python 3',language='python')))
    nbformat.validate(notebook)
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    path=output_dir/f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.ipynb"
    nbformat.write(notebook,path);return path


def run_agent(question,*,ask=None,model=None,db_path=DB_PATH,max_cells=MAX_CELLS,cell_timeout=CELL_TIMEOUT,total_timeout=TOTAL_TIMEOUT,output_dir=OUTPUT_DIR):
    """Plan, run one cell, observe, repeat. `ask` replaces the model in tests."""
    started=time.monotonic();model=model or default_model();warm=ask is None
    system=SYSTEM.format(tables=table_summary(db_path))
    if ask is None:ask=lambda payload:chat(system,payload,STEP_SCHEMA,max_tokens=MAX_TOKENS,model=model)
    cells=[];calls=0;idle=0;note='';status='failed';answer='';rejected='';error=''
    if warm:
        try:warm_model(model);started=time.monotonic()
        except requests.RequestException as exc:error=f'Không nạp được model: {exc}'
    with SandboxKernel(db_path,output_dir) as kernel:
        while not error and calls<MAX_MODEL_CALLS and idle<MAX_IDLE_TURNS and time.monotonic()-started<total_timeout:
            calls+=1;idle+=1
            try:step=ask(dict(question=question,history=history_payload(cells),note=note,cells_left=max_cells-len(cells),attempt=calls))
            except requests.RequestException as exc:
                error=f'Lỗi gọi model: {exc}';break
            except (ValueError,KeyError,TypeError):
                note='Lượt trước không phải JSON hợp lệ hoặc code quá dài. Viết code ngắn hơn.';continue
            note='';code=str(step.get('code') or '').strip();thought=str(step.get('thought') or '')
            if code:
                if len(cells)>=max_cells:note='Hết số ô cho phép. Trả lời bằng kết quả đã có, code rỗng.';continue
                if cells and cells[-1].code==code:note=f'Ô này giống hệt ô trước. Hãy sửa code hoặc trả lời. {last_error(cells)}'.strip();continue
                issues=check_code(code)
                if issues:cell=Cell(code=code,status='refused',text='Từ chối, chưa chạy: '+' '.join(issues))
                else:cell=kernel.run(code,timeout=cell_timeout)
                cell.thought=thought;cells.append(cell);idle=0;continue
            candidate=str(step.get('answer') or '').strip()
            successful='\n'.join(cell.text for cell in cells if cell.status=='ok')
            if not step.get('done') or not candidate:note='Thiếu code hoặc câu trả lời. Viết một ô code, hoặc done=true kèm answer.';continue
            if not successful:note=f'Chưa có ô nào chạy thành công. Hãy viết code lấy số từ dữ liệu. {last_error(cells)}'.strip();continue
            unsupported=unsupported_numbers(candidate,f'{question}\n{successful}')
            exact=exact_from_output(candidate,cells[-1]) if unsupported else ''
            if exact:
                status='answered';answer=exact;break
            if unsupported:
                rejected=candidate
                note=f"Câu trả lời có số không thấy trong output: {', '.join(unsupported[:6])}. Hãy print đúng các số đó bằng code hoặc sửa câu trả lời.";continue
            status='answered';answer=candidate;rejected='';break
    if status!='answered' and rejected:status='unverified'
    result=RunResult(question=question,status=status,answer=answer,model=model,cells=cells,model_calls=calls,seconds=round(time.monotonic()-started,1),rejected_answer=rejected,error=error)
    result.notebook=str(save_notebook(result,output_dir));return result
