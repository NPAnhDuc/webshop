"""Report source integrity after data-only publication; no automatic PASS scoring."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'data/unstructured/technology_20261020'
RUN=ROOT/'evaluation/user_bank_20261020/technology_run_v2'


def main():
    receipt=json.loads((PACK/'publication.json').read_text(encoding='utf8'))
    rows=json.loads((RUN/'results.json').read_text(encoding='utf8'))
    assert len(rows)==50,'Wait for all 50 cases before reporting'
    integrity=json.loads((RUN/'integrity.json').read_text(encoding='utf8'))
    assert integrity['unchanged'],'Knowledge or database changed during evaluation'
    errors=[];quotes=0;new_sources=set();versions=set();actions=Counter()
    answer_lines=['# 50 câu sau khi nạp dữ liệu công nghệ',
                  'Đáp án nguyên văn. Chưa chấm lại mức độ đáp ứng của toàn bộ 50 câu; không coi dẫn đúng nguồn là trả lời đúng.']
    for row in rows:
        result=row['result'];actions[result.get('basic_action','ERROR')]+=1
        sources={s['chunk_id']:s for s in result.get('sources',[])}
        for source in sources.values():
            identifier=source.get('document_id','')
            if identifier.startswith('tech-'):new_sources.add(identifier)
            if identifier.startswith('catalog-'):versions.add(source.get('version'))
            if row['case']['role']=='customer' and source.get('audience')=='admin':
                errors.append(dict(id=row['case']['id'],error='private source leak'))
        for claim in result.get('rag',{}).get('claims',[]):
            for evidence in claim.get('evidence',[]):
                for quote in evidence.get('quotes',[]):
                    quotes+=1
                    if evidence.get('chunk_id') not in sources or quote not in sources[evidence['chunk_id']]['text']:
                        errors.append(dict(id=row['case']['id'],error='quote absent from supplied source'))
        if not result:errors.append(dict(id=row['case']['id'],error='empty result / exception'))
        answer_lines += [f"\n## {row['case']['id']}. {row['case']['question']}",
                         f"Vai trò: {row['case']['role']}. Thời gian: {row['seconds']} giây.",
                         result.get('answer','ERROR'),
                         'Cảnh báo tự động (chưa phải kết luận chấm): '+str(row['automated_issues'])]
    (RUN/'ANSWERS.md').write_text('\n\n'.join(answer_lines)+'\n',encoding='utf8')
    summary=dict(cases=50,claims_quotes_checked=quotes,evidence_integrity_errors=errors,
                 technical_source_ids_retrieved=sorted(new_sources),catalog_versions_retrieved=sorted(versions),
                 actions=dict(actions),seconds=sum(r['seconds'] for r in rows),
                 frozen_corpus_integrity=integrity['unchanged'],acceptance_score='not automatically scored',
                 receipt_manifest_matches=hashlib.sha256(Path(receipt['manifest']).read_bytes()).hexdigest()==receipt['after_manifest_sha256'])
    (RUN/'publication_checks.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    assert not errors,errors
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
