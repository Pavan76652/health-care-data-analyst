from fastapi import APIRouter, HTTPException, Query

from app.schemas.predict import PredictRequest, PredictResponse
from app.services.data_service import (
    get_analytics_summary,
    get_dashboard_payload,
    get_patients,
)
from app.services.prediction_service import predict

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/patients")
def patients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
    search: str | None = Query(default=None),
) -> dict:
    return get_patients(page=page, page_size=page_size, search=search)


@router.get("/analytics")
def analytics() -> dict:
    return get_analytics_summary()


@router.get("/dashboard")
def dashboard() -> dict:
    return get_dashboard_payload()


@router.post("/predict", response_model=PredictResponse)
def predict_readmission(payload: PredictRequest) -> PredictResponse:
    try:
        result = predict(payload)
        return PredictResponse(**result)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc
