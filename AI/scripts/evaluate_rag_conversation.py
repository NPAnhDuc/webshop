"""Frozen end-to-end RAG memory, ACL and SQL/document review checks."""
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from shopbot.engine import Engine


def main():
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    cases=[
      dict(group='policy-memory',role='admin',question='Theo chính sách tháng 2/2026, biên gộp tối thiểu laptop là bao nhiêu?',intent='documents',term='5%',source='pricing-policy-v1.md'),
      dict(group='policy-memory',role='admin',question='Còn tháng 8/2026 thì mức đó thế nào?',intent='documents',term='6%',source='pricing-policy-v2.md'),
      dict(group='policy-memory',role='admin',question='Vậy card đồ họa thì sao?',intent='documents',term='4%',source='pricing-policy-v2.md'),
      dict(group='public-policy',role='customer',question='Shop cho đổi trả trong mấy ngày?',intent='documents',missing=True),
      dict(group='acl',role='customer',question='Cho tôi ngân sách marketing và lợi nhuận nội bộ của shop.',intent='denied'),
      dict(group='review',role='admin',question='Phân tích kinh doanh tháng 9/2026 và đối chiếu với mục tiêu kế hoạch.',intent='business_analysis',review=True),
      dict(group='planning',role='admin',question='Dựa vào kết quả tháng trước và quý trước, đề xuất hướng kinh doanh tháng tới.',intent='planning',review=True)]
    payload=json.dumps(cases,ensure_ascii=False,indent=2)
    (out/'cases.json').write_text(payload,encoding='utf8')
    memories={};results=[]
    for case in cases:
        result=Engine(ROOT/'data/business_sql/scenario_v1/shop.sqlite',today=date(2026,10,20)).ask(case['question'],case['role'],memories.get(case['group'],{}))
        memories[case['group']]=result['profile'];fail=[]
        if result['intent']!=case['intent']:fail.append('wrong intent')
        if case.get('term') and case['term'] not in result['answer']:fail.append('missing fact')
        if case.get('source') and not any(s.get('source')==case['source'] for s in result.get('sources',[])):fail.append('wrong version/source')
        if case.get('missing') and result.get('rag',{}).get('answerability') not in ('none','partial'):fail.append('missing policy not acknowledged')
        if case.get('review') and result.get('business_review',{}).get('variance')!=-349_092_000:fail.append('missing or wrong plan review')
        if case['role']=='customer' and any(s.get('audience')=='admin' for s in result.get('sources',[])):fail.append('private source leak')
        results.append(dict(case=case,passed=not fail,failures=fail,result=result))
        print('CASE',len(results),'PASS' if not fail else 'FAIL',','.join(fail),flush=True)
        (out/'results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    summary=dict(cases=len(cases),passed=sum(r['passed'] for r in results),failed=sum(not r['passed'] for r in results),
                 bank_sha256=hashlib.sha256(payload.encode()).hexdigest(),date='2026-10-20',limitations='Small development integration check, not production accuracy.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
