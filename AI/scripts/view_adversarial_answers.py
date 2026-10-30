"""Compact read-only view for manual rubric review; never a judge."""
import json,re,sys
from pathlib import Path
root=Path(sys.argv[3]) if len(sys.argv)>3 else Path(__file__).resolve().parents[1]/'evaluation/adversarial_100_20261020'
bank={c['id']:c for c in json.loads((root/'bank.json').read_text(encoding='utf8'))}
rows=json.loads((root/'results.json').read_text(encoding='utf8'))
start=int(sys.argv[1]);end=int(sys.argv[2])
for i,row in enumerate(rows,1):
    if not start<=i<=end:continue
    r=row['result'];c=bank[row['id']]
    text=re.sub(r'\[Nguồn:.*?\]','',r.get('answer','ERROR'),flags=re.S)
    text=text.replace('Nguồn thuộc shop mô phỏng, chưa phải chính sách hoặc số liệu shop thật.','')
    text=re.sub(r'\n\s*\n','\n',text).strip()
    print(row['id'],row['question'],'\nEXPECT:',c['rubric'],'\nANSWER:',text,
          '\nACTION:',r.get('basic_action'),'STATUS:',r.get('rag',{}).get('answerability'),
          '\nSOURCES:',','.join(sorted({s.get('document_id','?') for s in r.get('sources',[])})),'\n',flush=True)
print('Total completed:',len(rows))
