"""Small typed data structures used by the starter workflow."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ExperimentResult:
    """Result of evaluating one input case."""

    n: int
    observed_sum: int
    predicted_value: int
    passed: bool


@dataclass
class RunRecord:
    """Serializable record of one prototype run."""

    project: str
    version: str
    hypothesis: str
    max_n: int
    started_at_utc: str
    status: str
    results: list[ExperimentResult] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    @classmethod
    def create(cls, max_n: int) -> "RunRecord":
        return cls(
            project="BAYES",
            version="0.1.0",
            hypothesis="The sum of the first n positive odd integers equals n squared.",
            max_n=max_n,
            started_at_utc=datetime.now(timezone.utc).isoformat(),
            status="pending",
            limitations=[
                "This run tests only a finite range of positive integers.",
                "Passing finite tests does not constitute a general mathematical proof.",
                "This demonstration does not establish scientific novelty.",
            ],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
