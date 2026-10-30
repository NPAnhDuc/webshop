"""Self-contained Colab notebook for v2. No real transactions or secrets uploaded."""
import base64
import json
from pathlib import Path
import zlib

HERE=Path(__file__).resolve().parent


def build():
    folder=HERE/'v2'
    files={str(p.relative_to(folder)).replace('\\','/'):p.read_text(encoding='utf-8') for p in (folder/'data').iterdir() if p.is_file()}
    files['retriever_train.py']=(HERE/'retriever_train.py').read_text(encoding='utf-8').replace('max_length=384','max_length=512')
    files['forecast_train.py']=(HERE/'forecast_train.py').read_text(encoding='utf-8')
    payload=base64.b64encode(zlib.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):
        compile(text,'colab-v2','exec')
        cells.append({'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':text.splitlines(True)})
    md('''# ShopBot v2 — 67 sản phẩm và shop mô phỏng một năm

Hai loại dữ liệu dùng chung chatbot, không dùng chung một loss huấn luyện.
1. Embedding: E5 multilingual small, chạy GPU, so baseline với candidate.
2. Dữ liệu số: không train thuộc số. Huấn luyện riêng dự báo nhu cầu một ngày,
   so naive cùng thứ tuần trước với gradient boosting; chọn bằng validation.
3. Kev: định tuyến public, dùng notebook Kev riêng sau khi duyệt tập nhãn v2.
   Quyền admin luôn kiểm tra ở mã ứng dụng, không do Kev quyết định.

Không upload `.env`, khách hàng thật, giao dịch thật, báo cáo bản quyền đầy đủ,
đáp án sự kiện cài sẵn hoặc nhu cầu ẩn. Chỉ có thông số công khai và dữ liệu tổng hợp giả lập.
''')
    code(f'''import base64,json,zlib,sys,subprocess
from pathlib import Path
ROOT=Path('/content/shopbot_tutor_v2');ROOT.mkdir(parents=True,exist_ok=True)
FILES=json.loads(zlib.decompress(base64.b64decode('{payload}')))
for name,text in FILES.items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')
print(json.dumps(json.loads((ROOT/'data/manifest.json').read_text()),ensure_ascii=False,indent=2))
''')
    code('''import torch
assert torch.cuda.is_available(),'Chọn runtime GPU trước khi train retriever.'
print('GPU:',torch.cuda.get_device_name(0))
subprocess.run([sys.executable,'-m','pip','install','-q','transformers>=4.51,<6','huggingface-hub>=0.30','sentencepiece','scikit-learn','pandas'],check=True)
def run_live(command):
    with subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1) as process:
        for line in process.stdout: print(line,end='',flush=True)
        if process.wait(): raise RuntimeError('Training process failed; inspect output above.')
''')
    md('''## Retriever

Tập v1 giữ nguyên group/split; v2 thêm nguồn và kế hoạch. Câu hỏi khuôn mẫu chỉ là pilot.
Chỉ dùng mẫu supported để train; chỉ chọn trọng số mới nếu validation recall@1 tăng.
Kết quả này chưa đo ACL, thời gian hiệu lực, multi-hop hay chất lượng câu trả lời tự do.
''')
    code("run_live([sys.executable,str(ROOT/'retriever_train.py'),'--root',str(ROOT),'--epochs','3'])\n")
    md('''## Dự báo riêng

Tám tháng train, hai tháng validation, hai tháng test. Dùng lags quá khứ; test walk-forward
một ngày với dữ liệu ngày trước được quan sát. Không phải dự báo cố định trước 60 ngày.
Không khẳng định deep learning tốt hơn: một năm giả lập không đủ chứng minh điều đó.
''')
    code("run_live([sys.executable,str(ROOT/'forecast_train.py'),'--root',str(ROOT)])\n")
    md('## Lưu checkpoint và báo cáo, chưa thay model production')
    code('''import shutil
from google.colab import files
archive=shutil.make_archive('/content/shopbot_v2_outputs','zip',ROOT/'outputs')
print('Artifact:',archive)
files.download(archive)
''')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'ShopBot_v2_Colab.ipynb'},'accelerator':'GPU',
              'kernelspec':{'name':'python3','display_name':'Python 3'},'language_info':{'name':'python'}},'cells':cells}
    for index,cell in enumerate(cells):cell['id']=f'v2-{index}'
    (folder/'ShopBot_v2_Colab.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
    # A separate source for UI paste; stop before automatic download so outputs can be inspected.
    run_all='\n\n'.join(''.join(c['source']) for c in cells[:-1] if c['cell_type']=='code')
    (folder/'colab_run_all.py').write_text(run_all,encoding='utf-8')
    import html
    (folder/'launcher.html').write_text('<meta charset="utf-8"><h1>ShopBot v2 Colab source</h1><textarea style="width:100%;height:85vh">'+html.escape(run_all)+'</textarea>',encoding='utf-8')
    print(json.dumps({'notebook':str(folder/'ShopBot_v2_Colab.ipynb'),'ui_source_chars':len(run_all)}))


if __name__=='__main__': build()
