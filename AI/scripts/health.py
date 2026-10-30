"""Inspect local model services without reading or printing secrets."""
import json
import requests
import time
from pathlib import Path

checks={}
for name,url in [('streamlit','http://127.0.0.1:8501/_stcore/health'),('ollama','http://127.0.0.1:11435/api/tags'),('vietnamese','http://127.0.0.1:8011/health'),('kev_optional','http://127.0.0.1:8009/v1/models')]:
 try:
  r=requests.get(url,timeout=3)
  checks[name]={'status':r.status_code}
  if name=='ollama':checks[name]['models']=[v['name'] for v in r.json().get('models',[])]
  if name=='vietnamese':checks[name].update(r.json())
 except requests.RequestException:checks[name]={'status':'not ready'}
heartbeat=Path(__file__).resolve().parents[1]/'runtime/monthly/worker-status.json'
if heartbeat.exists():
 data=json.loads(heartbeat.read_text(encoding='utf-8'))
 checks['monthly_worker']={'status':'active' if 0<=time.time()-data['checked_at']<180 else 'stale',
                           'last_results':data.get('results',[])}
else:checks['monthly_worker']={'status':'not started'}
print(json.dumps(checks,ensure_ascii=False,indent=2))
