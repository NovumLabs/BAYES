"""Verification routines kept separate from the demonstration experiment."""

from collections.abc import Sequence
from typing import Any

from .models import ExperimentResult


def verify_sum_of_odds_results(
    results: Sequence[ExperimentResult],
) -> dict[str, Any]:
    """Check recorded cases against a separately computed expected value.

    This is an independent check of the recorded finite cases, not a proof
    of the identity for all positive integers.
    """
    failures: list[dict[str, int]] = []

    for result in results:
        expected = result.n * result.n
        if result.observed_sum != expected or result.predicted_value != expected:
            failures.append(
                {
                    "n": result.n,
                    "observed_sum": result.observed_sum,
                    "predicted_value": result.predicted_value,
                    "expected_value": expected,
                }
            )

    return {
        "method": "recompute_expected_square_for_each_recorded_case",
        "cases_checked": len(results),
        "passed": len(failures) == 0,
        "failure_count": len(failures),
        "failures": failures,
        "scope_note": "Verification covers only the supplied finite cases.",
    }
