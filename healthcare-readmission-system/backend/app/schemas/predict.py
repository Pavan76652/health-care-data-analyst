from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    age: int = Field(..., ge=0, le=110, description="Patient age in years")
    gender: str = Field(..., description="Male/Female/Other")
    diagnosis: str = Field(..., description="Primary diagnosis group or ICD-like label")
    time_in_hospital: int = Field(..., ge=1, le=14)
    number_of_medications: int = Field(..., ge=0, le=100)
    number_of_procedures: int = Field(..., ge=0, le=20)

    race: str = Field(default="Unknown")
    number_outpatient: int = Field(default=0, ge=0)
    number_emergency: int = Field(default=0, ge=0)
    number_inpatient: int = Field(default=0, ge=0)
    number_diagnoses: int = Field(default=3, ge=1, le=20)
    num_lab_procedures: int = Field(default=40, ge=0, le=200)
    admission_type_id: int = Field(default=1, ge=1, le=30)
    discharge_disposition_id: int = Field(default=1, ge=1, le=40)
    admission_source_id: int = Field(default=7, ge=1, le=30)
    on_insulin: bool = Field(default=False)
    diabetes_med: bool = Field(default=True)


class PredictResponse(BaseModel):
    readmission_probability: float
    risk_score: float
    risk_level: str
    recommendation: str
    top_risk_factors: list[str]
