# Architecture (initial)

BAYES is organized around a simple research loop:

1. Define a question and a testable hypothesis.
2. Run a controlled computational experiment.
3. preserve a structured run record.
4. Verify the recorded observations using a separate function.
5. Report the result and the scope of the evidence.

## Implemented in version 0.1.0

- CLI entry point.
- Deterministic sum-of-odd-numbers demo.
- JSON run record.
- Separate finite-case verification function.

## Not implemented yet

Autonomous hypothesis generation, literature retrieval, adaptive experiment selection, persistent experiment storage, model-provider integrations, arbitrary code execution, and a general-purpose scientific planner.

Keep component interfaces small and testable as the prototype expands.
