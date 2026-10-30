import json
import re
import sqlite3
from pathlib import Path

import nbformat
import pytest

from shopbot import notebook_agent as agent


@pytest.mark.parametrize('code',[
    '!dir','%ls','%%bash\nls','x=!whoami','df?',
    'import os','import subprocess','import socket','from os import system','import urllib.request','import requests','from . import x',
    'pd.compat.os.system("x")','np.ctypeslib','import numpy.ctypeslib','from pandas import compat',
    'open(".env").read()','eval("1")','exec("1")','__import__("os")','getattr(pd,"read_csv")','get_ipython().system("dir")',
    '().__class__.__base__','df._mgr',"'{0.__class__}'.format(1)",
    'pd.read_csv("http://x")','pd.read_pickle("x")','df.to_csv("x")','df.to_sql("t",conn)','np.load("x")','np.fromfile("x")',
    'sqlite3.connect("x")','from sqlite3 import connect','conn.executescript("x")','conn.enable_load_extension(True)',
    'df.query("a>1")','pd.eval("1")',
    'conn.execute("DELETE FROM orders")','conn.execute("update orders set id=1")','conn.execute("SELECT 1; DROP TABLE orders")',
    'conn.execute("ATTACH \'x\' AS y")','conn.execute("CREATE TEMP TABLE t(a)")',
])
def test_static_check_refuses(code):
    assert agent.check_code(code)


@pytest.mark.parametrize('code',[
    'import pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\nimport sqlite3',
    'df=pd.read_sql("SELECT month,SUM(net_revenue) s FROM monthly_pnl WHERE strftime(\'%Y\',month||\'-01\')=\'2026\' GROUP BY month",conn)\nprint(df)',
    'df=pd.read_sql_query("""\nSELECT REPLACE(month,\'-\',\'/\') FROM monthly_pnl\n""",conn)\nprint(df.to_string())',
    'print(f"{1234:,}")\nprint("Update: xong")',
    'df["m"]=pd.to_datetime(df["month"])\nprint(df["x"].pct_change().round(2).to_list())',
    'plt.plot([1,2]);plt.savefig("a.png")',
])
def test_static_check_allows_normal_analysis(code):
    assert agent.check_code(code)==[]


@pytest.mark.parametrize('answer,evidence',[
    ('Tổng doanh thu là 1.234.567 đồng','tong 1234567'),
    ('Tổng doanh thu là 1,234,567 đồng','1234567.0'),
    ('Tăng 12,34%','12.3412'),
    ('Giảm 5.2%','-5.2'),
    ('Khoảng 1,2 tỷ đồng','1234567890'),
    ('Trung bình 123.457 đồng','123456.78'),
    ('Tháng 3 năm 2026 và 2025-10 cao nhất, tháng 12/2025 thấp','không có số'),
    ('Lãi gộp tháng 2026-02 giảm 36.76% so với tháng 2026-01.','-36.76'),
])
def test_supported_numbers(answer,evidence):
    assert agent.unsupported_numbers(answer,evidence)==[]


@pytest.mark.parametrize('answer,evidence',[
    ('Tổng là 1.234.568 đồng','1234567'),
    ('Tăng 12,34%','12.40'),
    ('Tổng là 1,5 tỷ đồng','1234567890'),
    ('Có 5 tháng vượt','2 3'),
])
def test_unsupported_numbers(answer,evidence):
    assert agent.unsupported_numbers(answer,evidence)


@pytest.fixture(scope='module')
def kernel(tmp_path_factory):
    with agent.SandboxKernel(output_dir=tmp_path_factory.mktemp('sandbox')) as sandbox:yield sandbox


def test_kernel_reads_database_and_keeps_state(kernel):
    first=kernel.run('df=pd.read_sql("SELECT SUM(net_revenue) s FROM monthly_pnl",conn)\nprint(int(df.s[0]))')
    conn=sqlite3.connect(agent.DB_PATH.as_uri()+'?mode=ro',uri=True)
    assert first.status=='ok' and first.text.strip()==str(conn.execute('SELECT SUM(net_revenue) FROM monthly_pnl').fetchone()[0])
    assert kernel.run('print(len(df))').text.strip()=='1'


def test_kernel_reports_traceback(kernel):
    cell=kernel.run('print(no_such_name)')
    assert cell.status=='error' and 'NameError' in cell.text


def test_kernel_draws_figure(kernel):
    cell=kernel.run('plt.plot([1,2,3]);plt.show()')
    assert cell.status=='ok' and any('image/png' in item.get('data',{}) for item in cell.outputs)
    assert 'đã vẽ biểu đồ' in cell.text


