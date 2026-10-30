"""Role filtering is upstream; cache vectors by exact text and model revision.

Changing a document or worker model invalidates its vector. Disk cache contains
hashed keys/vectors only, never plaintext, rankings, answers or role permissions.
"""
from array import array
from collections import OrderedDict
import hashlib,math,os,sqlite3,threading
from urllib.parse import urlparse
import requests
from .store import ROOT

_cache=OrderedDict();_lock=threading.Lock()


def _disk():
    path=ROOT/'runtime/embedding-cache/vectors.sqlite'
    path.parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path,timeout=2)
    con.execute('CREATE TABLE IF NOT EXISTS vectors(signature TEXT,hash TEXT,vector BLOB,truncated INTEGER,PRIMARY KEY(signature,hash))')
    return con


def _vectors(texts,signature,endpoint):
    keys=[hashlib.sha256(text.encode('utf8')).hexdigest() for text in texts]
    found={}
    with _lock:
        for key in keys:
            if (signature,key) in _cache:found[key]=_cache[(signature,key)]
    con=None
    try:
        con=_disk()
        for key in set(keys)-found.keys():
            row=con.execute('SELECT vector,truncated FROM vectors WHERE signature=? AND hash=?',(signature,key)).fetchone()
            if row:
                vec=array('f');vec.frombytes(row[0]);found[key]=(vec,bool(row[1]))
    except (OSError,sqlite3.Error,ValueError):
        if con:con.close()
        con=None
    missing=list(dict.fromkeys(key for key in keys if key not in found));lookup=dict(zip(keys,texts))
    try:
        for start in range(0,len(missing),64):
            batch=missing[start:start+64]
            response=requests.post(endpoint+'/embed',json={'texts':[lookup[k] for k in batch]},timeout=(3,90));response.raise_for_status()
            payload=response.json()
            if len(payload['embeddings'])!=len(batch) or len(payload['truncated'])!=len(batch):raise ValueError('Invalid embedding count')
            for key,vector,truncated in zip(batch,payload['embeddings'],payload['truncated']):
                if not vector or not all(math.isfinite(x) for x in vector):raise ValueError('Invalid embedding vector')
                item=(array('f',vector),bool(truncated));found[key]=item
                if con:
                    try:con.execute('INSERT OR REPLACE INTO vectors VALUES (?,?,?,?)',(signature,key,item[0].tobytes(),int(item[1])))
                    except sqlite3.Error:pass
        if con:
            try:
                con.execute('DELETE FROM vectors WHERE rowid NOT IN (SELECT rowid FROM vectors ORDER BY rowid DESC LIMIT 8000)');con.commit()
            except sqlite3.Error:pass
    finally:
        if con:con.close()
    with _lock:
        for key,item in found.items():
            _cache[(signature,key)]=item;_cache.move_to_end((signature,key))
        while len(_cache)>4096:_cache.popitem(last=False)
    return [found[k] for k in keys]


def dense_scores(question,chunks):
    endpoint=os.getenv('VI_EMBEDDING_URL','').rstrip('/')
    if not endpoint:return None
    if urlparse(endpoint).hostname not in ('127.0.0.1','localhost','::1'):raise ValueError('Embedding worker must be local')
    response=requests.get(endpoint+'/health',timeout=(2,5));response.raise_for_status()
    info=response.json();signature=info['model']+':'+info['revision']
    encoded=_vectors([c.get('retrieval_text',c['text']) for c in chunks]+[question],signature,endpoint)
    query=encoded[-1][0];vectors=encoded[:-1]
    if any(len(v)!=len(query) for v,_ in vectors):raise ValueError('Invalid embedding dimension')
    return [sum(a*b for a,b in zip(query,v)) for v,_ in vectors],signature,[trunc for _,trunc in vectors]
