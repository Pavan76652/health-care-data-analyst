#!/usr/bin/env python
"""Print sample API outputs for project demo."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("HEALTHCARE READMISSION SYSTEM — LIVE API OUTPUT")
print("=" * 60)

print("\n[1] GET /api/v1/health")
print(json.dumps(client.get("/api/v1/health").json(), indent=2))

print("\n[2] GET /api/v1/dashboard — KPIs")
dash = client.get("/api/v1/dashboard").json()
for key, val in dash["kpis"].items():
    print(f"  {key}: {val}")

print("\n[3] GET /api/v1/patients?page=1&page_size=3")
patients = client.get("/api/v1/patients?page=1&page_size=3").json()
print(f"  total_records: {patients['total_records']:,}")
for row in patients["items"]:
    print(f"  - Patient {row['patient_id']} | {row['gender']} | {row['age']} | Risk: {row['risk_tier']} | Readmit: {row['readmitted_flag']}")

print("\n[4] GET /api/v1/analytics — readmission by age (top 3)")
analytics = client.get("/api/v1/analytics").json()
for row in analytics["readmission_by_age"][:3]:
    print(f"  {row['age']}: {row['readmission_rate']}%")

print("\n[5] POST /api/v1/predict — high-risk patient example")
predict = client.post(
    "/api/v1/predict",
    json={
        "age": 72,
        "gender": "Female",
        "diagnosis": "Circulatory_390_459",
        "time_in_hospital": 8,
        "number_of_medications": 20,
        "number_of_procedures": 3,
        "number_inpatient": 3,
        "number_emergency": 2,
        "on_insulin": True,
    },
).json()
print(json.dumps(predict, indent=2))

print("\n[6] Dashboard chart data samples")
charts = dash["charts"]
print(f"  Age groups: {len(charts['readmission_by_age'])}")
print(f"  Monthly trend points: {len(charts['monthly_trends'])}")
print(f"  Top medication: {charts['medication_analysis'][0]['medication_name']}")

print("\n" + "=" * 60)
print("All endpoints OK. Start servers to view UI in browser.")
print("=" * 60)
