from typing import Optional
from sqlmodel import SQLModel, Field


class ReturnRequest(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    order_id: int = Field(index=True)

    customer_id: int = Field(index=True)

    reason: str

    status: str = "requested"

    refund_amount: Optional[float] = None