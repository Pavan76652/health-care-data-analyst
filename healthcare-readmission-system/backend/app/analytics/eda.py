"""Exploratory data analysis utilities and plot generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CLEANED_CSV = PROJECT_ROOT / "data" / "processed" / "cleaned_data.csv"
PLOTS_DIR = PROJECT_ROOT / "reports" / "eda_plots"
INSIGHTS_JSON = PROJECT_ROOT / "reports" / "eda_insights.json"

MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide",
    "glimepiride", "acetohexamide", "glipizide", "glyburide", "tolbutamide",
    "pioglitazone", "rosiglitazone", "acarbose", "miglitol", "troglitazone",
    "tolazamide", "examide", "citoglipton", "insulin",
    "glyburide-metformin", "glipizide-metformin", "glimepiride-pioglitazone",
    "metformin-rosiglitazone", "metformin-pioglitazone",
]

AGE_ORDER = [
    "[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)",
    "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)",
]

PALETTE = {"NO": "#2ecc71", ">30": "#f39c12", "<30": "#e74c3c"}
READMIT_PALETTE = {0: "#3498db", 1: "#e74c3c"}


def load_eda_data(path: Path | str | None = None) -> pd.DataFrame:
    df = pd.read_csv(path or CLEANED_CSV)
    if "age" in df.columns:
        df["age"] = pd.Categorical(df["age"], categories=AGE_ORDER, ordered=True)
    return df


def _save_fig(fig: plt.Figure, name: str, plots_dir: Path) -> Path:
    plots_dir.mkdir(parents=True, exist_ok=True)
    out = plots_dir / f"{name}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def plot_age_distribution(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    counts = df["age"].value_counts().reindex(AGE_ORDER, fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(range(len(counts)), counts.values, color="#3498db", edgecolor="white")
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(AGE_ORDER, rotation=45, ha="right")
    ax.set_title("Age Distribution of Hospital Admissions", fontsize=14, fontweight="bold")
    ax.set_xlabel("Age Bracket")
    ax.set_ylabel("Number of Admissions")
    for bar, val in zip(bars, counts.values):
        if val > 5000:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{val:,}",
                    ha="center", va="bottom", fontsize=8)
    path = _save_fig(fig, "01_age_distribution", plots_dir)

    peak_age = counts.idxmax()
    pct_60_plus = counts[counts.index.isin(AGE_ORDER[6:])].sum() / len(df) * 100
    insight = {
        "chart": "Age Distribution",
        "peak_bracket": str(peak_age),
        "peak_count": int(counts.max()),
        "pct_age_60_plus": round(pct_60_plus, 1),
        "insight": (
            f"Admissions peak in the {peak_age} bracket ({counts.max():,} encounters). "
            f"Patients aged 60+ account for {pct_60_plus:.1f}% of all admissions, "
            "reflecting the elderly-heavy diabetic inpatient population typical of US hospitals."
        ),
    }
    return insight


def plot_gender_distribution(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    counts = df["gender"].value_counts()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].pie(counts, labels=counts.index, autopct="%1.1f%%",
                colors=["#9b59b6", "#3498db"], startangle=90)
    axes[0].set_title("Gender Distribution", fontweight="bold")

    readmit_by_gender = df.groupby("gender")["readmitted_30_days"].mean() * 100
    axes[1].bar(readmit_by_gender.index, readmit_by_gender.values,
                color=["#9b59b6", "#3498db"], edgecolor="white")
    axes[1].set_title("30-Day Readmission Rate by Gender", fontweight="bold")
    axes[1].set_ylabel("Readmission Rate (%)")
    axes[1].axhline(df["readmitted_30_days"].mean() * 100, color="red",
                    linestyle="--", label="Overall avg")
    axes[1].legend()

    path = _save_fig(fig, "02_gender_distribution", plots_dir)
    female_pct = counts.get("Female", 0) / len(df) * 100
    insight = {
        "chart": "Gender Distribution",
        "female_pct": round(female_pct, 1),
        "readmit_rate_female": round(readmit_by_gender.get("Female", 0), 2),
        "readmit_rate_male": round(readmit_by_gender.get("Male", 0), 2),
        "insight": (
            f"Females represent {female_pct:.1f}% of admissions. "
            f"30-day readmission rates: Female {readmit_by_gender.get('Female', 0):.2f}% vs "
            f"Male {readmit_by_gender.get('Male', 0):.2f}%. "
            "Gender differences are modest; age and prior utilization are stronger predictors."
        ),
    }
    return insight


def plot_readmission_trends(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    outcome_counts = df["readmitted"].value_counts().reindex(["NO", ">30", "<30"])
    axes[0].bar(outcome_counts.index, outcome_counts.values,
                color=[PALETTE[k] for k in outcome_counts.index], edgecolor="white")
    axes[0].set_title("Readmission Outcomes (All Categories)", fontweight="bold")
    axes[0].set_ylabel("Count")
    for i, v in enumerate(outcome_counts.values):
        axes[0].text(i, v, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", va="bottom", fontsize=9)

    age_readmit = (
        df.groupby("age", observed=True)["readmitted_30_days"]
        .agg(["mean", "count"])
        .reindex(AGE_ORDER)
    )
    ax2 = axes[1]
    ax2.bar(range(len(age_readmit)), age_readmit["mean"] * 100, color="#e74c3c", alpha=0.8)
    ax2.set_xticks(range(len(age_readmit)))
    ax2.set_xticklabels(AGE_ORDER, rotation=45, ha="right")
    ax2.set_title("30-Day Readmission Rate by Age", fontweight="bold")
    ax2.set_ylabel("Readmission Rate (%)")

    path = _save_fig(fig, "03_readmission_trends", plots_dir)
    rate_30 = df["readmitted_30_days"].mean() * 100
    worst_age = age_readmit["mean"].idxmax()
    insight = {
        "chart": "Readmission Trends",
        "readmit_30_day_rate": round(rate_30, 2),
        "readmit_after_30_rate": round((df["readmitted"] == ">30").mean() * 100, 2),
        "highest_risk_age": str(worst_age),
        "insight": (
            f"Overall 30-day readmission rate is {rate_30:.2f}% — a key CMS penalty metric. "
            f"An additional {(df['readmitted'] == '>30').mean() * 100:.1f}% are readmitted after 30 days. "
            f"Highest-risk age bracket: {worst_age}. "
            "Hospitals should target discharge planning for elderly high-utilization patients."
        ),
    }
    return insight


def plot_diagnosis_analysis(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    diag = (
        df.groupby("diag_1_group")
        .agg(admissions=("readmitted_30_days", "count"),
             readmit_rate=("readmitted_30_days", "mean"))
        .query("admissions >= 500")
        .sort_values("admissions", ascending=False)
        .head(10)
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].barh(diag.index[::-1], diag["admissions"][::-1], color="#1abc9c")
    axes[0].set_title("Top 10 Primary Diagnosis Groups (Volume)", fontweight="bold")
    axes[0].set_xlabel("Admissions")

    top_rate = (
        df.groupby("diag_1_group")
        .agg(admissions=("readmitted_30_days", "count"),
             readmit_rate=("readmitted_30_days", "mean"))
        .query("admissions >= 1000")
        .sort_values("readmit_rate", ascending=False)
        .head(8)
    )
    axes[1].barh(top_rate.index[::-1], (top_rate["readmit_rate"] * 100)[::-1], color="#e67e22")
    axes[1].set_title("Highest Readmission Rate by Diagnosis (≥1000 cases)", fontweight="bold")
    axes[1].set_xlabel("30-Day Readmission Rate (%)")

    path = _save_fig(fig, "04_diagnosis_analysis", plots_dir)
    top_diag = diag.index[0]
    top_rate_diag = top_rate.index[0]
    insight = {
        "chart": "Diagnosis Analysis",
        "top_volume_diagnosis": top_diag,
        "top_volume_count": int(diag["admissions"].iloc[0]),
        "highest_readmit_diagnosis": top_rate_diag,
        "highest_readmit_rate": round(top_rate["readmit_rate"].iloc[0] * 100, 2),
        "insight": (
            f"{top_diag} is the most common primary diagnosis ({int(diag['admissions'].iloc[0]):,} cases). "
            f"{top_rate_diag} has the highest readmission rate ({top_rate['readmit_rate'].iloc[0]*100:.1f}%) "
            "among high-volume groups. Care pathways for circulatory and diabetes complications "
            "should be prioritized for readmission reduction programs."
        ),
    }
    return insight


def plot_length_of_stay(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    los_counts = df["time_in_hospital"].value_counts().sort_index()
    axes[0].bar(los_counts.index, los_counts.values, color="#8e44ad", edgecolor="white")
    axes[0].set_title("Length of Stay Distribution", fontweight="bold")
    axes[0].set_xlabel("Days in Hospital")
    axes[0].set_ylabel("Admissions")

    los_readmit = df.groupby("time_in_hospital")["readmitted_30_days"].mean() * 100
    axes[1].plot(los_readmit.index, los_readmit.values, marker="o", color="#e74c3c", linewidth=2)
    axes[1].fill_between(los_readmit.index, los_readmit.values, alpha=0.2, color="#e74c3c")
    axes[1].set_title("Readmission Rate vs Length of Stay", fontweight="bold")
    axes[1].set_xlabel("Days in Hospital")
    axes[1].set_ylabel("30-Day Readmission Rate (%)")
    axes[1].axhline(df["readmitted_30_days"].mean() * 100, color="gray", linestyle="--")

    path = _save_fig(fig, "05_length_of_stay", plots_dir)
    avg_los = df["time_in_hospital"].mean()
    los_readmit_corr = df["time_in_hospital"].corr(df["readmitted_30_days"])
    insight = {
        "chart": "Length of Stay Analysis",
        "avg_los_days": round(avg_los, 2),
        "median_los_days": float(df["time_in_hospital"].median()),
        "los_readmit_correlation": round(los_readmit_corr, 3),
        "insight": (
            f"Average length of stay is {avg_los:.1f} days (median {df['time_in_hospital'].median():.0f}). "
            f"LOS-readmission correlation is {los_readmit_corr:.3f}. "
            "Longer stays often indicate clinical complexity; extended stays beyond 7 days "
            "warrant enhanced discharge planning and home health coordination."
        ),
    }
    return insight


def plot_medication_analysis(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    active_meds = {}
    for col in MEDICATION_COLUMNS:
        if col in df.columns:
            active_meds[col] = df[col].isin(["Steady", "Up", "Down"]).sum()
    med_series = pd.Series(active_meds).sort_values(ascending=False).head(10)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].barh(med_series.index[::-1], med_series.values[::-1], color="#16a085")
    axes[0].set_title("Top 10 Active Medications", fontweight="bold")
    axes[0].set_xlabel("Active Prescriptions")

    med_bins = pd.cut(df["num_medications"], bins=[0, 5, 10, 15, 20, 100],
                       labels=["1-5", "6-10", "11-15", "16-20", "21+"])
    med_readmit = df.groupby(med_bins, observed=True)["readmitted_30_days"].mean() * 100
    axes[1].bar(med_readmit.index.astype(str), med_readmit.values, color="#d35400", edgecolor="white")
    axes[1].set_title("Readmission Rate by Medication Count", fontweight="bold")
    axes[1].set_xlabel("Number of Medications")
    axes[1].set_ylabel("30-Day Readmission Rate (%)")

    path = _save_fig(fig, "06_medication_analysis", plots_dir)
    insulin_rate = df.groupby("on_insulin")["readmitted_30_days"].mean()
    insight = {
        "chart": "Medication Analysis",
        "top_medication": med_series.index[0],
        "top_med_count": int(med_series.iloc[0]),
        "avg_medications": round(df["num_medications"].mean(), 1),
        "insulin_readmit_rate": round(insulin_rate.get("Yes", 0) * 100, 2),
        "no_insulin_readmit_rate": round(insulin_rate.get("No", 0) * 100, 2),
        "insight": (
            f"{med_series.index[0]} is the most frequently active medication ({int(med_series.iloc[0]):,} cases). "
            f"Patients on insulin have a {insulin_rate.get('Yes', 0)*100:.1f}% readmission rate vs "
            f"{insulin_rate.get('No', 0)*100:.1f}% without insulin, indicating insulin use as a "
            "complexity marker. Polypharmacy (16+ meds) correlates with elevated readmission risk."
        ),
    }
    return insight


def plot_correlation_heatmap(df: pd.DataFrame, plots_dir: Path) -> dict[str, Any]:
    numeric_cols = [
        "age_midpoint", "time_in_hospital", "num_lab_procedures", "num_procedures",
        "num_medications", "number_outpatient", "number_emergency", "number_inpatient",
        "number_diagnoses", "total_prior_visits", "active_medication_count",
        "readmitted_30_days",
    ]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available].corr()

    fig, ax = plt.subplots(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    sns.heatmap(
        corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
        center=0, square=True, linewidths=0.5, ax=ax, vmin=-1, vmax=1,
    )
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold")
    path = _save_fig(fig, "07_correlation_heatmap", plots_dir)

    target_corr = corr["readmitted_30_days"].drop("readmitted_30_days").abs().sort_values(ascending=False)
    top_predictor = target_corr.index[0]
    insight = {
        "chart": "Correlation Heatmap",
        "strongest_predictor": top_predictor,
        "strongest_correlation": round(target_corr.iloc[0], 3),
        "top_3_predictors": {k: round(v, 3) for k, v in target_corr.head(3).items()},
        "insight": (
            f"Strongest correlation with 30-day readmission: {top_predictor} "
            f"(r={target_corr.iloc[0]:.3f}). "
            "Prior utilization (inpatient/emergency visits) and medication count cluster together, "
            "confirming that high-utilization diabetic patients are the primary readmission risk cohort. "
            "These features should be weighted heavily in the ML model."
        ),
    }
    return insight


def run_full_eda(
    data_path: Path | str | None = None,
    plots_dir: Path | str | None = None,
) -> dict[str, Any]:
    """Generate all EDA plots and business insights."""
    sns.set_theme(style="whitegrid", palette="muted")
    df = load_eda_data(data_path)
    out_dir = Path(plots_dir) if plots_dir else PLOTS_DIR

    insights = [
        plot_age_distribution(df, out_dir),
        plot_gender_distribution(df, out_dir),
        plot_readmission_trends(df, out_dir),
        plot_diagnosis_analysis(df, out_dir),
        plot_length_of_stay(df, out_dir),
        plot_medication_analysis(df, out_dir),
        plot_correlation_heatmap(df, out_dir),
    ]

    report = {
        "dataset_rows": len(df),
        "readmission_rate_30_day_pct": round(df["readmitted_30_days"].mean() * 100, 2),
        "plots_directory": str(out_dir),
        "insights": insights,
    }

    INSIGHTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(INSIGHTS_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report
