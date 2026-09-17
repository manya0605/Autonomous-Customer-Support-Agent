from typing import Optional
from sqlmodel import SQLModel, Field


class SupportTicket(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    customer_id: int = Field(index=True)

    subject: str

    description: str

    category: str

    priority: str = "medium"

    status: str = "open"

    assigned_to: Optional[str] = None