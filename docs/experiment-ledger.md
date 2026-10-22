\# BAYES Experiment Ledger



\## Overview



BAYES is a prototype for recording hypotheses, experiments, and supporting evidence in a local SQLite database.



\## Current Capabilities



\- Create, list, and inspect hypotheses.

\- Update hypothesis status.

\- Record experiments linked to existing hypotheses.

\- Store experiment inputs and results as JSON.

\- Record positive, negative, or neutral evidence.

\- Associate evidence with an experiment.

\- Run a deterministic numerical demonstration and optionally save its results to the experiment ledger.



\## Demonstration



The initial demonstration checks the identity



\\\[

1+3+5+\\cdots +(2n-1)=n^2

\\]



for positive integers from \\(n=1\\) through a configurable maximum.



Example:



```powershell

bayes run-demo --max-n 100 --hypothesis-id HYP-6C0225AA0D90 --output reports/bayes-ledger-run.json

```



The command produces a JSON run report and, when a hypothesis ID is provided, records an experiment and associated evidence in the SQLite ledger.



\## Verification and Limitations



The prototype's demonstration verifies the recorded cases against the expected square values. A passing finite numerical test does not constitute a general mathematical proof or establish scientific novelty.



The SQLite database and generated run report are local runtime artifacts and should remain excluded from ordinary source-control commits.



\## Tests



Run the test suite with:



```powershell

python -m pytest -q

```



The initial test suite contains 14 tests covering the demo, ledger, and verification functionality.



\## Project Status



This is an early prototype. Its current capabilities should not be interpreted as a validated autonomous scientific discovery system.



