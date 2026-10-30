"""Generate downloadable example reports from the same SQL analysis as the app."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shopbot.business_analysis import analyze_business, format_business_report
from shopbot.reporting import render_report_png, explain_visual


def main():
    folder=ROOT/'reports/examples';folder.mkdir(parents=True,exist_ok=True)
    report=analyze_business(ROOT/'data/business_sql/scenario_v1/shop.sqlite','2026-07-01','2026-10-01')
    for kind in ('overview','financial_flow'):
        (folder/f'2026-Q3-{kind}.png').write_bytes(render_report_png(report,kind))
    (folder/'2026-Q3-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'2026-Q3-analysis.md').write_text('# Báo cáo Q3/2026 — MÔ PHỎNG\n\n'+format_business_report(report)+'\n\n'+explain_visual(report),encoding='utf-8')
    print(folder)


if __name__=='__main__': main()
