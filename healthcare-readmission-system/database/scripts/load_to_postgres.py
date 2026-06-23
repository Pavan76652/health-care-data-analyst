#!/usr/bin/env python
"""Load seed CSVs into PostgreSQL using SQLAlchemy (optional helper)."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SEEDS_DIR = PROJECT_ROOT / "database" / "seeds" / "csv"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/healthcare_readmission",
)


def load_table(engine, table: str, csv_file: Path, if_exists: str = "append") -> int:
    df = pd.read_csv(csv_file)
    df.to_sql(table, engine, schema="healthcare", if_exists=if_exists, index=False, method="multi", chunksize=5000)
    return len(df)


def main() -> None:
    engine = create_engine(DATABASE_URL)
    order = [
        ("patients", "patients.csv"),
        ("admissions", "admissions.csv"),
        ("diagnosis", "diagnosis.csv"),
        ("medications", "medications.csv"),
        ("hospital_visits", "hospital_visits.csv"),
    ]

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE healthcare.hospital_visits, healthcare.medications, "
                          "healthcare.diagnosis, healthcare.admissions, healthcare.patients "
                          "RESTART IDENTITY CASCADE"))

    for table, filename in order:
        path = SEEDS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(f"Run generate_seed_data.py first: {path}")
        n = load_table(engine, table, path)
        print(f"Loaded {table}: {n:,} rows")

    print("Database load complete.")


if __name__ == "__main__":
    main()
