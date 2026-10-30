"""Fetch a pinned Vietnamese model locally; never execute repository code."""
import hashlib
import json
import os
from pathlib import Path
import requests
import time

ROOT=Path(__file__).resolve().parents[1]
PINNED_REVISION='4ab46e46ba5902328ba0742e489e75f787932f2b'


def main():
    os.environ['HF_HUB_DISABLE_XET']='1'
    from huggingface_hub import HfApi,snapshot_download
    model='dangvantuan/vietnamese-embedding'
    info=HfApi().model_info(model,revision=PINNED_REVISION,files_metadata=True)
    revision=info.sha
    weight_info=next(f for f in info.siblings if f.rfilename=='model.safetensors')
    expected_sha=weight_info.lfs.sha256
    expected=weight_info.size
    folder=ROOT/'models/vietnamese-embedding'
    folder.mkdir(parents=True,exist_ok=True)
    snapshot_download(model,revision=revision,local_dir=folder,max_workers=3,
        allow_patterns=['config.json','tokenizer*','special_tokens_map.json',
                        'vocab*','bpe.codes','added_tokens.json','sentence_bert_config.json','modules.json','1_Pooling/*','README.md'])
    # A single HTTPS stream also works on networks where concurrent CDN range requests stall.
    weights=folder/'model.safetensors'
    if not weights.exists():
        partial=folder/'model.safetensors.download'
        for attempt in range(5):
            received=partial.stat().st_size if partial.exists() else 0
            if received==expected: break
            try:
                with requests.get(f'https://huggingface.co/{model}/resolve/{revision}/model.safetensors',headers={'Range':f'bytes={received}-'},stream=True,timeout=(15,90)) as response:
                    response.raise_for_status()
                    if received and response.status_code!=206: raise ValueError('Server did not honor resume range')
                    with partial.open('ab' if received else 'wb') as stream:
                        for block in response.iter_content(1024*1024):
                            stream.write(block);received+=len(block)
                            if received//(50*1024*1024)!=(received-len(block))//(50*1024*1024): print(f'Vietnamese model: {received}/{expected} bytes',flush=True)
            except requests.RequestException:
                if attempt==4: raise
                time.sleep(2)
        if partial.stat().st_size!=expected: raise ValueError('Incomplete model download')
        with partial.open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()!=expected_sha: raise ValueError('Model SHA256 mismatch')
        partial.replace(weights)
    files={}
    for path in folder.rglob('*'):
        if path.is_file() and '.cache' not in path.parts and path.name!='source-manifest.json':
            with path.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
            if path.name=='model.safetensors' and digest!=expected_sha: raise ValueError('Installed model SHA256 mismatch')
            files[str(path.relative_to(folder))]={'bytes':path.stat().st_size,'sha256':digest}
    manifest={'model':model,'revision':revision,'license':'apache-2.0','local_only_inference':True,
              'word_segmentation':'pyvi.ViTokenizer.tokenize','pooling':'masked mean pooling, L2 normalized',
              'files':files}
    (folder/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'model':model,'revision':revision,'files':len(files),'bytes':sum(f['bytes'] for f in files.values())}),flush=True)


if __name__=='__main__': main()
