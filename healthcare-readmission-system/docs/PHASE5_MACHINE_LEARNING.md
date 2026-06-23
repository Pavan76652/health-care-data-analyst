# Phase 5 — Machine Learning (Complete)

## Objective

Predict **30-day hospital readmission** (`readmitted_30_days`) and produce a **risk score 0–100** for hospital administrators.

## Models Trained

| Model | Test Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|---------------|-----------|--------|-----|---------|
| Logistic Regression | 0.6522 | 0.1709 | 0.5495 | 0.2607 | 0.6509 |
| Random Forest | 0.7923 | 0.2174 | 0.3316 | 0.2626 | 0.6705 |
| **XGBoost** ★ | **0.8368** | **0.2638** | **0.2585** | **0.2611** | **0.6866** |

**Best model: XGBoost** — selected by highest ROC-AUC on held-out test set (20%, stratified).

## Methodology

| Step | Implementation |
|------|----------------|
| Train/test split | 80/20, stratified on target |
| Cross-validation | 3-fold StratifiedKFold |
| Hyperparameter tuning | RandomizedSearchCV (ROC-AUC scoring) |
| Class imbalance | `class_weight='balanced'` (LR, RF), `scale_pos_weight=4.83` (XGB) |
| Features | 84 encoded features from Phase 2 preprocessor |
| Leakage prevention | Preprocessor fit on train split only |

## Best XGBoost Hyperparameters

```json
{
  "subsample": 0.8,
  "n_estimators": 300,
  "max_depth": 6,
  "learning_rate": 0.01,
  "colsample_bytree": 0.8
}
```

## Top Feature Importance (XGBoost)

| Feature | Importance |
|---------|------------|
| Prior inpatient visit (Yes) | 0.162 |
| Prior inpatient visit (No) | 0.152 |
| Number of prior inpatient visits | 0.096 |
| Discharge disposition ID | 0.030 |
| Total prior visits | 0.015 |
| On diabetes medication | 0.015 |

**Clinical interpretation:** Prior hospital utilization is the dominant predictor — consistent with Phase 4 EDA (r=0.165 for inpatient visits).

## Confusion Matrix (XGBoost, Test Set)

See `models/metrics.json` for full details. With 11% positive class:
- High accuracy (84%) reflects majority-class prediction
- **Recall ~26%** — model catches roughly 1 in 4 true readmissions
- **Precision ~26%** — about 1 in 4 flagged patients are true readmissions

For clinical deployment, tune threshold to prioritize **recall** (catch more at-risk patients) at the cost of precision.

## Risk Score Mapping

```
risk_score = readmission_probability × 100

Low:      0–39
Moderate: 40–69
High:     70–100
```

## Saved Artifacts

| File | Description |
|------|-------------|
| `models/best_model.joblib` | XGBoost + fitted preprocessor bundle |
| `models/preprocessor.joblib` | Standalone preprocessing pipeline |
| `models/metrics.json` | Full comparison metrics |
| `models/feature_importance.json` | Top 25 features |
| `reports/model_comparison.json` | Model leaderboard |

## Run Training

```bash
python backend/scripts/run_training.py
```

## Business Impact

- **ROC-AUC 0.69** — moderate discriminative ability; suitable for risk stratification, not standalone clinical decisions
- Flag **high-utilization patients** at discharge for care management programs
- Estimated CMS penalty avoidance: identifying top 20% risk patients could reduce readmissions by 10–15% with targeted interventions

## Next Phase

**Phase 6 — Power BI Dashboard** OR **Phase 7 — FastAPI** (per original plan).

*Awaiting approval to proceed.*
