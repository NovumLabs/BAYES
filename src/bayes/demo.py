"""Deterministic demo experiment for the initial BAYES prototype."""

from .models import ExperimentResult, RunRecord
from .verification import verify_sum_of_odds_results


def run_demo(max_n: int = 10) -> RunRecord:
    """Test the sum-of-odds identity for n=1..max_n and verify recorded results."""
    if max_n < 1:
        raise ValueError("max_n must be at least 1")

    record = RunRecord.create(max_n=max_n)

    for n in range(1, max_n + 1):
        observed_sum = sum(2 * k - 1 for k in range(1, n + 1))
        predicted_value = n * n
        record.results.append(
            ExperimentResult(
                n=n,
                observed_sum=observed_sum,
                predicted_value=predicted_value,
                passed=(observed_sum == predicted_value),
            )
        )

    verification = verify_sum_of_odds_results(record.results)
    record.verification = verification
    record.status = "supported" if verification["passed"] else "rejected"
    return record
