"""Make a self-contained Colab notebook; contains only the reviewed public pilot."""
import base64
import json
import zlib
from pathlib import Path

HERE=Path(__file__).resolve().parent

def build():
    files={p.relative_to(HERE).as_posix():p.read_text(encoding='utf-8') for p in (HERE/'data').glob('*.json*')}
    files['retriever_train.py']=(HERE/'retriever_train.py').read_text(encoding='utf-8')
    payload=base64.b64encode(zlib.compress(json.dumps(files,ensure_ascii=False).encode(),9)).decode()
    cells=[]
    def md(text):cells.append({'cell_type':'markdown','metadata':{},'source':text.splitlines(True)})
    def code(text):cells.append({'cell_type':'code','metadata':{},'source':text.splitlines(True),'execution_count':None,'outputs':[]})
    md('''# ShopBot - Gia sư RAG và fine-tune Kev trên Colab

Bộ thử nghiệm từ 37 sản phẩm công khai. Huấn luyện encoder truy xuất bằng cặp câu hỏi–nguồn, rồi fine-tune bộ định tuyến Kev 0.8B. Không train lại Qwen sinh văn bản và không coi giá/tồn kho chưa biết là sự thật.

Chọn **Runtime → Change runtime type → T4 GPU** trước khi chạy. Notebook dùng phiên GPU tương tác, không dựng web server. Kết quả có thể không tốt hơn bản gốc; không tự triển khai model.

Vòng gia sư: hỏi → tìm nguồn → chấm đúng nguồn → ghi lỗi validation kèm dẫn chứng → người hướng dẫn duyệt sửa → chạy phiên mới. Test được giữ riêng. Câu sai không tự biến thành kiến thức mới.
''')
    code(f'''import base64, json, zlib, sys, subprocess, os
from pathlib import Path
ROOT=Path('/content/shopbot_tutor')
ROOT.mkdir(parents=True,exist_ok=True)
FILES=json.loads(zlib.decompress(base64.b64decode('{payload}')))
for name,text in FILES.items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT.resolve())
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(text,encoding='utf-8')
print(json.dumps(json.loads((ROOT/'data/manifest.json').read_text()),ensure_ascii=False,indent=2))
''')
    md('## 1. Kiểm tra GPU và cài thư viện encoder')
    code('''import torch
print('Python:',sys.version)
print('Torch:',torch.__version__)
assert torch.cuda.is_available(), 'Chưa có GPU: đổi runtime sang GPU rồi chạy lại.'
print('GPU:',torch.cuda.get_device_name(0))
subprocess.run([sys.executable,'-m','pip','install','-q','transformers>=4.51,<6','huggingface-hub>=0.30','sentencepiece'],check=True)
''')
    md('''## 2. Huấn luyện retriever và ghi bài cần kèm lại

Encoder: `intfloat/multilingual-e5-small`, chốt revision khi tải. So recall@1/3 trước và sau; chỉ chọn trọng số mới khi validation tăng. Luôn giữ `last-trained` để kiểm tra. Các câu giá/tồn kho thiếu dữ liệu được gắn `must_abstain`, không đưa vào loss truy xuất.
''')
    code('''subprocess.run([sys.executable,str(ROOT/'retriever_train.py'),'--root',str(ROOT),'--epochs','3'],check=True)
summary=json.loads((ROOT/'outputs/retriever/training-summary.json').read_text())
print(json.dumps(summary,ensure_ascii=False,indent=2))
queue=json.loads((ROOT/'outputs/retriever/tutor-review-queue.json').read_text())
print('Bài cần gia sư duyệt:',len(queue))
print(json.dumps(queue[:2],ensure_ascii=False,indent=2))
''')
    md('''## 3. Fine-tune Kev 0.8B từ checkpoint đã phát hành

Schema nhãn đặt trong từng `questions.intent.label`. Tập này có 73 nhóm ý nghĩa, chưa đủ để khẳng định chất lượng triển khai. Môi trường Kev riêng để đáp ứng Python/dependency của repo đã chốt. GPU T4 dùng fp32 vì trainer phiên bản này không hỗ trợ fp16. Chỉ GPU hỗ trợ bf16 mới dùng bf16.
''')
    code('''RUN_KEV=True
if RUN_KEV:
    subprocess.run([sys.executable,'-m','pip','install','-q','uv'],check=True)
    repo=ROOT/'kev'
    if not (repo/'.git').exists():
        subprocess.run(['git','clone','https://github.com/jaredpalmer/kev.git',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'checkout','1f04cfa28e6a708485b28a9585010b9e436b776e'],check=True)
    venv=ROOT/'kev-venv'
    subprocess.run(['uv','venv','--python','3.12','--system-site-packages',str(venv)],check=True)
    PY=str(venv/'bin/python')
    subprocess.run(['uv','pip','install','--python',PY,'-e',str(repo)],check=True)
    from huggingface_hub import snapshot_download
    kev_checkpoint=snapshot_download('jaredpalmer/kev-0.8b',revision='bf75a6a8848ea6960ff2ed108d9ed44c2941174f')
    DTYPE='bf16' if torch.cuda.is_bf16_supported() else 'fp32'
    OUT=ROOT/'outputs/kev'
    OUT.mkdir(parents=True,exist_ok=True)
    subprocess.run([PY,'-m','kev.benchmark','--run',kev_checkpoint,'--data',str(ROOT/'data/kev-validation.jsonl'),'--device','cuda','--out',str(OUT/'baseline-validation')],cwd=repo,check=True)
    command=[PY,'-m','kev.train','--data',str(ROOT/'data/kev-train.jsonl'),
      '--base','Qwen/Qwen3.5-0.8B-Base','--base_revision','dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68',
      '--init_from',kev_checkpoint,'--epochs','2','--lr','2e-5','--batch','1','--accum','8',
      '--dtype',DTYPE,'--checkpointing','1','--device','cuda','--out',str(OUT/'trained')]
    print(' '.join(command))
    subprocess.run(command,cwd=repo,check=True)
    for split in ['validation','test']:
        subprocess.run([PY,'-m','kev.benchmark','--run',str(OUT/'trained'),'--data',str(ROOT/f'data/kev-{split}.jsonl'),'--device','cuda','--out',str(OUT/f'trained-{split}')],cwd=repo,check=True)
    subprocess.run([PY,'-m','kev.benchmark','--run',kev_checkpoint,'--data',str(ROOT/'data/kev-test.jsonl'),'--device','cuda','--out',str(OUT/'baseline-test')],cwd=repo,check=True)
    print('Đã lưu trọng số Kev và báo cáo; chưa đổi endpoint đang dùng.')
''')
    md('''## 4. Lưu kết quả về máy

Phiên Colab có thể bị ngắt. Tải artifact sau khi train xong. Nếu lỗi giữa chừng, có thể chạy cell này để giữ các phần đã hoàn thành. LoRA Kev ở phiên bản này chỉ lưu cuối lượt train; không hứa resume giữa optimizer step.
''')
    code('''import shutil
from google.colab import files
archive=shutil.make_archive('/content/shopbot_tutor_outputs','zip',ROOT/'outputs')
print('Artifact:',archive)
files.download(archive)
''')
    notebook={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'ShopBot_Tutor_Colab.ipynb'},'kernelspec':{'display_name':'Python 3','name':'python3'},'language_info':{'name':'python'},'accelerator':'GPU'},'cells':cells}
    for index,cell in enumerate(cells):cell['id']=f'shopbot-{index:02d}'
    path=HERE/'ShopBot_Tutor_Colab.ipynb'
    path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1),encoding='utf-8')
    # Syntax-check every Python cell locally without executing GPU commands.
    for cell in cells:
        if cell['cell_type']=='code':compile(''.join(cell['source']),str(path),'exec')
    print(path,path.stat().st_size)

if __name__=='__main__':build()
