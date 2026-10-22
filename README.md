# BAYES
### An Autonomous Scientific Discovery Engine
**From Hypothesis to Verified Discovery.**

BAYES is a research and engineering project by Novum Labs to build a structured workflow for hypothesis generation, computational experimentation, independent verification, failure analysis, and reproducible research reporting.

> **Current status:** This repository is an initial, runnable prototype scaffold. It demonstrates a small deterministic hypothesis-testing workflow; it is not yet a general-purpose autonomous scientist.

## What works in this starter

- A command-line interface (`bayes run-demo`).
- A sample mathematical hypothesis: the sum of the first `n` positive odd numbers equals `n²`.
- Finite computational experiments over a configurable range.
- A separate verification step that compares the experiment results against the expected values.
- JSON output for an auditable run record.
- Unit tests for the demo workflow.

The demo verifies a finite set of cases. It does **not** prove the mathematical identity for all positive integers, establish scientific novelty, or demonstrate autonomous discovery.

## Project principles

1. **Test claims:** express a hypothesis in a form that can be evaluated.
2. **Keep evidence:** preserve inputs, outputs, and verification outcomes.
3. **Separate execution from verification:** use a distinct verification step rather than treating a generated result as self-validating.
4. **Report uncertainty honestly:** finite tests support only the cases tested.
5. **Make runs reproducible:** keep configurations and output records.

## Quick start

Requires Python 3.10 or newer.

### 1. Create and activate a virtual environment

**Windows PowerShell**
```powershell
py -3.10 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install the project

From the repository root:
```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 3. Run the demo

```bash
bayes run-demo
```

Run a larger finite test range:
```bash
bayes run-demo --max-n 100
```

Write the run record to a JSON file:
```bash
bayes run-demo --max-n 25 --output reports/demo-run.json
```

### 4. Run tests

```bash
python -m pytest
```

## Example workflow

The demo tests the claim:

> For every positive integer `n`, the sum of the first `n` positive odd numbers equals `n²`.

The program evaluates the first `N` cases and then checks the recorded outputs in a separate verification function. A successful run means only that all tested cases passed. A finite computational test is not a general proof.

## Repository structure

```text
BAYES/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CITATION.cff
├── pyproject.toml
├── .gitignore
├── .env.example
├── src/
│   └── bayes/
│       ├── __init__.py
│       ├── cli.py
│       ├── demo.py
│       ├── models.py
│       └── verification.py
├── tests/
│   ├── test_demo.py
│   └── test_verification.py
├── docs/
│   ├── architecture.md
│   ├── research-methodology.md
│   └── verification-policy.md
├── configs/
│   └── default.json
├── examples/
│   └── README.md
├── benchmarks/
│   └── README.md
├── data/
│   └── README.md
├── artifacts/
│   └── README.md
└── reports/
    └── .gitkeep
```

## Architecture (initial)

```text
Research question
      |
      v
Hypothesis definition
      |
      v
Experiment runner ---> Run record (JSON)
      |                      |
      v                      v
Observed results ---> Independent verification
                             |
                             v
                    Supported / rejected /
                       inconclusive status
```

The current code implements only the small deterministic demo. Components such as autonomous hypothesis generation, literature retrieval, adaptive experiment selection, sandboxed code execution, and model integration are future work.

## Development roadmap

- [x] Initial package structure and command-line entry point
- [x] Deterministic demonstration experiment
- [x] Separate verification function
- [x] JSON run-record output
- [x] Starter unit tests
- [ ] Formal hypothesis and experiment schemas for multiple task types
- [ ] Experiment ledger and persistent run history
- [ ] Pluggable experiment runners
- [ ] More robust independent verification strategies
- [ ] Benchmark suite and baseline comparisons
- [ ] Controlled execution environment for untrusted/generated code
- [ ] Evidence provenance and research report generation
- [ ] Optional model integrations, evaluated separately

Roadmap items are intentions, not claims of existing functionality.

## Safety and research integrity

- Do not execute untrusted or model-generated code on a host machine.
- Add resource limits and isolation before introducing arbitrary code execution.
- Never commit API keys, passwords, private datasets, or other secrets.
- Preserve failed and inconclusive runs.
- Distinguish measured observations from model-generated interpretations.
- Do not claim a result is novel without an appropriate review of prior work.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include tests, document assumptions, and avoid unsupported scientific or performance claims.

## License

This starter includes an MIT license. Review the license and any third-party dependency terms before redistributing or incorporating external code or datasets.

## About

BAYES is an AI research initiative by **Novum Labs Private Limited** focused on building testable, evidence-grounded, and reproducible scientific software.

**BAYES — From Hypothesis to Verified Discovery.**
