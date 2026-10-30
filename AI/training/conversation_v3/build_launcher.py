"""Package synthetic conversation files into a portable Colab code cell."""
from pathlib import Path
import base64
import html
import json
import zlib

ROOT=Path(__file__).resolve().parent
files={p.relative_to(ROOT).as_posix():p.read_text(encoding='utf-8') for p in (ROOT/'data').glob('*') if p.suffix in ('.json','.jsonl')}
files['train_colab.py']=(ROOT/'train_colab.py').read_text(encoding='utf-8')
payload=base64.b64encode(zlib.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
source="""# ShopBot v3: Vietnamese contextual conversation training (synthetic, no secrets)
import base64,json,zlib,sys,subprocess,os,runpy
from pathlib import Path
ROOT=Path('/content/shopbot_conversation_v3');ROOT.mkdir(exist_ok=True)
FILES=json.loads(zlib.decompress(base64.b64decode(PAYLOAD)))
for name,body in FILES.items():
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body,encoding='utf-8')
subprocess.run([sys.executable,'-m','pip','-q','install','pyvi','safetensors','transformers','requests'],check=True)
runpy.run_path(str(ROOT/'train_colab.py'),run_name='__main__')
""".replace('PAYLOAD',repr(payload))
(ROOT/'colab_launcher.py').write_text(source,encoding='utf-8')
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'colab':{'name':'ShopBot_Conversation_V3.ipynb'},'accelerator':'GPU','kernelspec':{'name':'python3','display_name':'Python 3'}},'cells':[{'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':source.splitlines(keepends=True)}]}
(ROOT/'ShopBot_Conversation_V3.ipynb').write_text(json.dumps(nb,ensure_ascii=False),encoding='utf-8')
(ROOT.parent/'conversation-launcher.html').write_text('<meta charset="utf-8"><title>ShopBot V3 Colab launcher</title><h1>Vietnamese conversation training</h1><textarea style="width:95%;height:80vh" aria-label="Colab launcher">'+html.escape(source)+'</textarea>',encoding='utf-8')
print('Portable launcher ready',len(source))
