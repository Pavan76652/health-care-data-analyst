#!/usr/bin/env python
"""Run Phase 5 ML training pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ml.config import METRICS_PATH, MODELS_DIR
from app.ml.train import BEST_MODEL_PATH, run_training_pipeline


def main() -> None:
    print("=" * 60)
    print("Phase 5: Machine Learning — Readmission Prediction")
    print("=" * 60)
    print("Target: readmitted within 30 days")
    print("Models: Logistic Regression, Random Forest, XGBoost")
    print("-" * 60)

    summary = run_training_pipeline()

    print("\n" + "=" * 60)
    print("MODEL COMPARISON (Test Set)")
    print("=" * 60)
    print(f"{'Model':<22} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1':>10} {'ROC-AUC':>10}")
    print("-" * 60)
    for name, res in summary["models"].items():
        m = res["test_metrics"]
        marker = " *" if name == summary["best_model"] else ""
        print(
            f"{name:<22} {m['accuracy']:>10.4f} {m['precision']:>10.4f} "
            f"{m['recall']:>10.4f} {m['f1_score']:>10.4f} "
            f"{m.get('roc_auc') or 0:>10.4f}{marker}"
        )

    print("-" * 60)
    print(f"\nBest model: {summary['best_model']} (ROC-AUC: {summary['best_test_roc_auc']:.4f})")
    print(f"Saved to:   {BEST_MODEL_PATH}")
    print(f"Metrics:    {METRICS_PATH}")

    best = summary["models"][summary["best_model"]]
    print("\nTop features (best model):")
    for feat, imp in best["top_features"].items():
        print(f"  {feat}: {imp:.4f}")

    print("\nPhase 5 complete.")


if __name__ == "__main__":
    main()
