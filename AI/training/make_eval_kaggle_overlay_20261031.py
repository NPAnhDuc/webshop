"""Small overlay on shopbot-eval-bundle: changed code plus the policy documents and bank.

The 760 MB bundle stays as it is on Kaggle; only files that differ from its manifest go up.
"""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

AI=Path(__file__).resolve().parents[1]
BUNDLE=AI/'training/kaggle_upload/shopbot-eval-bundle.zip'
OUT=AI/'training/kaggle_upload/eval_overlay_ds'
MANAGED='data/unstructured/managed/e397df083984c120'
EXTRA=[f'{MANAGED}/manifest.json','data/business_sql/scenario_v1/documents/manifest.json',*[p.relative_to(AI).as_posix() for p in (AI/MANAGED).glob('policy-*.md')],
       *[p.relative_to(AI).as_posix() for p in (AI/'evaluation/policy_20261031').glob('*.json')],
       *[p.relative_to(AI).as_posix() for p in (AI/'evaluation/natural_20261031').glob('*.json')]]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


with zipfile.ZipFile(BUNDLE) as z:
    name=next(n for n in z.namelist() if n.endswith('BUNDLE_MANIFEST.json'))
    frozen=json.loads(z.read(name))['files']
code=[p.relative_to(AI).as_posix() for p in sorted((AI/'shopbot').glob('*.py'))]+[f for f in frozen if f.startswith('scripts/')]
changed=[f for f in code if frozen.get(f)!=sha(AI/f)]
files=sorted(set(changed+EXTRA+['scripts/run_policy_20261031.py','scripts/run_natural_20261031.py']))
if OUT.exists():shutil.rmtree(OUT)
root=OUT/'work';root.mkdir(parents=True)
for f in files:
    (root/f).parent.mkdir(parents=True,exist_ok=True);shutil.copy(AI/f,root/f)
(root/'OVERLAY_MANIFEST.json').write_text(json.dumps(dict(files={f:sha(AI/f) for f in files}),indent=1),encoding='utf8')
shutil.make_archive(str(OUT/'shopbot-eval-overlay'),'zip',root);shutil.rmtree(root)
(OUT/'dataset-metadata.json').write_text(json.dumps(dict(title='shopbot-eval-overlay',id='nguynphananhc/shopbot-eval-overlay',
    licenses=[dict(name='other')]),indent=1),encoding='utf8')
print(len(files));print('\n'.join(files))
