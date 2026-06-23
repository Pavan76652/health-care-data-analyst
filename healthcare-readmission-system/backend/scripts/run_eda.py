#!/usr/bin/env python
"""Run Phase 4 EDA — generate all visualizations and insights."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analytics.eda import run_full_eda


def main() -> None:
    print("=" * 60)
    print("Phase 4: Exploratory Data Analysis")
    print("=" * 60)

    report = run_full_eda()

    print(f"\nDataset rows:     {report['dataset_rows']:,}")
    print(f"30-day readmit %:   {report['readmission_rate_30_day_pct']}%")
    print(f"Plots saved to:     {report['plots_directory']}")
    print("\nBusiness Insights:")
    print("-" * 60)
    for i, item in enumerate(report["insights"], 1):
        print(f"\n{i}. {item['chart']}")
        print(f"   {item['insight']}")

    print("\nPhase 4 complete.")


if __name__ == "__main__":
    main()
