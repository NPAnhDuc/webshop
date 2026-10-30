"""Traditional TF-IDF retrieval reference; never fit on question labels."""
import json
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

HERE=Path(__file__).resolve().parent
docs=[json.loads(s) for s in (HERE/'data/corpus.jsonl').read_text(encoding='utf-8').splitlines()]
qa=[json.loads(s) for s in (HERE/'data/qa.jsonl').read_text(encoding='utf-8').splitlines()]
vectorizer=TfidfVectorizer(ngram_range=(1,2),strip_accents='unicode')
matrix=vectorizer.fit_transform([d['text'] for d in docs])
report={'method':'TF-IDF word unigrams/bigrams','scope':'Source retrieval only on same frozen pilot; not full chatbot accuracy','splits':{}}
for split in ('validation','test'):
    questions=[q for q in qa if q['split']==split and q['answerability']=='supported']
    scores=cosine_similarity(vectorizer.transform([q['question'] for q in questions]),matrix)
    correct1=correct3=0
    for q,row in zip(questions,scores):
        found=[docs[i]['id'] for i in row.argsort()[::-1][:3]]
        correct1+=found[0]==q['positive_id']
        correct3+=q['positive_id'] in found
    report['splits'][split]={'samples':len(questions),'recall_at_1':correct1/len(questions),'recall_at_3':correct3/len(questions)}
out=HERE/'results'
out.mkdir(exist_ok=True)
(out/'lexical-baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
