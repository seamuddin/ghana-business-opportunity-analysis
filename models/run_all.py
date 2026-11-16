"""
Rebuild every output in the repository from the input CSVs, in order:

  1. financial_model.py  -> monthly projections, summary metrics, investment breakdown, sensitivity
  2. scoring_model.py    -> screening robustness, criterion scores, weighted ranking, ranking robustness
  3. make_charts.py      -> all PNG charts in visuals/financial-charts/
  4. report_tables.py    -> markdown tables in data/datasets/outputs/tables/ used by the write-up

Usage (from the repository root):
    pip install -r requirements.txt
    python models/run_all.py
"""
from __future__ import annotations

import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent

for script in ("financial_model.py", "scoring_model.py", "make_charts.py", "report_tables.py"):
    print(f"\n=== {script} ===")
    runpy.run_path(str(HERE / script), run_name="__main__")

print("\nAll outputs rebuilt.")
