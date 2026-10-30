import json
from pathlib import Path
from datetime import date
from shopbot.quality_eval import grade,observation
from shopbot.monthly import active_documents


def fixture_result(doc='right',version=3,text='RAM:16GB.'):
 s=dict(document_id=doc,version=version,chunk_id='chunk',text=text,audience='customer')
 return dict(answer=text,basic_action='answer',sources=[s],rag=dict(answerability='full',claims=[dict(text=text,evidence=[dict(chunk_id='chunk',quotes=[text])])],available_fields=[dict(document_id=doc)]))


def case(behavior='facts'):
 return dict(role='customer',expected_behavior=behavior,required=[dict(document_id='right',version=3,quote='RAM:16GB.')])


def test_same_number_wrong_period_or_sku_is_a_failure():
 result=fixture_result(doc='other')
 assert grade(case(),result)['status']=='FAIL_CHECKS'
 assert grade(case(),fixture_result())['status']=='PASS_CHECKS'


def test_old_version_not_accepted_as_current():
 assert grade(case(),fixture_result(version=2))['status']=='FAIL_CHECKS'


def test_semantic_answer_never_auto_passes():
 assert grade(case('semantic'),fixture_result())['status']=='NEEDS_REVIEW'


def test_fake_quote_and_private_source_fail_checks():
 result=fixture_result();result['sources'][0]['text']='Different text'
 assert any(x['cause']=='EVIDENCE_INTEGRITY' for x in grade(case(),result)['issues'])
 result=fixture_result();result['sources'][0]['audience']='admin'
 assert any(x['cause']=='PERMISSION' for x in grade(case(),result)['issues'])


def test_unknown_product_cannot_be_filled_by_another_machine():
 assert grade(case('unknown'),fixture_result())['status']=='FAIL_CHECKS'


def test_missing_log_is_a_review_signal_not_a_fact_or_failure():
 task=observation(dict(status='none',role='customer',question='Tôi có email a@b.com',origin='interactive'))
 assert task['status']=='REVIEW_REQUIRED' and 'a@b.com' not in task['question']
 assert observation(dict(status='full',action='answer',question='Good')) is None


def test_frozen_bank_keeps_conversations_and_active_source_versions():
 root=Path(__file__).resolve().parents[1]/'evaluation/quality_loop_20261021'
 bank=json.loads((root/'bank.json').read_text(encoding='utf8'))
 docs=json.loads((root/'gold_sources.json').read_text(encoding='utf8'))
 active={(d['document_id'],d['version']):d for d in active_documents(docs,'admin','demo',date(2026,10,21))}
 splits={}
 for c in bank:
  assert splits.setdefault(c['conversation'],c['split'])==c['split']
  for g in c['required']:
   source=active[(g['document_id'],g['version'])]
   assert g['quote'] in source['text']
   assert c['role']=='admin' or source['audience']=='customer'
 assert len(bank)==600 and sum(c['role']=='customer' for c in bank)==300


def test_full_interactive_answers_still_enter_review_queue():
 row=dict(status='full',action='answer',question='Looks confident',role='customer',origin='interactive')
 assert observation(row) is None
 assert observation(row,include_full=True)['status']=='REVIEW_REQUIRED'


def test_targeted_selection_keeps_prelude_and_cannot_open_validation():
    import pytest
    from shopbot.quality_eval import select_cases
    bank=[dict(id='first',split='development',conversation='a'),dict(id='other',split='development',conversation='b'),dict(id='followup',split='development',conversation='a'),dict(id='sealed',split='validation',conversation='c')]
    assert [c['id'] for c in select_cases(bank,'development',requested=['followup'])]==['first','followup']
    with pytest.raises(ValueError):select_cases(bank,'development',requested=['sealed'])
    with pytest.raises(ValueError):select_cases(bank,'development',requested=[])
