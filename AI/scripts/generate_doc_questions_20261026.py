"""Ask the local base model to write questions for each non-product fragment.

Only the QUESTION comes from the model; the label stays the fragment itself
(the sentence the question was written from). Every question must name the
fragment's anchor (month, quarter, campaign code or document title) so that a
sentence repeated across documents can still be attributed. Output feeds
scripts/build_qwen_sft_20261026.py --v2.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shopbot.chunking import chunk_document
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import active_documents
from shopbot.rag_answer import chat,evidence_fragments
from shopbot.retrieval import normalize

DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
OUT=ROOT/'data/finetune_qwen_20261026_v2/doc_questions.jsonl'
TODAY=date(2026,10,26)
SKIP=re.compile(r'^(?:nguon|doi chieu|tai lieu tham khao ben ngoai|du lieu mo phong|khong phai chinh sach hay ket qua)')
DATED={'monthly_report','sales_plan'}
STOP=set('va cua cho ve la gi co khong nhu the nao theo trong voi cac mot shop'.split())
SCHEMA={'type':'object','properties':{'questions':{'type':'array','minItems':1,'maxItems':2,'items':{'type':'string','maxLength':220}}},
        'required':['questions'],'additionalProperties':False}
PROMPT='''Viết 1-2 câu hỏi tiếng Việt tự nhiên (có dấu) mà ĐOẠN trả lời trực tiếp, như người dùng thật hỏi chatbot shop máy tính.
Mỗi câu hỏi BẮT BUỘC chứa nguyên văn cụm "anchor". Không chép nguyên câu của đoạn, không hỏi điều đoạn không nói, không dùng "này/đó".
Một câu hỏi chỉ hỏi một ý, không dùng dấu phẩy hoặc chữ "và" để nối hai ý. Trả JSON theo schema.'''


def anchor(doc,text):
    title=doc.get('title','')
    if doc['doc_type']=='monthly_report':
        m=re.search(r'(20\d{2})-(\d{2})',title+' '+doc['document_id'])
        return f'báo cáo tháng {int(m[2])}/{m[1]}' if m else title
    if doc['doc_type']=='sales_plan':
        m=re.search(r'(20\d{2})-Q([1-4])',title+' '+doc['document_id'])
        return f'kế hoạch quý {m[2]}/{m[1]}' if m else title
    code=re.search(r'\|\s*([A-Z][A-Z0-9]{0,5}-[A-Z0-9]{2,})\s*\|',text)
    if code:return code[1]
    return title


def main():
    store=KnowledgeStore(DB)
    docs=[d for d in active_documents(store.all_records(),'admin',store.kind,TODAY) if d['doc_type']!='product']
    OUT.parent.mkdir(parents=True,exist_ok=True)
    done={json.loads(l)['fragment'] for l in OUT.read_text(encoding='utf8').splitlines()} if OUT.exists() else set()
    with OUT.open('a',encoding='utf8') as out:
        for n,doc in enumerate(docs):
            frags=[f['text'] for f in evidence_fragments(chunk_document(doc,max_words=100)).values()
                   if len(f['text'].split())>=5 and not SKIP.search(normalize(f['text']))]
            for text in frags:
                if text in done:continue
                a=anchor(doc,text)
                try:result=chat(PROMPT,dict(anchor=a,document=doc.get('title'),doc_type=doc['doc_type'],fragment=text),SCHEMA,max_tokens=200)
                except Exception as exc:
                    print('skip',doc['document_id'],type(exc).__name__,flush=True);continue
                raw=[q.strip() for q in result.get('questions',[])]
                # Report/plan sentences repeat month to month, so those need the
                # exact period; other documents only need a word of their title.
                title_words=set(normalize(doc.get('title','')).split())-STOP
                kept=[q for q in raw if normalize(a) in normalize(q) or
                      (doc['doc_type'] not in DATED and title_words&set(normalize(q).split()))]
                out.write(json.dumps(dict(fragment=text,anchor=a,questions=kept,raw=raw,entity=doc['document_id'],doc_type=doc['doc_type'],
                                          audience=doc.get('audience'),title=doc.get('title')),ensure_ascii=False)+'\n')
                out.flush();done.add(text)
            print(n+1,len(docs),doc['document_id'],flush=True)


if __name__=='__main__':main()
