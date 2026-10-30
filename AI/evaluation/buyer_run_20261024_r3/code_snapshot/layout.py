"""The two data domains. Runtime state stays outside the source data."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / 'data' / 'structured'
UNSTRUCTURED = ROOT / 'data' / 'unstructured'
MONTHLY_RUNTIME = ROOT / 'runtime' / 'monthly'
