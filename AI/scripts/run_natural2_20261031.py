"""Run the existing quality-loop runner against natural2_20261031."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("run_quality_loop", ROOT / "scripts/run_quality_loop.py")
loop = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = loop
spec.loader.exec_module(loop)
loop.BASE = ROOT / "evaluation/natural2_20261031"

if __name__ == "__main__":
    loop.main()
