"""CLI:  python -m qk_norm_blindspot {build|ask|export|verify-models|eval|dashboard}"""
from __future__ import annotations

import argparse
import json
import sys


def main(argv=None) -> int:
    arguments = sys.argv[1:] if argv is None else list(argv)
    if arguments and arguments[0] == "experiment":
        from .experiment_cli import main as experiment_main
        return experiment_main(arguments[1:])
    ap = argparse.ArgumentParser(prog="qk_norm_blindspot")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("experiment", help="Kayıtlı örneklerle run/sweep/list model denemeleri")
    sub.add_parser("build", help="build outputs/*.json from curated evidence and sources")
    a = sub.add_parser("ask", help="answer a question")
    a.add_argument("question")
    a.add_argument("--filters", default=None, help="JSON object")
    a.add_argument("--no-llm", action="store_true")
    sub.add_parser("export", help="write outputs/all_findings.json")
    v = sub.add_parser("verify-models", help="verify pinned checksums of models A, B, C and WT4")
    v.add_argument("--skip-base-weights", action="store_true")
    e = sub.add_parser("eval", help="run software tests only and write outputs/eval_results.json")
    e.add_argument("--no-llm", action="store_true")
    e.add_argument("--compare-base", action="store_true", help="also measure citation validity of the unpatched base model")
    sub.add_parser("dashboard", help="write dashboard/dashboard_data.json")
    args = ap.parse_args(argv)

    if args.cmd == "build":
        from .build import build
        print(json.dumps(build(), indent=2))
    elif args.cmd == "ask":
        from .agent import analyze_blindspots
        f = json.loads(args.filters) if args.filters else None
        print(json.dumps(analyze_blindspots(args.question, f, use_llm=False), indent=2, ensure_ascii=False))
    elif args.cmd == "export":
        from .agent import export_findings
        print(json.dumps(export_findings(), indent=2))
    elif args.cmd == "verify-models":
        from .verify_models import verify_all
        print(json.dumps(verify_all(check_base_weights=not args.skip_base_weights), indent=2))
    elif args.cmd == "eval":
        from .software_eval import run_eval
        report = run_eval()
        print(json.dumps(report, indent=2))
        return report["exit_code"]
    elif args.cmd == "dashboard":
        from .dashboard import write_dashboard_data
        print(json.dumps(write_dashboard_data(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
