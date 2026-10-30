import hashlib
import re
import unicodedata
import requests
from collections import Counter
import math
from pathlib import Path
from .store import ROOT, DB, dataset_source, connect
from .monthly import active_documents, local_today, read_json
from .chunking import chunk_document


def normalize(text):
    text = unicodedata.normalize('NFD', text.lower().replace('đ','d'))
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


def extract(path):
    path = Path(path)
    if path.suffix.lower() == '.pdf':
        from pypdf import PdfReader
        return '\n'.join(p.extract_text() or '' for p in PdfReader(path).pages)
    if path.suffix.lower() == '.docx':
        from docx import Document
        doc = Document(path)
        return '\n'.join([p.text for p in doc.paragraphs] + [' | '.join(c.text for c in row.cells) for t in doc.tables for row in t.rows])
    return path.read_text(encoding='utf-8-sig')


def bm25_scores(question,texts):
    """Sparse rank preserves identifiers such as C-BTS; no fitted labels."""
    tokens=lambda s:re.findall(r'\b\w[\w-]*\b',normalize(s))
    corpus=[Counter(tokens(t)) for t in texts];query=set(tokens(question))
    lengths=[sum(c.values()) for c in corpus];average=sum(lengths)/max(1,len(lengths)) or 1
    frequency=Counter(term for c in corpus for term in c)
    result=[]
    for counts,length in zip(corpus,lengths):
        score=0.
        for term in query & counts.keys():
            idf=math.log(1+(len(corpus)-frequency[term]+.5)/(frequency[term]+.5))
            tf=counts[term];score+=idf*tf*2.2/(tf+1.2*(.25+.75*length/average))
        result.append(score)
    return result


def lexical_query(question,texts):
    """Small spelling/abbreviation expansion only for retrieval, never facts."""
    import difflib
    q=normalize(question)
    for short,long in {'bh':'bao hanh','baohanh':'bao hanh','ko':'khong','k':'khong',
                       'hdsd':'huong dan su dung','hd':'hoa don','kh':'khach hang'}.items():
        q=re.sub(r'\b'+short+r'\b',long,q)
    vocabulary=set(re.findall(r'\b[a-z]{4,}\b',normalize(' '.join(texts))))
    def correct(match):
        token=match[0]
        if token in vocabulary:return token
        options=difflib.get_close_matches(token,vocabulary,n=2,cutoff=.75 if len(token)==4 else .85)
        return options[0] if len(options)==1 else token
    return re.sub(r'\b[a-z]{4,}\b',correct,q)


def product_codes(title):
    return [token for token in re.findall(r'[a-z0-9-]+',normalize(title)) if len(token)>=3
            and re.search(r'[a-z].*[a-z]',token) and re.search(r'\d',token) and not re.fullmatch(r'\d+(?:gb|tb|hz|wh|w)',token)]


def named_product(document,question):
    title=normalize(document.get('title','?'))
    return title in question or any(re.search(r'(?<!\w)'+re.escape(token)+r'(?!\w)',question) for token in product_codes(title))


