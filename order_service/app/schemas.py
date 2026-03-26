from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    product: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class OrderResponse(BaseModel):
    id: int
    status: str


class OrderDetailsResponse(BaseModel):
    id: int
    customer_id: str
    product: str
    quantity: int
    status: str
    created_at: datetime
