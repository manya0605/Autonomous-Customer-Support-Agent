from typing import Optional
from sqlmodel import SQLModel, Field


class Customer(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    name: str

    email: str = Field(
        index=True,
        unique=True
    )

    password_hash: str

    phone: Optional[str] = None

    address: Optional[str] = None

    is_active: bool = True