
import pytest

from bayes.ledger import ExperimentLedger


@pytest.fixture
def ledger(tmp_path):
    """Give each test its own isolated database."""
    return ExperimentLedger(tmp_path / "test-bayes.db")


def test_add_hypothesis(ledger):
    hypothesis = ledger.add_hypothesis(
        "Odd-number sum identity",
        "The sum of the first n positive odd integers equals n squared.",
    )

    assert hypothesis["id"].startswith("HYP-")
    assert hypothesis["title"] == "Odd-number sum identity"
    assert hypothesis["status"] == "proposed"
    assert hypothesis["metadata"] == {}


def test_hypothesis_persists(ledger):
    hypothesis = ledger.add_hypothesis(
        "Persistence test",
        "A saved hypothesis remains available.",
    )

    retrieved = ledger.get_hypothesis(hypothesis["id"])

    assert retrieved is not None
    assert retrieved["statement"] == (
        "A saved hypothesis remains available."
    )


def test_hypothesis_status_update(ledger):
    hypothesis = ledger.add_hypothesis(
        "Status test",
        "The status can be updated.",
    )

    updated = ledger.set_hypothesis_status(
        hypothesis["id"], "testing"
    )

    assert updated["status"] == "testing"


def test_invalid_hypothesis_status(ledger):
    hypothesis = ledger.add_hypothesis(
        "Invalid status test",
        "An invalid status should be rejected.",
    )

    with pytest.raises(ValueError):
        ledger.set_hypothesis_status(
            hypothesis["id"], "unknown"
        )


def test_add_experiment_and_evidence(ledger):
    hypothesis = ledger.add_hypothesis(
        "Odd-number sum identity",
        "The sum of the first n positive odd integers equals n squared.",
    )

    experiment = ledger.add_experiment(
        hypothesis_id=hypothesis["id"],
        name="Finite numerical check",
        method="Calculate the sum for n = 1 through 100.",
        inputs={"max_n": 100},
        results={"cases_checked": 100, "passed": True},
        outcome="supports",
    )

    assert experiment["id"].startswith("EXP-")
    assert experiment["hypothesis_id"] == hypothesis["id"]
    assert experiment["inputs"] == {"max_n": 100}
    assert experiment["results"]["passed"] is True

    evidence = ledger.add_evidence(
        experiment_id=experiment["id"],
        kind="positive",
        description="All 100 tested cases matched n squared.",
    )

    assert evidence["id"].startswith("EVD-")
    assert evidence["kind"] == "positive"

    evidence_records = ledger.list_evidence(experiment["id"])
    assert len(evidence_records) == 1


def test_experiment_requires_existing_hypothesis(ledger):
    with pytest.raises(ValueError, match="Hypothesis not found"):
        ledger.add_experiment(
            hypothesis_id="HYP-DOES-NOT-EXIST",
            name="Orphan experiment",
            method="Test missing hypothesis handling.",
        )


def test_evidence_requires_existing_experiment(ledger):
    with pytest.raises(ValueError, match="Experiment not found"):
        ledger.add_evidence(
            experiment_id="EXP-DOES-NOT-EXIST",
            kind="neutral",
            description="This experiment does not exist.",
        )


def test_empty_hypothesis_title_is_rejected(ledger):
    with pytest.raises(ValueError, match="title cannot be empty"):
        ledger.add_hypothesis(
            "   ",
            "A hypothesis with an empty title should fail.",
        )


def test_invalid_experiment_outcome_is_rejected(ledger):
    hypothesis = ledger.add_hypothesis(
        "Outcome test",
        "Experiment outcomes must use the defined vocabulary.",
    )

    with pytest.raises(ValueError, match="Invalid experiment outcome"):
        ledger.add_experiment(
            hypothesis_id=hypothesis["id"],
            name="Invalid outcome test",
            method="Validation check",
            outcome="definitely_proven",
        )
