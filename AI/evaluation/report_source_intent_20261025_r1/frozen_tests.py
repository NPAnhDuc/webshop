from datetime import date
from pathlib import Path
import json
import pytest
from shopbot.rag_metrics import metric_request
from shopbot.rag_scope import resolve_scope
C=json.loads((Path(__file__).resolve().parents[1]/'evaluation/report_source_intent_20261025_r1/contract.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('question',C['report_questions'])
def test_explicit_report_reading_stays_on_document_path(question):
 assert metric_request(question,'admin',resolve_scope(question,date(2026,10,24))) is None

@pytest.mark.parametrize('question',C['sql_questions'])
def test_direct_kpi_remains_on_sql_path(question):
 assert metric_request(question,'admin',resolve_scope(question,date(2026,10,24))) is not None
