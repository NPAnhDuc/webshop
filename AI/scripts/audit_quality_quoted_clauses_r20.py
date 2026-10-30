"""Offline development-only audit; no model, retrieval service or production edit."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shopbot.grounded_rag import question_parts
from shopbot.retrieval import normalize

BASE = ROOT / 'evaluation/quality_loop_20261021'
OUT = ROOT / 'evaluation/quoted_clauses_20261023_r20_v2'
QUOTES = re.compile(r'“[^”\n]+”|"[^"\n]+"|«[^»\n]+»')
OLD = "    parts=[p.strip(' ,;?') for p in re.split(r'\\s*(?:(?<!\\d),|,(?!\\d)|;)\\s*|\\s+và\\s+',question,flags=re.I) if p.strip(' ,;?')]"
NEW = '''    # A quoted title is one reference, even when it contains conjunctions.
    # Split independent requests only outside complete paired quotations.
    quoted=[m.span() for m in re.finditer(r'“[^”\\n]+”|"[^"\\n]+"|«[^»\\n]+»',question)]
    boundaries=[m for m in re.finditer(r'\\s*(?:(?<!\\d),|,(?!\\d)|;)\\s*|\\s+và\\s+',question,flags=re.I)
                if not any(m.start()<end and m.end()>start for start,end in quoted)]
    pieces=[];start=0
    for boundary in boundaries:
        pieces.append(question[start:boundary.start()]);start=boundary.end()
    pieces.append(question[start:])
    parts=[p.strip(' ,;?') for p in pieces if p.strip(' ,;?')]'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    path = OUT / name
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists():
        assert path.read_text(encoding='utf-8') == text, 'Preserve prior artifact: ' + name
    else:
        path.write_text(text, encoding='utf-8')


def main():
    OUT.mkdir(exist_ok=True)
    active = ROOT / 'shopbot/grounded_rag.py'
    code = active.read_text(encoding='utf-8')
    assert code.count(OLD) == 1
    candidate = code.replace(OLD, NEW)
    target = OUT / 'grounded_rag_candidate.py'
    if target.exists():
        assert target.read_text(encoding='utf-8') == candidate
    else:
        target.write_text(candidate, encoding='utf-8')
    tree = ast.parse(candidate)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'question_parts')
    isolated = ast.Module(body=[fn], type_ignores=[])
    env = {'re': re, 'normalize': normalize}
    exec(compile(isolated, str(target), 'exec'), env)
    proposed = env['question_parts']
    rows_path = BASE / 'candidate_v9_development/results.json'
    review_path = BASE / 'candidate_v9_development/human_review.json'
    rows = json.loads(rows_path.read_text(encoding='utf-8'))
    reviews = json.loads(review_path.read_text(encoding='utf-8'))
    manifest_path = ROOT / 'data/unstructured/managed/ecdd21ab64861674/manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert len(rows) == 479 and all(r['split'] == 'development' for r in rows)
    checks = [
        ('Đọc “CPU, GPU và RAM”; giải thích bảo hành?', ['Đọc “CPU, GPU và RAM”', 'giải thích bảo hành']),
        ('Đọc "CPU và GPU", rồi nêu điều kiện?', ['Đọc "CPU và GPU"', 'rồi nêu điều kiện']),
        ('So “A và B” và «C; D»?', ['So “A và B”', '«C; D»']),
        ('Tên “CPU và GPU không đóng, RAM?', ['Tên “CPU', 'GPU không đóng', 'RAM']),
        ('Boost 5,2 GHz và TDP120W đúng không?', ['Boost 5,2 GHz', 'TDP120W đúng không']),
    ]
    for question, expected in checks:
        assert proposed(question) == expected, (question, proposed(question))
    audit = []
    changes = []
    for row in rows:
        question = row['question']
        old, new = question_parts(question), proposed(question)
        quotes = QUOTES.findall(question)
        if not quotes:
            assert old == new, row['id']
        if old != new:
            changes.append(dict(id=row['id'], question=question, before=old, candidate=new))
        if not quotes:
            continue
        result = row['result']
        sources = result.get('sources', [])
        titles = {normalize(q[1:-1]) for q in quotes}
        title_documents = {d['document_id'] for d in manifest if normalize(d.get('title', '')) in titles}
        available_owners = {f.get('document_id') for f in result.get('rag', {}).get('available_fields', [])}
        named = [s for s in sources if normalize(s.get('title', '')) in titles]
        named_chunks = {s['chunk_id'] for s in named}
        claims = result.get('rag', {}).get('claims', [])
        off_title = [c['text'] for c in claims if c.get('evidence') and not any(
            e.get('chunk_id') in named_chunks for e in c['evidence'])] if named else []
        audit.append(dict(id=row['id'], question=question, quoted_text=quotes,
                          old_parts=old, candidate_parts=new,
                          baseline_review=reviews.get(row['id']),
                          exact_title_in_returned_sources=bool(named),
                          exact_title_in_available_fields=bool(title_documents & available_owners),
                          source_snapshot_limitation='sources contain only selected chunks; absence does not prove retrieval miss',
                          title_documents=sorted({s['document_id'] for s in named}),
                          baseline_claims_from_other_titles=off_title,
                          baseline_answer=result.get('answer', '')))
    frozen = dict(production_sha256=sha(active), results_sha256=sha(rows_path),
                  manifest_sha256=sha(manifest_path),
                  human_review_sha256=sha(review_path), candidate_sha256=sha(target),
                  mode='offline only; no inference/retrieval; no production mutation',
                  code={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'app.py', *sorted((ROOT/'shopbot').glob('*.py'))]})
    write('metadata.json', frozen)
    write('audit.json', audit)
    write('parser_changes.json', changes)
    summary = dict(development_rows=len(rows), quoted_rows=len(audit),
                   changed_parser_rows=len(changes),
                   no_paired_quote_rows_unchanged=sum(not QUOTES.search(r['question']) for r in rows),
                   exact_title_in_returned_sources=sum(a['exact_title_in_returned_sources'] for a in audit),
                   exact_title_in_available_fields=sum(a['exact_title_in_available_fields'] for a in audit),
                   rows_with_other_title_claims=sum(bool(a['baseline_claims_from_other_titles']) for a in audit),
                   changed_ids=[r['id'] for r in changes], edge_case_assertions=len(checks),
                   model_calls=0, semantic_improvement_measured=False, production_changed=False)
    write('summary.json', summary)
    assert sha(active) == frozen['production_sha256']
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
