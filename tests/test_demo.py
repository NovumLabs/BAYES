from bayes.demo import run_demo


def test_demo_passes_for_default_range():
    record = run_demo()

    assert record.status == "supported"
    assert len(record.results) == 10
    assert record.verification["passed"] is True
    assert record.verification["cases_checked"] == 10


def test_demo_supports_custom_range():
    record = run_demo(max_n=25)

    assert record.max_n == 25
    assert len(record.results) == 25
    assert record.results[-1].n == 25


def test_demo_records_finite_test_limitation():
    record = run_demo(max_n=3)

    assert any("finite range" in note for note in record.limitations)
