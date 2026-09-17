from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class ConversationMessage(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    customer_id: int = Field(index=True)

    conversation_id: str = Field(index=True)

    role: str

    message: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )