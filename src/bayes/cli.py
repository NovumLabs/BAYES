
"""Command-line interface for BAYES."""

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .demo import run_demo
from .ledger import ExperimentLedger


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bayes",
        description="BAYES scientific experimentation and verification prototype.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Existing demo command
    demo = subparsers.add_parser(
        "run-demo",
        help="Run the finite sum-of-odds demo.",
    )
    demo.add_argument("--max-n", type=int, default=10)
    demo.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the JSON run record.",
    )

    demo.add_argument(
    "--hypothesis-id",
    help="Optional hypothesis ID to link the run to the experiment ledger.",
    )
    # Hypothesis commands
    hypothesis = subparsers.add_parser(
        "hypothesis",
        help="Manage scientific hypotheses.",
    )
    hypothesis_commands = hypothesis.add_subparsers(
        dest="hypothesis_action",
        required=True,
    )

    hypothesis_add = hypothesis_commands.add_parser(
        "add",
        help="Register a hypothesis.",
    )
    hypothesis_add.add_argument("--title", required=True)
    hypothesis_add.add_argument("--statement", required=True)

    hypothesis_list = hypothesis_commands.add_parser(
        "list",
        help="List hypotheses.",
    )
    hypothesis_list.add_argument(
        "--status",
        choices=[
            "proposed", "testing", "supported",
            "refuted", "inconclusive", "archived",
        ],
    )

    hypothesis_show = hypothesis_commands.add_parser(
        "show",
        help="Show a hypothesis by ID.",
    )
    hypothesis_show.add_argument("hypothesis_id")

    hypothesis_status = hypothesis_commands.add_parser(
        "set-status",
        help="Update a hypothesis status.",
    )
    hypothesis_status.add_argument("hypothesis_id")
    hypothesis_status.add_argument(
        "--status",
        required=True,
        choices=[
            "proposed", "testing", "supported",
            "refuted", "inconclusive", "archived",
        ],
    )

    # Experiment commands
    experiment = subparsers.add_parser(
        "experiment",
        help="Manage experiments.",
    )
    experiment_commands = experiment.add_subparsers(
        dest="experiment_action",
        required=True,
    )

    experiment_add = experiment_commands.add_parser(
        "add",
        help="Record an experiment.",
    )
    experiment_add.add_argument("--hypothesis-id", required=True)
    experiment_add.add_argument("--name", required=True)
    experiment_add.add_argument("--method", required=True)
    experiment_add.add_argument(
        "--inputs-json",
        default="{}",
        help="Experiment inputs as a JSON object or value.",
    )
    experiment_add.add_argument(
        "--results-json",
        default="{}",
        help="Experiment results as a JSON object or value.",
    )
    experiment_add.add_argument(
        "--outcome",
        default="inconclusive",
        choices=[
            "supports", "contradicts", "inconclusive", "failed", "mixed",
        ],
    )
    experiment_add.add_argument("--notes", default="")

    experiment_list = experiment_commands.add_parser(
        "list",
        help="List experiments.",
    )
    experiment_list.add_argument("--hypothesis-id")

    # Evidence commands
    evidence = subparsers.add_parser(
        "evidence",
        help="Manage evidence records.",
    )
    evidence_commands = evidence.add_subparsers(
        dest="evidence_action",
        required=True,
    )

    evidence_add = evidence_commands.add_parser(
        "add",
        help="Attach evidence to an experiment.",
    )
    evidence_add.add_argument("--experiment-id", required=True)
    evidence_add.add_argument(
        "--kind",
        required=True,
        choices=["positive", "negative", "neutral"],
    )
    evidence_add.add_argument("--description", required=True)
    evidence_add.add_argument("--artifact-uri")

    evidence_list = evidence_commands.add_parser(
        "list",
        help="List evidence for an experiment.",
    )
    evidence_list.add_argument("--experiment-id", required=True)

    return parser


