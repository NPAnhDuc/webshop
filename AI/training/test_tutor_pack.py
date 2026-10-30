import json
import unittest
import copy
from pathlib import Path
from review_corrections import verify_feedback

HERE=Path(__file__).resolve().parent
def read(name):return [json.loads(line) for line in (HERE/'data'/name).read_text(encoding='utf-8').splitlines()]

class TutorDataTests(unittest.TestCase):
    def test_product_groups_never_cross_splits(self):
        seen={}
        for row in read('qa.jsonl'):
            self.assertEqual(seen.setdefault(row['group_id'],row['split']),row['split'])
    def test_supported_answers_are_exact_source_values(self):
        products={r['record_id']:r for r in read('../../data/structured/processed/product_catalog.jsonl')}
        for row in read('qa.jsonl'):
            if row['answerability']!='supported':continue
            product=products[row['positive_id']]
            value=product['attributes'].get(row['field'],product.get(row['field']))
            self.assertIsNotNone(value)
            self.assertEqual(json.loads(row['expected_answer']),value)
    def test_unknown_shop_facts_require_abstention(self):
        rows=[r for r in read('qa.jsonl') if r['answerability']=='must_abstain']
        self.assertEqual(len(rows),37*3)
        self.assertTrue(all(r['expected_answer']=='Chưa có dữ liệu được xác minh của shop.' for r in rows))
    def test_all_routing_labels_use_upstream_kev_schema(self):
        seen={}
        for split in ('train','validation','test'):
            labels=set()
            for row in read('kev-'+split+'.jsonl'):
                self.assertNotIn('labels',row)
                question=row['questions']['intent']
                self.assertIn(question['label'],question['criteria'])
                labels.add(question['label'])
                self.assertEqual(seen.setdefault(row['_meta']['group_id'],split),split)
            self.assertEqual(labels,{'products','documents','handoff','clarify'})
    def test_all_qa_citations_exist(self):
        ids={d['id'] for d in read('corpus.jsonl')}
        self.assertEqual(len(ids),37)
        self.assertTrue(all(q['positive_id'] in ids for q in read('qa.jsonl')))
    def test_notebook_code_parses(self):
        nb=json.loads((HERE/'ShopBot_Tutor_Colab.ipynb').read_text(encoding='utf-8'))
        for cell in nb['cells']:
            if cell['cell_type']=='code':compile(''.join(cell['source']),'notebook','exec')
    def test_tutor_rejects_guesses_and_heldout_contamination(self):
        products={r['record_id']:r for r in read('../../data/structured/processed/product_catalog.jsonl')}
        corpus={r['id']:r for r in read('corpus.jsonl')}
        train_id=next(i for i,d in corpus.items() if d['split']=='train')
        product=products[train_id]
        field=next(k for k,v in product['attributes'].items() if v is not None and k!='name')
        valid={'source_id':train_id,'field':field,'expected_answer':json.dumps(product['attributes'][field],ensure_ascii=False),
               'question':'Nhờ tra lại thông số trong nguồn?','evidence_quote':corpus[train_id]['text'],
               'approved':True,'reviewed_by':'test-reviewer'}
        self.assertEqual(verify_feedback(valid,products,corpus)['split'],'train')
        bad=copy.deepcopy(valid);bad['expected_answer']='999999999999'
        with self.assertRaises(ValueError):verify_feedback(bad,products,corpus)
        bad=copy.deepcopy(valid);bad['field']='stock'
        with self.assertRaises(ValueError):verify_feedback(bad,products,corpus)
        bad=copy.deepcopy(valid);bad['source_id']=next(i for i,d in corpus.items() if d['split']=='test')
        with self.assertRaises(ValueError):verify_feedback(bad,products,corpus)

if __name__=='__main__':unittest.main()
