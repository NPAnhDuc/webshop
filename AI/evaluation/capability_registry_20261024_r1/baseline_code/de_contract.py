"""Fail-closed eligibility contract for simulated curated builds; never activates data."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .de_snapshot import digest, verify_raw, write_new


ACCOUNTING = 'All prices exclude VAT; no income tax or interest model. Output is operating profit before interest/tax, not net profit.'
COST_METHOD = 'FIFO with ±1.5% synthetic purchase cost variation; returns restore original item cost only if saleable.'
GRAINS = {'financial_ledger': ['id'], 'operating_expenses': ['id'],
          'inventory_daily': ['day', 'sku'], 'products': ['sku']}
METRICS = {'net_revenue': 'SUM(financial_ledger.revenue)',
           'net_cogs': 'SUM(financial_ledger.cost)',
           'gross_profit': 'net_revenue - net_cogs',
           'operating_expenses': 'SUM(operating_expenses.amount)',
           'operating_profit_before_interest_tax': 'gross_profit - operating_expenses'}


def assess_curated_contract(revision, reconciliation, assumptions, output):
    """Bind declared scenario semantics to verified bytes, without publishing a database.

    This adapter accepts simulation assumptions only. It cannot certify real imports,
    source completeness, licensing or market validity. All output is a NEW revision.
    """
    revision = Path(revision).resolve(strict=True)
    reconciliation = Path(reconciliation).resolve(strict=True)
    assumptions = Path(assumptions).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Contract revision exists; preserve previous results')
    tracked = [revision/'manifest.json', revision/'staging/manifest.json',
               revision/'staging/audit.json', revision/'staging/quarantine.json',
               reconciliation/'manifest.json', reconciliation/'reconciliation.json',
               reconciliation/'quarantine.json', assumptions]
    hashes = {p: digest(p) for p in tracked}
    raw = verify_raw(revision)
    stage = json.loads(tracked[1].read_text(encoding='utf-8'))
    audit = json.loads(tracked[2].read_text(encoding='utf-8'))
    rec = json.loads(tracked[4].read_text(encoding='utf-8'))
    report = json.loads(tracked[5].read_text(encoding='utf-8'))
    evidence_bytes = assumptions.read_bytes()
    evidence = json.loads(evidence_bytes.decode('utf-8'))
    ledger_hash = raw['artifacts']['ledger.sqlite']['sha256']
    if (raw['data_kind'] != 'simulation' or rec.get('data_kind') != 'simulation'
            or raw.get('source_metadata', {}).get('source') != 'demo'):
        raise ValueError('This contract adapter supports simulation only')
    if (stage.get('schema') != 'de-staging-audit-v1'
            or stage.get('data_kind') != 'simulation'
            or stage.get('status') != 'audit_passed_pending_reconciliation'
            or stage.get('source_id') != raw['source_id']
            or stage.get('raw_manifest_sha256') != hashes[tracked[0]]
            or stage.get('audit_sha256') != hashes[tracked[2]]
            or stage.get('quarantine_sha256') != hashes[tracked[3]]):
        raise ValueError('Invalid staging lineage')
    if (rec.get('schema') != 'de-reconciliation-manifest-v1'
            or rec.get('status') != 'reconciled_pending_curated_design'
            or rec.get('source_id') != raw['source_id']
            or rec.get('raw_manifest_sha256') != hashes[tracked[0]]
            or rec.get('staging_manifest_sha256') != hashes[tracked[1]]
            or rec.get('reconciliation_sha256') != hashes[tracked[5]]
            or report.get('schema') != 'de-reconciliation-v1'
            or report.get('source', {}).get('sha256') != ledger_hash):
        raise ValueError('Invalid reconciliation lineage')
    for result, quarantine in [(audit, tracked[3]), (report, tracked[6])]:
        checks = result.get('checks')
        if (result.get('passed') is not True or not checks
                or any(c.get('passed') is not True for c in checks)
                or result.get('quarantine_samples') != []
                or json.loads(quarantine.read_text(encoding='utf-8')) != []):
            raise ValueError('Audit/reconciliation must pass with empty quarantine')
    if (audit.get('schema') != 'de-ledger-audit-v1'
            or audit.get('source', {}).get('sha256') != ledger_hash
            or audit.get('source', {}).get('catalog', {}).get('sha256')
                != raw['artifacts']['catalog_public.json']['sha256']):
        raise ValueError('Audit belongs to another ledger')
    with closing(sqlite3.connect((revision/'raw/ledger.sqlite').as_uri()+'?mode=ro', uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        metadata = dict(db.execute('SELECT key,value FROM metadata'))
    period = report['totals']['declared_period']
    if (evidence.get('synthetic') is not True
            or evidence.get('scenario_id') != raw['source_id']
            or metadata.get('scenario_id') != raw['source_id']
            or evidence.get('period_start') != period['start']
            or evidence.get('period_end') != period['end']
            or metadata.get('period_start') != period['start']
            or metadata.get('period_end') != period['end']):
        raise ValueError('Assumptions source/period mismatch')
    if (evidence.get('accounting') != ACCOUNTING or evidence.get('cost_method') != COST_METHOD
            or not evidence.get('laptop_model_price_assumptions_vnd')
            or not evidence.get('expected_monthly_revenue_reference_vnd')):
        raise ValueError('Unsupported or missing declared accounting/currency basis')
    contract = dict(schema='de-curated-contract-v1', source_id=raw['source_id'],
        data_kind='simulation', money=dict(currency='VND', storage='integer',
            basis='scenario declaration, not independently certified', vat='excluded'),
        accounting=dict(cost_method='FIFO', intraday_order=['day', 'inventory_moves.id'],
            restocked_returns='append new lot at reversed original cost',
            interest_and_income_tax='not modeled', net_profit='not available'),
        period=dict(start_inclusive=period['start'], end_inclusive=period['end']),
        grains=GRAINS, metrics=METRICS,
        coverage=dict(inventory='declared day x SKU grid reconciled',
            sales='unverified; absent days are not zero', demand='not observed'),
        raw_manifest_sha256=hashes[tracked[0]], staging_manifest_sha256=hashes[tracked[1]],
        reconciliation_manifest_sha256=hashes[tracked[4]],
        reconciliation_sha256=hashes[tracked[5]], ledger_sha256=ledger_hash,
        assumptions_sha256=hashes[assumptions],
        usage='internal simulated pipeline evaluation; no new external usage rights inferred')
    # Detect changes before completing the new artifact; never rewrite upstream files.
    verify_raw(revision)
    if any(digest(p) != value for p, value in hashes.items()):
        raise RuntimeError('Upstream evidence changed during contract assessment')
    output.mkdir(parents=True, exist_ok=False)
    (output/'assumptions.json').write_bytes(evidence_bytes)
    if digest(output/'assumptions.json') != hashes[assumptions]:
        raise RuntimeError('Assumptions copy mismatch')
    write_new(output/'contract.json', contract)
    manifest = dict(schema='de-curated-eligibility-v1', source_id=raw['source_id'],
        data_kind='simulation', status='eligible_for_simulation_curated_build',
        contract_sha256=digest(output/'contract.json'), assumptions_sha256=hashes[assumptions],
        implementation_sha256=digest(__file__), curated_published=False, active_source_changed=False,
        limitations=['Eligibility only; no curated tables or active pointer published.',
            'Declared simulation currency/accounting, not certification of real data or licensing.',
            'Hash/no-overwrite protocol is not a signature or WORM storage.'])
    write_new(output/'manifest.json', manifest)
    return manifest
