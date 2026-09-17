from typing import Optional
from sqlmodel import SQLModel, Field


class Payment(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    order_id: int = Field(index=True)

    amount: float

    payment_method: str

    status: str = "pending"

    transaction_id: Optional[str] = None