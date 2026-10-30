"""Ask the prototype data-team agent one question and print its answer and notebook path."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot import notebook_agent as agent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question')
    parser.add_argument('--model',help=f'Ollama model (default AGENT_CODE_MODEL or {agent.DEFAULT_MODEL})')
    parser.add_argument('--max-cells',type=int,default=agent.MAX_CELLS)
    parser.add_argument('--cell-timeout',type=int,default=agent.CELL_TIMEOUT)
    parser.add_argument('--total-timeout',type=int,default=agent.TOTAL_TIMEOUT)
    parser.add_argument('--json',action='store_true',help='print the full run as JSON')
    args=parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    result=agent.run_agent(args.question,model=args.model,max_cells=args.max_cells,cell_timeout=args.cell_timeout,total_timeout=args.total_timeout)
    if args.json:print(json.dumps(result.summary(),ensure_ascii=False,indent=1))
    else:
        print(f'[{result.status}] {result.answer or result.error or "Chưa có câu trả lời đã xác minh."}')
        print(f'{len(result.cells)} ô, {result.model_calls} lượt gọi model, {result.seconds} giây')
        print(f'Notebook: {result.notebook}')
    return 0 if result.status=='answered' else 1


if __name__=='__main__':raise SystemExit(main())
