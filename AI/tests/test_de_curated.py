import json
import sqlite3
import pytest
from test_de_reconcile import source
from shopbot.de_snapshot import capture_raw, stage_audit, digest
from shopbot.de_reconcile import reconcile_revision
from shopbot.de_contract import assess_curated_contract, ACCOUNTING, COST_METHOD
from shopbot.de_curated import build_curated, TABLES


@pytest.fixture
def inputs(source, tmp_path):
    with sqlite3.connect(source) as db:
        db.execute("INSERT INTO metadata VALUES ('scenario_id','fixture')")
        db.execute("INSERT INTO operating_expenses VALUES ('e1','2026-01-02',17)")
        db.execute('ALTER TABLE products ADD COLUMN private_contact TEXT')
        db.execute("UPDATE products SET private_contact='do-not-export'")
    catalog=tmp_path/'catalog.json'
    catalog.write_text(json.dumps(dict(schema='agent-catalog-v1',products=[dict(id='p1')])))
    raw=tmp_path/'raw';rec=tmp_path/'rec';gate=tmp_path/'gate'
    capture_raw(source,catalog,raw,'fixture');stage_audit(raw);reconcile_revision(raw,rec)
    assumptions=tmp_path/'assumptions.json'
    assumptions.write_text(json.dumps(dict(scenario_id='fixture',synthetic=True,
        period_start='2026-01-01',period_end='2026-01-03',accounting=ACCOUNTING,
        cost_method=COST_METHOD,laptop_model_price_assumptions_vnd={'p1':100},
        expected_monthly_revenue_reference_vnd=[100,200])))
    assess_curated_contract(raw,rec,assumptions,gate)
    return raw,rec,gate,tmp_path/'curated'


def test_exact_projection_separate_grains_no_pii_or_zero_calendar_fill(inputs):
    raw,rec,gate,out=inputs
    before={p:digest(p) for root in [raw,rec,gate] for p in root.rglob('*') if p.is_file()}
    m=build_curated(*inputs)
    assert m['status']=='built_verified_not_activated'
    assert m['visibility']=='admin_only' and m['data_kind']=='simulation'
    assert not m['curated_published'] and not m['active_source_changed']
    assert m['database_sha256']==digest(out/'curated.sqlite')
    with sqlite3.connect(out/'curated.sqlite') as db:
        assert set(r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'"))==set(TABLES)|{'metadata'}
        assert [r[1] for r in db.execute('PRAGMA table_info(products)')]==['sku','stock']
        assert db.execute('SELECT COUNT(*) FROM financial_ledger').fetchone()[0]==2
        assert db.execute('SELECT SUM(amount) FROM operating_expenses').fetchone()[0]==17
        assert db.execute('SELECT COUNT(*) FROM financial_ledger WHERE day=?',('2026-01-01',)).fetchone()[0]==0
        assert dict(db.execute('SELECT key,value FROM metadata'))['sales_completeness']=='unverified'
    p=json.loads((out/'parity.json').read_text())
    assert p['passed'] and all(c['passed'] for c in p['checks'])
    assert p['totals']['operating_profit_before_interest_tax']==-17
    assert p['totals']['monthly_expenses']==[['2026-01',17]]
    assert all(digest(p)==sha for p,sha in before.items())
    with pytest.raises(ValueError,match='exists'):build_curated(*inputs)


def test_changed_raw_rejected_before_build(inputs):
    raw,rec,gate,out=inputs
    with (raw/'raw/ledger.sqlite').open('ab') as stream:stream.write(b' ')
    with pytest.raises(ValueError):build_curated(*inputs)
    assert not out.exists()


@pytest.mark.parametrize('field,value',[('source_id','backend35'),('data_kind','real'),('status','approved')])
def test_invalid_eligibility_cannot_build(inputs,field,value):
    raw,rec,gate,out=inputs
    path=gate/'manifest.json';m=json.loads(path.read_text());m[field]=value;path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='eligibility'):build_curated(*inputs)
    assert not out.exists()


def test_rehashed_but_unsupported_metric_contract_rejected(inputs):
    raw,rec,gate,out=inputs
    path=gate/'contract.json';c=json.loads(path.read_text());c['metrics']['net_revenue']='SUM(cost)'
    path.write_text(json.dumps(c));path=gate/'manifest.json';m=json.loads(path.read_text())
    m['contract_sha256']=digest(gate/'contract.json');path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='semantics'):build_curated(*inputs)
    assert not (out/'manifest.json').exists() and (out/'build.failed.json').exists()


def test_change_during_materialization_leaves_no_completion_marker(inputs,monkeypatch):
    import shopbot.de_curated as module
    raw,rec,gate,out=inputs;original=module._totals;changed=False
    def changing(db):
        nonlocal changed
        result=original(db)
        if not changed:
            changed=True
            with (gate/'assumptions.json').open('a') as stream:stream.write(' ')
        return result
    monkeypatch.setattr(module,'_totals',changing)
    with pytest.raises(RuntimeError,match='Upstream changed'):build_curated(*inputs)
    assert not (out/'manifest.json').exists() and (out/'build.failed.json').exists()


def test_wrong_persisted_totals_block_completion(inputs,monkeypatch):
    import shopbot.de_curated as module
    original=module._totals;calls=0
    def corrupt(db):
        nonlocal calls
        result=original(db);calls+=1
        if calls==3:result['net_revenue']+=1
        return result
    monkeypatch.setattr(module,'_totals',corrupt)
    with pytest.raises(ValueError,match='Persisted'):build_curated(*inputs)
    out=inputs[-1]
    assert not (out/'manifest.json').exists() and (out/'build.failed.json').exists()