def _print_json(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _parse_json_argument(value: str, argument_name: str):
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{argument_name} must be valid JSON: {exc.msg}"
        ) from exc


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
                # Run the deterministic demo and optionally record it in the ledger.
        if args.command == "run-demo":
            if args.max_n < 1:
                parser.error("--max-n must be at least 1")

            record = run_demo(max_n=args.max_n)
            run_data = record.to_dict()
            rendered = json.dumps(run_data, indent=2, ensure_ascii=False)

            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(
                    rendered + "\n",
                    encoding="utf-8",
                )
                print(f"Run record written to: {args.output}")
            else:
                print(rendered)

            if args.hypothesis_id:
                ledger = ExperimentLedger("data/bayes.db")

                passed = bool(record.verification.get("passed"))
                outcome = "supports" if passed else "contradicts"

                experiment = ledger.add_experiment(
                    hypothesis_id=args.hypothesis_id,
                    name="Finite numerical check",
                    method=(
                        f"Test the sum-of-odds identity for "
                        f"positive integers n=1 through {args.max_n}."
                    ),
                    inputs={"max_n": args.max_n},
                    results=run_data,
                    outcome=outcome,
                    notes=(
                        "Finite numerical verification only; "
                        "not a general mathematical proof."
                    ),
                )

                evidence_kind = "positive" if passed else "negative"
                verification = record.verification
                cases_checked = verification.get("cases_checked", 0)
                failure_count = verification.get("failure_count", 0)

                ledger.add_evidence(
                    experiment_id=experiment["id"],
                    kind=evidence_kind,
                    description=(
                        f"Demo verification: {cases_checked} cases checked; "
                        f"{failure_count} failures; passed={passed}."
                    ),
                    artifact_uri=(
                        str(args.output.resolve()) if args.output else None
                    ),
                )

                print("\nExperiment and evidence saved to ledger:")
                print(f"Experiment ID: {experiment['id']}")
                print(f"Evidence type: {evidence_kind}")

            print(f"\nBAYES status: {record.status}")
            return 0 if record.verification.get("passed") else 1

        # Use a local SQLite database unless otherwise configured.
        ledger = ExperimentLedger("data/bayes.db")

        if args.command == "hypothesis":
            if args.hypothesis_action == "add":
                result = ledger.add_hypothesis(
                    title=args.title,
                    statement=args.statement,
                )
                _print_json(result)
                return 0

            if args.hypothesis_action == "list":
                _print_json(ledger.list_hypotheses(status=args.status))
                return 0

            if args.hypothesis_action == "show":
                result = ledger.get_hypothesis(args.hypothesis_id)
                if result is None:
                    print(
                        f"Hypothesis not found: {args.hypothesis_id}",
                        file=sys.stderr,
                    )
                    return 1
                _print_json(result)
                return 0

            if args.hypothesis_action == "set-status":
                _print_json(
                    ledger.set_hypothesis_status(
                        args.hypothesis_id,
                        args.status,
                    )
                )
                return 0

        if args.command == "experiment":
            if args.experiment_action == "add":
                inputs = _parse_json_argument(
                    args.inputs_json, "--inputs-json"
                )
                results = _parse_json_argument(
                    args.results_json, "--results-json"
                )

                result = ledger.add_experiment(
                    hypothesis_id=args.hypothesis_id,
                    name=args.name,
                    method=args.method,
                    inputs=inputs,
                    results=results,
                    outcome=args.outcome,
                    notes=args.notes,
                )
                _print_json(result)
                return 0

            if args.experiment_action == "list":
                _print_json(
                    ledger.list_experiments(
                        hypothesis_id=args.hypothesis_id
                    )
                )
                return 0

        if args.command == "evidence":
            if args.evidence_action == "add":
                result = ledger.add_evidence(
                    experiment_id=args.experiment_id,
                    kind=args.kind,
                    description=args.description,
                    artifact_uri=args.artifact_uri,
                )
                _print_json(result)
                return 0

            if args.evidence_action == "list":
                _print_json(
                    ledger.list_evidence(args.experiment_id)
                )
                return 0

    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    return 2


if __name__ == "__main__":
    sys.exit(main())
