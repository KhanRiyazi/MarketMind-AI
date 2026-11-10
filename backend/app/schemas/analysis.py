from pydantic import BaseModel, Field


class IPORequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    price_high: float = Field(gt=0)
    lot_size: int = Field(gt=0)
    eps: float
    peer_pe: float = Field(gt=0)
    gmp: float = 0
    subscription_x: float = Field(0, ge=0)
