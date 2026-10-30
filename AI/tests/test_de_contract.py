import json
import sqlite3
import pytest
from test_de_reconcile import source
from shopbot.de_snapshot import capture_raw, stage_audit, digest
from shopbot.de_reconcile import reconcile_revision
from shopbot.de_contract import assess_curated_contract, ACCOUNTING, COST_METHOD


@pytest.fixture
def chain(source, tmp_path):
    with sqlite3.connect(source) as db:
        db.execute("INSERT INTO metadata VALUES ('scenario_id','fixture')")
    catalog = tmp_path/'catalog.json'
    catalog.write_text(json.dumps(dict(schema='agent-catalog-v1', products=[dict(id='p1')])), encoding='utf-8')
    raw = tmp_path/'captured'; rec = tmp_path/'reconciled'
    capture_raw(source, catalog, raw, 'fixture'); stage_audit(raw); reconcile_revision(raw, rec)
    evidence = tmp_path/'assumptions.json'
    evidence.write_text(json.dumps(dict(scenario_id='fixture', synthetic=True,
        period_start='2026-01-01', period_end='2026-01-03', accounting=ACCOUNTING,
        cost_method=COST_METHOD, laptop_model_price_assumptions_vnd={'p1':100},
        expected_monthly_revenue_reference_vnd=[100,200])), encoding='utf-8')
    return raw, rec, evidence, tmp_path/'contract'


def test_bound_contract_keeps_grain_simulation_and_coverage_without_activation(chain):
    raw, rec, evidence, out = chain
    before = {p:digest(p) for root in [raw,rec] for p in root.rglob('*') if p.is_file()}
    result = assess_curated_contract(*chain)
    c = json.loads((out/'contract.json').read_text(encoding='utf-8'))
    assert result['status']=='eligible_for_simulation_curated_build'
    assert not result['curated_published'] and not result['active_source_changed']
    assert c['data_kind']=='simulation' and c['money']['currency']=='VND'
    assert c['period']['end_inclusive']=='2026-01-03'
    assert c['grains']['inventory_daily']==['day','sku']
    assert c['accounting']['net_profit']=='not available'
    assert 'not zero' in c['coverage']['sales']
    assert c['assumptions_sha256']==digest(out/'assumptions.json')==digest(evidence)
    assert all(digest(p)==value for p,value in before.items())
    with pytest.raises(ValueError, match='exists'): assess_curated_contract(*chain)


@pytest.mark.parametrize('field,value', [
    ('synthetic',False), ('scenario_id','other-shop'), ('period_end','2026-01-04'),
    ('accounting','VAT included; net profit'), ('cost_method','weighted average'),
    ('laptop_model_price_assumptions_vnd',{}),
])
def test_wrong_or_missing_semantics_cannot_publish(chain, field, value):
    raw, rec, evidence, out = chain
    e=json.loads(evidence.read_text());e[field]=value;evidence.write_text(json.dumps(e))
    with pytest.raises(ValueError): assess_curated_contract(*chain)
    assert not out.exists()


@pytest.mark.parametrize('relative', ['staging/audit.json','staging/manifest.json','raw/ledger.sqlite'])
def test_upstream_tamper_rejected(chain, relative):
    raw, rec, evidence, out = chain
    with (raw/relative).open('ab') as stream: stream.write(b' ')
    with pytest.raises(ValueError): assess_curated_contract(*chain)
    assert not out.exists()


def test_reconciliation_from_other_source_rejected(chain):
    raw, rec, evidence, out = chain
    path=rec/'manifest.json';m=json.loads(path.read_text());m['source_id']='backend-35'
    path.write_text(json.dumps(m))
    with pytest.raises(ValueError, match='lineage'): assess_curated_contract(*chain)
    assert not out.exists()


def test_failed_check_cannot_be_hidden_by_top_level_pass(chain):
    raw, rec, evidence, out = chain
    path=rec/'reconciliation.json';r=json.loads(path.read_text());r['checks'][0]['passed']=False
    path.write_text(json.dumps(r))
    path=rec/'manifest.json';m=json.loads(path.read_text());m['reconciliation_sha256']=digest(rec/'reconciliation.json')
    path.write_text(json.dumps(m))
    with pytest.raises(ValueError, match='must pass'): assess_curated_contract(*chain)
    assert not out.exists()
