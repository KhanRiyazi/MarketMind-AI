from pydantic import BaseModel, Field


class SIPRequest(BaseModel):
    monthly: float = Field(gt=0, le=10_000_000)
    years: int = Field(ge=1, le=50)
    annual_return: float = Field(0.12, gt=-0.5, le=0.5, description="e.g. 0.12 for 12%")
    step_up: float = Field(0.0, ge=0, le=0.5)
    inflation: float = Field(0.06, ge=0, le=0.3)


class GoalRequest(BaseModel):
    target: float = Field(gt=0)
    years: int = Field(ge=1, le=50)
    annual_return: float = Field(0.12, gt=-0.5, le=0.5)
    step_up: float = Field(0.0, ge=0, le=0.5)


class BacktestRequest(BaseModel):
    scheme_code: int
    monthly: float = Field(gt=0)
    years: int = Field(ge=1, le=20)
