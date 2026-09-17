from typing import Optional
from sqlmodel import SQLModel, Field


class Order(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    customer_id: int = Field(index=True)

    product_id: int

    quantity: int = 1

    total_amount: float

    status: str = "processing"

    shipping_address: Optional[str] = None