#!/usr/bin/env python
"""Run Phase 2 data cleaning pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running as: python backend/scripts/run_cleaning.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.preprocessing import run_preprocessing_pipeline


def main() -> None:
    print("=" * 60)
    print("Phase 2: Healthcare Data Cleaning Pipeline")
    print("=" * 60)

    summary = run_preprocessing_pipeline()

    print(f"\nRaw rows:          {summary['raw_rows']:,}")
    print(f"Cleaned rows:      {summary['cleaned_rows']:,}")
    print(f"Feature matrix:    {summary['feature_matrix_shape']}")
    print(f"30-day readmit %:  {summary['cleaning_stats']['target_positive_rate']}%")
    print(f"\nOutputs:")
    print(f"  Cleaned CSV:     {summary['cleaned_data_path']}")
    print(f"  Quality report:  {summary['quality_report_path']}")
    print(f"  Preprocessor:    {summary['preprocessor_path']}")
    print("\nPhase 2 complete.")


if __name__ == "__main__":
    main()
