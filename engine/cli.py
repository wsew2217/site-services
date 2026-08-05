from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .intake import write_intake_template
from .pipeline import run_deal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m engine",
        description="Generic Site Services deal engine (customer-name-free)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init-template", help="Write a blank intake workbook")
    p_init.add_argument("-o", "--output", default="samples/intake_template.xlsx")

    p_tpl = sub.add_parser("template", help="Alias for init-template")
    p_tpl.add_argument("-o", "--output", default="samples/intake_template.xlsx")

    p_run = sub.add_parser("run", help="Run staffing + cost on an intake workbook")
    p_run.add_argument("intake", help="Path to intake.xlsx")
    p_run.add_argument("-o", "--output", default="Deal_Output.xlsx")
    p_run.add_argument("--json", default=None, help="Optional web summary JSON path")

    args = parser.parse_args(argv)

    if args.cmd in {"init-template", "template"}:
        path = write_intake_template(Path(args.output))
        print(f"Wrote intake template: {path}")
        return 0

    if args.cmd == "run":
        intake = Path(args.intake)
        if not intake.exists():
            print(f"ERROR intake not found: {intake}", file=sys.stderr)
            return 2
        result = run_deal(intake, Path(args.output), Path(args.json) if args.json else None)
        print(json.dumps(result, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
