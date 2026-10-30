import json
import sqlite3
import pytest
from test_de_curated import inputs, source
from test_agent_tools import catalog
from shopbot.agent_tools import AgentTools
from shopbot.curated_reader import CuratedReader
from shopbot.de_curated import build_curated
from shopbot.de_snapshot import digest


@pytest.fixture
def built(inputs):
    build_curated(*inputs)
    return inputs[-1]


def reader(root):return CuratedReader(root,digest(root/'manifest.json'))


def test_quality_is_read_only_provenance_bound_and_honest_about_coverage(built):
    before={p:digest(p) for p in built.rglob('*') if p.is_file()}
    tool=AgentTools(catalog(),None,curated_reader=reader(built))
    result=tool.execute('admin','admin.data_quality',{})
    assert result['row_counts']==dict(products=1,financial_ledger=2,operating_expenses=1,inventory_daily=3)
    assert result['observed_financial_dates']==dict(first='2026-01-02',last='2026-01-03')
    assert result['data_kind']=='simulation' and result['visibility']=='admin_only'
    assert result['parity_checks_passed']==8 and 'unverified' in result['coverage']['sales']
    assert result['source_manifest_sha256']==digest(built/'manifest.json')
    assert not result['active_source_changed']
    assert all(digest(p)==value for p,value in before.items())
    assert 'do-not-export' not in json.dumps(result)


def test_customer_role_rejected_before_reader_io(tmp_path):
    missing=CuratedReader(tmp_path/'does-not-exist','a'*64)
    tools=AgentTools(catalog(),None,curated_reader=missing)
    with pytest.raises(PermissionError):tools.execute('customer','admin.data_quality',{})
    with pytest.raises(PermissionError):tools.execute('owner','admin.data_quality',{})


@pytest.mark.parametrize('args',[{'role':'admin'},{'path':'elsewhere'},{'sql':'SELECT 1'},{'source_id':'backend35'}])
def test_model_cannot_select_source_execute_sql_or_change_role(args):
    tools=AgentTools(catalog(),None)
    with pytest.raises(ValueError,match='Unknown tool arguments'):tools.execute('admin','admin.data_quality',args)


def test_unconfigured_reader_does_not_fall_back_to_financial_database():
    with pytest.raises(ValueError,match='not configured'):
        AgentTools(catalog(),'some-db').execute('admin','admin.data_quality',{})


@pytest.mark.parametrize('file',['curated.sqlite','parity.json','revalidated_gate/contract.json'])
def test_artifact_tamper_rejected(built,file):
    r=reader(built)
    with (built/file).open('ab') as stream:stream.write(b' ')
    with pytest.raises(ValueError,match='hash/size'):r.quality()


def test_rehashing_artifact_and_manifest_cannot_replace_server_pin(built):
    r=reader(built)
    path=built/'manifest.json';m=json.loads(path.read_text());m['source_id']='other'
    path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='changed'):r.quality()


def test_metadata_label_mismatch_rejected_even_with_new_server_pin(built):
    with sqlite3.connect(built/'curated.sqlite') as db:
        db.execute("UPDATE metadata SET value='real' WHERE key='data_kind'")
    path=built/'manifest.json';m=json.loads(path.read_text());m['database_sha256']=digest(built/'curated.sqlite')
    m['database_bytes']=(built/'curated.sqlite').stat().st_size;path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='metadata'):reader(built).quality()


def test_file_path_in_manifest_cannot_redirect_reader(built):
    path=built/'manifest.json';m=json.loads(path.read_text());m['database_path']='../elsewhere.sqlite'
    path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='Unsupported'):reader(built).quality()


def test_partial_build_has_no_readable_quality(built):
    (built/'build.failed.json').write_text('{}')
    with pytest.raises(ValueError,match='Incomplete'):reader(built).quality()


def test_gate_from_another_source_is_rejected(built):
    path=built/'revalidated_gate/manifest.json';m=json.loads(path.read_text());m['source_id']='backend35'
    path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match='lineage'):reader(built).quality()


def test_active_wal_is_not_ignored(built):
    (built/'curated.sqlite-wal').write_bytes(b'active')
    with pytest.raises(ValueError,match='stable SQLite'):reader(built).quality()


def test_change_during_read_does_not_return_stale_summary(built,monkeypatch):
    import shopbot.curated_reader as module
    r=reader(built);original=module.stable_sqlite;calls=0
    def changing(path):
        nonlocal calls
        original(path);calls+=1
        if calls==2:
            with (built/'parity.json').open('a') as stream:stream.write(' ')
    monkeypatch.setattr(module,'stable_sqlite',changing)
    with pytest.raises(RuntimeError,match='changed during read'):r.quality()