def search(question, role, extra_dir=None, db_path=DB, as_of=None, doc_types=None, top_k=6, categories=None, scope=None, historical=False, document_title=None):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    today=as_of or local_today()
    kind='demo' if not Path(db_path).exists() or dataset_source(db_path)=='demo' else 'shop'
    namespace=hashlib.sha256(str(Path(db_path).resolve()).encode()).hexdigest()[:16]
    index=read_json(ROOT/'runtime'/'monthly'/(namespace+'-knowledge.json'),{'documents':[]})
    monthly=index['documents']
    q=normalize(question)
    q=re.sub(r'\bq\s*([1-4])\b',r'quy \1',q)
    q=re.sub(r'\bt\s*(\d{1,2})\b',r'thang \1',q)
    month=re.search(r'thang\s*(\d{1,2})\b',q)
    year=re.search(r'\b(20\d{2})\b',q)
    if month and scope is None:
        period=f"{year[1] if year else today.year}-{int(month[1]):02d}"
        monthly=[d for d in monthly if d.get('doc_type')!='monthly_report' or d['period']==period]
    replaced={d['document_id'] for d in index['documents']
              if d['data_kind']==kind and d['status']=='approved' and d['effective_from']<=today.isoformat()}
    documents=list(monthly)
    scenario_documents=None
    if Path(db_path).exists():
        with connect(db_path,readonly=True) as con:
            if con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='metadata'").fetchone():
                row=con.execute("SELECT value FROM metadata WHERE key='knowledge_dir'").fetchone()
                if row:
                    folder=(ROOT/row[0]).resolve()
                    if not folder.is_relative_to((ROOT/'data').resolve()): raise ValueError('Knowledge folder outside data')
                    scenario_documents=read_json(folder/'manifest.json',[])
    if scenario_documents is not None:
        documents+=scenario_documents
    from .knowledge import KnowledgeStore
    if Path(db_path).exists():documents+=KnowledgeStore(db_path).records()
    if historical and role=='admin':
        current=active_documents(documents,role,kind,today)
        allowed={d['document_id'] for d in current}
        # Explicit admin archive reads only; deleted IDs and drafts stay excluded.
        documents=[dict(d,historical=True) for d in documents if d['document_id'] in allowed and d['data_kind']==kind
                   and d['status']=='approved' and d['effective_from']<=today.isoformat()]
    else:documents=active_documents(documents,role,kind,today)
    if month and scope is None:
        target=f"{year[1] if year else today.year}-{int(month[1]):02d}"
        documents=[d for d in documents if d.get('doc_type')!='monthly_report' or d.get('period',d.get('document_id','').removeprefix('monthly-report-'))==target]
    base=ROOT/'data'/'unstructured'
    dirs=[base/'public']
    if role=='admin':
        dirs += [base/'admin',base/'uploads']
        if extra_dir: dirs.append(Path(extra_dir))
    for directory in ([] if scenario_documents is not None else dirs):
        if not directory.exists():continue
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in ('.txt','.md','.pdf','.docx') or path.stem in replaced:continue
            if kind=='shop' and '-mau' in path.stem:continue
            documents.append({'source':path.name,'text':extract(path),'authority':'legacy_shop_document'})
    if scenario_documents is None and role=='admin' and not any(w in q for w in ('bao hanh','doi tra','tra gop','chinh sach gia','muc tieu doanh thu')):
        for path in sorted((base/'reference').glob('*/*.md')):
            documents.append({'source':str(path.relative_to(base)),'text':extract(path),'authority':'external_reference_only'})
    chunks=[]
    if document_title is not None:
        # Source identity is stronger than a guessed document type or incidental
        # catalog SKU. Documents have already passed role/status/date filtering.
        title=normalize(' '.join(document_title.split()))
        documents=[d for d in documents if normalize(' '.join(d.get('title','').split()))==title]
    if doc_types is not None and document_title is None:
        documents=[d for d in documents if d.get('doc_type') in doc_types
                   or (scope is not None and d.get('doc_type')=='product' and named_product(d,q))]
    if categories is not None and document_title is None:
        documents=[d for d in documents if d.get('category','all') in ['all',*categories]
                   or (d.get('doc_type')=='product' and d.get('title') and normalize(d['title']) in normalize(question))]
    quarter=re.search(r'quy\s*([1-4])\b',q)
    if scope is not None:
        from .rag_scope import filter_periods
        documents=filter_periods(documents,scope)
    elif quarter and year and len(re.findall(r'quy\s*[1-4]\b',q))==1:
        target_period=f'{year[1]}-Q{quarter[1]}'
        documents=[d for d in documents if d.get('doc_type')!='sales_plan' or target_period in d.get('document_id','')]
    elif month and year:
        target_period=f'{year[1]}-Q{(int(month[1])-1)//3+1}'
        documents=[d for d in documents if d.get('doc_type')!='sales_plan' or target_period in d.get('document_id','')]
    if not isinstance(top_k,int) or not 1<=top_k<=12:raise ValueError('top_k must be 1..12')
    if scope is not None and document_title is None:
        named=[d for d in documents if d.get('doc_type')=='product' and named_product(d,q)]
        names={d['document_id'] for d in named};codes=set(token for d in named for token in product_codes(d.get('title','')))
        if names:
            documents=[d for d in documents if (d.get('doc_type')!='product' or d['document_id'] in names)
                       and (not product_codes(d.get('title','')) or not codes or bool(codes.intersection(product_codes(d.get('title','')))))]
    for document in documents:
        import os
        chunks.extend(chunk_document(document,max_words=100 if os.getenv('VI_EMBEDDING_URL') else 180))
    if not chunks:return []
    vectorizer=TfidfVectorizer(preprocessor=normalize,ngram_range=(1,2))
    try: matrix=vectorizer.fit_transform([c.get('retrieval_text',c['text']) for c in chunks])
    except ValueError:return []
    lexical=lexical_query(question,[c.get('retrieval_text',c['text']) for c in chunks])
    scores=cosine_similarity(vectorizer.transform([lexical]),matrix)[0]
    sparse=bm25_scores(lexical,[c.get('retrieval_text',c['text']) for c in chunks])
    try:
        from .dense_retrieval import dense_scores
        result=dense_scores(question,chunks)
    except (requests.RequestException,ValueError,KeyError,TypeError):
        result=None
    if result is not None:
        dense,model,truncated=result
        lexical_rank=sorted(range(len(chunks)),key=lambda i:float(scores[i]),reverse=True)
        dense_rank=sorted(range(len(chunks)),key=lambda i:dense[i],reverse=True)
        fused={i:0. for i in range(len(chunks))}
        sparse_rank=sorted(range(len(chunks)),key=lambda i:sparse[i],reverse=True)
        for ranking in (lexical_rank,dense_rank,sparse_rank):
            for rank,i in enumerate(ranking): fused[i]+=1/(60+rank+1)
        ranked=sorted(fused,key=fused.get,reverse=True)
        candidates=[dict(chunks[i],score=round(fused[i],5),dense_score=round(dense[i],4),lexical_score=round(float(scores[i]),4),bm25_score=round(sparse[i],4),retrieval='Vietnamese dense + TF-IDF + BM25 RRF',embedding_model=model,
                     embedding_truncated=truncated[i]) for i in ranked[:max(48 if scope is not None else 12,top_k)] if scores[i]>.08 or dense[i]>.45]
    else:
        candidates=[dict(chunks[i],score=round(float(scores[i]),3),lexical_score=round(float(scores[i]),4),retrieval='TF-IDF fallback') for i in scores.argsort()[::-1][:(48 if scope is not None else 12)] if scores[i]>0.08]
    if scope is not None:
        named=[d for d in documents if d.get('doc_type')=='product' and named_product(d,q)]
        names={d['document_id'] for d in named}
        chosen=[];seen=set()
        def add(item):
            if item['chunk_id'] not in seen:chosen.append(item);seen.add(item['chunk_id'])
        # Complete named-SKU attributes before adding loosely related products.
        for item in chunks:
            if item.get('document_id') in names:add(dict(item,retrieval='explicit named product',score=1.0))
        if scope.get('months') or scope.get('quarters'):
            owners=set()
            for item in candidates:
                key=(item.get('document_id'),item.get('version'))
                if item.get('doc_type') in ('monthly_report','sales_plan') and key not in owners:
                    add(item);owners.add(key)
        for item in candidates:add(item)
        candidates=chosen
    import os
    if os.getenv('RAG_RERANK','0')=='1' and candidates:
        from .rag_answer import rerank
        return rerank(question,candidates,top_k)
    return candidates[:top_k]
