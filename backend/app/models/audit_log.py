from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class AuditLog(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    customer_id: Optional[int] = Field(
        default=None,
        index=True
    )

    conversation_id: Optional[str] = Field(
        default=None,
        index=True
    )

    action: str = Field(
        index=True
    )

    agent: Optional[str] = None

    entity_type: Optional[str] = None

    entity_id: Optional[int] = None

    status: str = Field(
        default="success",
        index=True
    )

    details: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )