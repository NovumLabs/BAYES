from bayes.models import ExperimentResult
from bayes.verification import verify_sum_of_odds_results


def test_verifier_accepts_correct_record():
    results = [
        ExperimentResult(n=1, observed_sum=1, predicted_value=1, passed=True),
        ExperimentResult(n=2, observed_sum=4, predicted_value=4, passed=True),
        ExperimentResult(n=3, observed_sum=9, predicted_value=9, passed=True),
    ]

    outcome = verify_sum_of_odds_results(results)

    assert outcome["passed"] is True
    assert outcome["failure_count"] == 0


def test_verifier_detects_incorrect_record():
    results = [
        ExperimentResult(n=3, observed_sum=8, predicted_value=9, passed=False),
    ]

    outcome = verify_sum_of_odds_results(results)

    assert outcome["passed"] is False
    assert outcome["failure_count"] == 1
    assert outcome["failures"][0]["expected_value"] == 9
