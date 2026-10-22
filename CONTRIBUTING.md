# Contributing to BAYES

Thank you for your interest in BAYES.

## Before contributing
- Open an issue for substantial features or architectural changes.
- Explain the problem, expected behavior, and how success will be evaluated.
- Check that proposed work fits the project's scientific-integrity and safety principles.

## Development setup
```bash
python -m venv .venv
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

## Pull request expectations
- Keep changes focused.
- Add or update tests.
- Document assumptions, edge cases, and limitations.
- Do not commit credentials, private data, or unlicensed material.
- Do not claim scientific novelty or performance improvements without evidence.
- Preserve failed and inconclusive outcomes where relevant.

## Research integrity
A passing finite test is not necessarily a proof. Clearly distinguish test results, formal verification, empirical support, and scientific novelty.
