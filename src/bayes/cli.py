"""Command-line interface for BAYES."""

import argparse
import json
from pathlib import Path
import sys

from . import __version__
from .demo import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bayes",
        description="BAYES scientific experimentation and verification prototype.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo = subparsers.add_parser("run-demo", help="Run the finite sum-of-odds demo.")
    demo.add_argument(
        "--max-n",
        type=int,
        default=10,
        help="Test n=1 through max-n (default: 10).",
    )
    demo.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the JSON run record.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run-demo":
        if args.max_n < 1:
            parser.error("--max-n must be at least 1")

        record = run_demo(max_n=args.max_n)
        rendered = json.dumps(record.to_dict(), indent=2)

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
            print(f"Run record written to: {args.output}")
        else:
            print(rendered)

        print(f"\nBAYES status: {record.status}")
        return 0 if record.verification.get("passed") else 1

    return 2


if __name__ == "__main__":
    sys.exit(main())