# The cells below skip check_code on purpose: the kernel must hold on its own.
@pytest.mark.parametrize('code',[
    'import socket\nsocket.create_connection(("127.0.0.1",11435),1)',
    'import socket\nsocket.getaddrinfo("example.com",80)',
    'import urllib.request\nurllib.request.urlopen("http://127.0.0.1:11435/api/tags",timeout=1)',
    'import subprocess\nsubprocess.run(["cmd","/c","echo pwned"])',
    'import os\nos.system("echo pwned")',
    f'open({str(agent.ROOT/".env")!r}).read()',
    f'open({str(agent.ROOT/"sandbox_escape.txt")!r},"w").write("x")',
    f'import pandas\npandas.read_csv({str(agent.DB_PATH.parent/"csv/orders.csv")!r})',
    f'import sqlite3 as s\ns.connect({str(agent.DB_PATH)!r})',
    'import ctypes\nctypes.CDLL("kernel32")',
    'conn.execute("DELETE FROM orders")',
    'conn.execute("INSERT INTO suppliers VALUES (1,2,3)")',
    'conn.execute("CREATE TEMP TABLE t(a)")',
    "conn.execute(\"ATTACH 'x.db' AS other\")",
    "conn.execute(\"VACUUM INTO 'x.db'\")",
])
def test_kernel_blocks_bypass_of_static_check(kernel,code):
    cell=kernel.run(code)
    assert cell.status=='error' and re.search(r'sandbox chặn|not authorized|authorization denied|prohibited|readonly',cell.text),cell.text
    assert not (agent.ROOT/'sandbox_escape.txt').exists()


def test_kernel_environment_has_no_secrets(kernel,monkeypatch):
    assert 'env' not in kernel.__dict__
    names=kernel.run('import os\nprint(sorted(os.environ))').text
    assert 'OLLAMA' not in names and 'API_KEY' not in names and 'HF_TOKEN' not in names


def test_shell_magics_do_not_run_in_kernel(kernel):
    assert kernel.run('!echo pwned').status=='error'
    assert 'Volume' not in kernel.run('ls').text


def test_timeout_restarts_kernel_and_loses_state(tmp_path):
    with agent.SandboxKernel(output_dir=tmp_path) as sandbox:
        sandbox.run('x=1')
        cell=sandbox.run('while True:pass',timeout=2)
        assert cell.status=='timeout' and 'khởi động lại' in cell.text
        assert sandbox.run('print(x)').status=='error'
        assert sandbox.run('print(int(pd.read_sql("SELECT COUNT(*) c FROM products",conn).c[0]))').text.strip()=='67'


def scripted(steps):
    pending=iter(steps);seen=[]
    def ask(payload):
        seen.append(payload);step=next(pending)
        if isinstance(step,Exception):raise step
        return dict(thought='kế hoạch',code='',done=False,answer='')|step
    ask.seen=seen;return ask


def test_agent_recovers_from_refusal_and_error_then_saves_notebook(tmp_path):
    ask=scripted([
        dict(code='import os\nprint(os.getcwd())'),
        dict(code='print(undefined_value)'),
        dict(code='print(int(pd.read_sql("SELECT COUNT(*) c FROM products",conn).c[0]))'),
        dict(done=True,answer='Shop có 67 sản phẩm.'),
    ])
    result=agent.run_agent('Có bao nhiêu sản phẩm?',ask=ask,output_dir=tmp_path)
    assert result.status=='answered' and result.answer=='Shop có 67 sản phẩm.'
    assert [cell.status for cell in result.cells]==['refused','error','ok']
    assert 'Từ chối' in ask.seen[1]['history'][0]['output'] and 'NameError' in ask.seen[2]['history'][1]['output']
    notebook=nbformat.read(Path(result.notebook),as_version=4);nbformat.validate(notebook)
    text=json.dumps(notebook,ensure_ascii=False)
    assert 'Có bao nhiêu sản phẩm?' in text and 'Shop có 67 sản phẩm.' in text and 'NameError' in text and 'Từ chối' in text
    assert [cell.get('metadata',{}).get('agent_status') for cell in notebook.cells if cell.cell_type=='code']==['refused','error','ok']


def test_agent_rejects_answer_with_invented_number(tmp_path):
    ask=scripted([dict(code='print(67)'),dict(done=True,answer='Có 68 sản phẩm.'),dict(done=True,answer='Có 69 sản phẩm.')]+[dict(done=True,answer='Có 70 sản phẩm.')]*10)
    result=agent.run_agent('Có bao nhiêu sản phẩm?',ask=ask,output_dir=tmp_path)
    assert result.status=='unverified' and result.answer=='' and '70' in result.rejected_answer
    assert 'không thấy trong output' in ask.seen[2]['note']


def test_agent_requires_executed_cell_before_answering(tmp_path):
    ask=scripted([dict(done=True,answer='Không có số nào.')]+[dict()]*11)
    result=agent.run_agent('Có bao nhiêu?',ask=ask,output_dir=tmp_path)
    assert result.status=='failed' and result.answer==''
    assert 'Chưa có ô nào' in ask.seen[1]['note']


def test_agent_stops_at_cell_limit(tmp_path):
    ask=scripted([dict(code=f'print({n})') for n in range(12)])
    result=agent.run_agent('x',ask=ask,output_dir=tmp_path,max_cells=3)
    assert len(result.cells)==3 and result.status=='failed'
    assert 'Hết số ô' in ask.seen[-1]['note']


def test_agent_survives_invalid_model_json(tmp_path):
    ask=scripted([ValueError('bad json'),dict(code='print(1)'),dict(done=True,answer='Kết quả là 1.')])
    assert agent.run_agent('x',ask=ask,output_dir=tmp_path).status=='answered'


def test_agent_reports_model_outage_instead_of_crashing(tmp_path):
    ask=scripted([agent.requests.ConnectionError('ollama down')])
    result=agent.run_agent('x',ask=ask,output_dir=tmp_path)
    assert result.status=='failed' and 'ollama down' in result.error and Path(result.notebook).exists()
