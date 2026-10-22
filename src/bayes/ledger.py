
"""Persistent hypothesis, experiment, and evidence ledger for BAYES."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HYPOTHESIS_STATUSES = {
    "proposed",
    "testing",
    "supported",
    "refuted",
    "inconclusive",
    "archived",
}

EXPERIMENT_OUTCOMES = {
    "supports",
    "contradicts",
    "inconclusive",
    "failed",
    "mixed",
}

EVIDENCE_KINDS = {"positive", "negative", "neutral"}


def _timestamp() -> str:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def _json_text(value: Any, field_name: str) -> str:
    """Validate a value and serialize it as JSON."""
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{field_name} must contain valid JSON-compatible data."
        ) from exc


class ExperimentLedger:
    """SQLite-backed records for hypotheses, experiments, and evidence."""

    def __init__(self, database_path: str | Path = "data/bayes.db") -> None:
        self.database_path = Path(database_path)

        if str(database_path) != ":memory:":
            self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self._connection_path = str(self.database_path)
        self._initialize_database()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._connection_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize_database(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS hypotheses (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS experiments (
                    id TEXT PRIMARY KEY,
                    hypothesis_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    method TEXT NOT NULL,
                    inputs_json TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    notes TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (hypothesis_id)
                        REFERENCES hypotheses(id)
                        ON DELETE RESTRICT
                );

                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    description TEXT NOT NULL,
                    artifact_uri TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (experiment_id)
                        REFERENCES experiments(id)
                        ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_experiments_hypothesis
                    ON experiments(hypothesis_id);

                CREATE INDEX IF NOT EXISTS idx_evidence_experiment
                    ON evidence(experiment_id);
                """
            )

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12].upper()}"

    @staticmethod
    def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None

        result = dict(row)

        for key in ("metadata_json", "inputs_json", "results_json"):
            if key in result:
                json_key = key.removesuffix("_json")
                result[json_key] = json.loads(result.pop(key))

        return result

    def add_hypothesis(
        self,
        title: str,
        statement: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create a hypothesis with the initial status 'proposed'."""
        title = title.strip()
        statement = statement.strip()

        if not title:
            raise ValueError("Hypothesis title cannot be empty.")
        if not statement:
            raise ValueError("Hypothesis statement cannot be empty.")
        if metadata is not None and not isinstance(metadata, dict):
            raise ValueError("Hypothesis metadata must be a dictionary.")

        metadata_json = _json_text(metadata or {}, "metadata")
        now = _timestamp()
        hypothesis_id = self._new_id("HYP")

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO hypotheses
                    (id, title, statement, status, metadata_json,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    hypothesis_id,
                    title,
                    statement,
                    "proposed",
                    metadata_json,
                    now,
                    now,
                ),
            )

        return self.get_hypothesis(hypothesis_id)  # type: ignore[return-value]

    def list_hypotheses(
        self, status: str | None = None
    ) -> list[dict[str, Any]]:
        """List hypotheses, optionally filtering by status."""
        if status is not None and status not in HYPOTHESIS_STATUSES:
            raise ValueError(f"Invalid hypothesis status: {status}")

        with self._connect() as connection:
            if status:
                rows = connection.execute(
                    """
                    SELECT * FROM hypotheses
                    WHERE status = ?
                    ORDER BY created_at DESC
                    """,
                    (status,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM hypotheses ORDER BY created_at DESC"
                ).fetchall()

        return [self._row_to_dict(row) for row in rows]  # type: ignore[misc]

    def get_hypothesis(self, hypothesis_id: str) -> dict[str, Any] | None:
        """Retrieve a hypothesis by ID."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM hypotheses WHERE id = ?",
                (hypothesis_id,),
            ).fetchone()

        return self._row_to_dict(row)

    def set_hypothesis_status(
        self, hypothesis_id: str, status: str
    ) -> dict[str, Any]:
        """Update a hypothesis status."""
        if status not in HYPOTHESIS_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. "
                f"Choose from: {', '.join(sorted(HYPOTHESIS_STATUSES))}"
            )

        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE hypotheses
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (status, _timestamp(), hypothesis_id),
            )

            if cursor.rowcount == 0:
                raise ValueError(f"Hypothesis not found: {hypothesis_id}")

        return self.get_hypothesis(hypothesis_id)  # type: ignore[return-value]

    def add_experiment(
        self,
        hypothesis_id: str,
        name: str,
        method: str,
        inputs: Any = None,
        results: Any = None,
        outcome: str = "inconclusive",
        notes: str = "",
    ) -> dict[str, Any]:
        """Record an experiment linked to an existing hypothesis."""
        name = name.strip()
        method = method.strip()

        if not name:
            raise ValueError("Experiment name cannot be empty.")
        if not method:
            raise ValueError("Experiment method cannot be empty.")
        if outcome not in EXPERIMENT_OUTCOMES:
            raise ValueError(
                f"Invalid experiment outcome: {outcome}"
            )

        inputs_json = _json_text(
            {} if inputs is None else inputs, "inputs"
        )
        results_json = _json_text(
            {} if results is None else results, "results"
        )
        experiment_id = self._new_id("EXP")
        now = _timestamp()

        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM hypotheses WHERE id = ?",
                (hypothesis_id,),
            ).fetchone()

            if exists is None:
                raise ValueError(
                    f"Hypothesis not found: {hypothesis_id}"
                )

            connection.execute(
                """
                INSERT INTO experiments
                    (id, hypothesis_id, name, method, inputs_json,
                     results_json, outcome, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    experiment_id,
                    hypothesis_id,
                    name,
                    method,
                    inputs_json,
                    results_json,
                    outcome,
                    notes,
                    now,
                ),
            )

        return self.get_experiment(experiment_id)  # type: ignore[return-value]

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        """Retrieve an experiment by ID."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM experiments WHERE id = ?",
                (experiment_id,),
            ).fetchone()

        return self._row_to_dict(row)

    def list_experiments(
        self, hypothesis_id: str | None = None
    ) -> list[dict[str, Any]]:
        """List experiments, optionally for one hypothesis."""
        with self._connect() as connection:
            if hypothesis_id:
                rows = connection.execute(
                    """
                    SELECT * FROM experiments
                    WHERE hypothesis_id = ?
                    ORDER BY created_at DESC
                    """,
                    (hypothesis_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM experiments ORDER BY created_at DESC"
                ).fetchall()

        return [self._row_to_dict(row) for row in rows]  # type: ignore[misc]

    def add_evidence(
        self,
        experiment_id: str,
        kind: str,
        description: str,
        artifact_uri: str | None = None,
    ) -> dict[str, Any]:
        """Attach a positive, negative, or neutral evidence record."""
        description = description.strip()

        if kind not in EVIDENCE_KINDS:
            raise ValueError(
                f"Invalid evidence kind: {kind}. "
                f"Choose from: {', '.join(sorted(EVIDENCE_KINDS))}"
            )
        if not description:
            raise ValueError("Evidence description cannot be empty.")

        evidence_id = self._new_id("EVD")
        now = _timestamp()

        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM experiments WHERE id = ?",
                (experiment_id,),
            ).fetchone()

            if exists is None:
                raise ValueError(
                    f"Experiment not found: {experiment_id}"
                )

            connection.execute(
                """
                INSERT INTO evidence
                    (id, experiment_id, kind, description,
                     artifact_uri, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    experiment_id,
                    kind,
                    description,
                    artifact_uri,
                    now,
                ),
            )

        return self.get_evidence(evidence_id)  # type: ignore[return-value]

    def get_evidence(self, evidence_id: str) -> dict[str, Any] | None:
        """Retrieve one evidence record by ID."""
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM evidence WHERE id = ?",
                (evidence_id,),
            ).fetchone()

        return self._row_to_dict(row)

    def list_evidence(
        self, experiment_id: str
    ) -> list[dict[str, Any]]:
        """List evidence attached to an experiment."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM evidence
                WHERE experiment_id = ?
                ORDER BY created_at DESC
                """,
                (experiment_id,),
            ).fetchall()

        return [dict(row) for row in rows]
