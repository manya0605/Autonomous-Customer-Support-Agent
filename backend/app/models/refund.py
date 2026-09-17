from typing import Optional

from sqlmodel import SQLModel, Field


class Refund(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    order_id: int = Field(
        index=True
    )

    customer_id: int = Field(
        index=True
    )

    payment_id: Optional[int] = Field(
        default=None,
        index=True
    )

    amount: float

    reason: str

    status: str = "requested"

    refund_reference: Optional[str] = None