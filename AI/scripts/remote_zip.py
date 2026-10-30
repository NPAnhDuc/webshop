import io, json, requests, zipfile
URL='https://github.com/ollama/ollama/releases/download/v0.40.5/ollama-windows-amd64.zip'
class Remote(io.RawIOBase):
 def __init__(self):
  r=requests.get(URL,headers={'Range':'bytes=0-0'},timeout=60)
  r.raise_for_status()
  if r.status_code!=206: raise ValueError('Range not supported')
  self.url=r.url; self.size=int(r.headers['Content-Range'].split('/')[-1]); self.pos=0
 def seek(self,offset,whence=0):
  self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
  return self.pos
 def tell(self): return self.pos
 def read(self,size=-1):
  if size<0: size=self.size-self.pos
  if not size:return b''
  r=requests.get(self.url,headers={'Range':f'bytes={self.pos}-{self.pos+size-1}'},timeout=120)
  r.raise_for_status()
  if r.status_code!=206:raise ValueError('Range not honored')
  self.pos+=len(r.content);return r.content
if __name__=='__main__':
 with zipfile.ZipFile(Remote()) as z:
  entries=[{'name':i.filename,'size':i.file_size,'compressed':i.compress_size} for i in z.infolist()]
  print(json.dumps(entries,indent=2))
