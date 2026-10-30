from pathlib import Path
import hashlib,json,zipfile
from remote_zip import Remote, URL
root=Path(__file__).resolve().parents[1]/'runtime'/'ollama'
root.mkdir(parents=True,exist_ok=True)
manifest=[]
with zipfile.ZipFile(Remote()) as z:
 for info in z.infolist():
  if info.is_dir() or '/cuda_' in info.filename: continue
  target=(root/info.filename).resolve()
  if not target.is_relative_to(root.resolve()): raise ValueError('Invalid path')
  target.parent.mkdir(parents=True,exist_ok=True)
  data=z.read(info)
  target.write_bytes(data)
  manifest.append({'path':info.filename,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
  print(info.filename,flush=True)
(root/'download-manifest.json').write_text(json.dumps({'source':URL,'files':manifest},indent=2))
