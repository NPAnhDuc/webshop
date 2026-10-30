"""Pinned, read-only curated quality reader for trusted server-side admin tools."""
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3

from .de_curated import TABLES
from .de_snapshot import digest, stable_sqlite


class CuratedReader:
    def __init__(self, revision, expected_manifest_sha256):
        # No disk access until the dispatcher has checked the authenticated role.
        self.revision = Path(revision).absolute()
        if not isinstance(expected_manifest_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_manifest_sha256):
            raise ValueError('Server-pinned manifest SHA256 required')
        self.expected_manifest_sha256 = expected_manifest_sha256

    def quality(self):
        root = self.revision.resolve(strict=True)
        def path(name):
            result = (root/name).resolve(strict=True)
            if not result.is_relative_to(root):
                raise ValueError('Curated artifact escaped configured revision')
            return result
        def read(name):
            return json.loads(path(name).read_text(encoding='utf-8'))
        manifest_path = path('manifest.json')
        if (root/'build.failed.json').exists() or digest(manifest_path) != self.expected_manifest_sha256:
            raise ValueError('Incomplete or changed curated revision')
        manifest = read('manifest.json')
        if (manifest.get('schema') != 'de-curated-build-v1'
                or manifest.get('status') != 'built_verified_not_activated'
                or manifest.get('data_kind') != 'simulation'
                or manifest.get('visibility') != 'admin_only'
                or manifest.get('database_path') != 'curated.sqlite'):
            raise ValueError('Unsupported curated contract')
        artifact_names = ['manifest.json', 'curated.sqlite', 'parity.json',
            'revalidated_gate/contract.json', 'revalidated_gate/manifest.json',
            'revalidated_gate/assumptions.json']
        hashes = {name:digest(path(name)) for name in artifact_names}
        if (hashes['curated.sqlite'] != manifest['database_sha256']
                or path('curated.sqlite').stat().st_size != manifest['database_bytes']
                or hashes['parity.json'] != manifest['parity_sha256']
                or hashes['revalidated_gate/contract.json'] != manifest['contract_sha256']):
            raise ValueError('Curated artifact hash/size mismatch')
        contract = read('revalidated_gate/contract.json')
        gate = read('revalidated_gate/manifest.json')
        parity = read('parity.json')
        if (contract.get('schema') != 'de-curated-contract-v1'
                or contract.get('source_id') != manifest['source_id']
                or contract.get('data_kind') != 'simulation'
                or contract.get('raw_manifest_sha256') != manifest['raw_manifest_sha256']
                or contract.get('reconciliation_manifest_sha256') != manifest['reconciliation_manifest_sha256']
                or contract.get('money', {}).get('currency') != 'VND'
                or gate.get('schema') != 'de-curated-eligibility-v1'
                or gate.get('status') != 'eligible_for_simulation_curated_build'
                or gate.get('source_id') != manifest['source_id']
                or gate.get('data_kind') != 'simulation'
                or gate.get('contract_sha256') != hashes['revalidated_gate/contract.json']
                or gate.get('assumptions_sha256') != hashes['revalidated_gate/assumptions.json']
                or contract.get('assumptions_sha256') != hashes['revalidated_gate/assumptions.json']):
            raise ValueError('Curated lineage mismatch')
        if (parity.get('schema') != 'de-curated-parity-v1' or parity.get('passed') is not True
                or parity.get('data_kind') != 'simulation' or not parity.get('checks')
                or any(check.get('passed') is not True for check in parity['checks'])):
            raise ValueError('Curated parity must pass')
        database = path('curated.sqlite'); stable_sqlite(database)
        with closing(sqlite3.connect(database.as_uri()+'?mode=ro', uri=True)) as db:
            db.execute('PRAGMA query_only=ON'); db.execute('BEGIN')
            metadata = dict(db.execute('SELECT key,value FROM metadata'))
            expected_metadata = dict(source='demo', scenario_id=manifest['source_id'], data_kind='simulation',
                currency='VND', visibility='admin_only', sales_completeness='unverified',
                period_start=contract['period']['start_inclusive'], period_end=contract['period']['end_inclusive'],
                contract_sha256=manifest['contract_sha256'])
            if metadata != expected_metadata:
                raise ValueError('Curated metadata mismatch')
            counts = {table:db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0] for table in TABLES}
            if counts != parity.get('row_counts'):
                raise ValueError('Curated row counts mismatch')
            first, last = db.execute('SELECT MIN(day),MAX(day) FROM financial_ledger').fetchone()
        stable_sqlite(database)
        if any(digest(path(name)) != value for name,value in hashes.items()):
            raise RuntimeError('Curated artifacts changed during read')
        if digest(manifest_path) != self.expected_manifest_sha256:
            raise RuntimeError('Server-pinned manifest changed during read')
        return dict(tool='admin.data_quality', data_kind='simulation', visibility='admin_only',
            source_id=manifest['source_id'], source_manifest_sha256=self.expected_manifest_sha256,
            database_sha256=manifest['database_sha256'], raw_manifest_sha256=manifest['raw_manifest_sha256'],
            reconciliation_manifest_sha256=manifest['reconciliation_manifest_sha256'],
            contract_sha256=manifest['contract_sha256'], period=contract['period'],
            row_counts=counts, parity_checks_passed=len(parity['checks']),
            observed_financial_dates=dict(first=first,last=last), coverage=contract['coverage'],
            active_source_changed=False,
            limitations=['Simulated internal projection, not real shop or live backend data.',
                'Passing these checks does not certify complete sales, policies, licenses or external truth.',
                'Orders, customer identities, purchase/movement records and forecast are outside this projection.',
                'Server must supply the authenticated role; file metadata does not authenticate a user.'])
