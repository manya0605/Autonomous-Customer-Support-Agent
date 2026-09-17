from typing import List, Dict, Any

from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models.conversation import ConversationMessage


def save_message(
    customer_id: int,
    conversation_id: str,
    role: str,
    message: str
) -> Dict[str, Any]:

    with Session(engine) as session:

        record = ConversationMessage(
            customer_id=customer_id,
            conversation_id=conversation_id,
            role=role,
            message=message
        )

        session.add(record)
        session.commit()
        session.refresh(record)

        return {
            "success": True,
            "message_id": record.id,
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "role": role
        }


def get_conversation_history(
    customer_id: int,
    conversation_id: str,
    limit: int = 10
) -> Dict[str, Any]:

    with Session(engine) as session:

        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.customer_id == customer_id,
                ConversationMessage.conversation_id == conversation_id
            )
            .order_by(ConversationMessage.created_at)
        )

        records = session.exec(statement).all()

        records = records[-limit:]

        messages: List[Dict[str, Any]] = []

        for record in records:
            messages.append({
                "message_id": record.id,
                "role": record.role,
                "message": record.message,
                "created_at": record.created_at.isoformat()
            })

        return {
            "success": True,
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "messages": messages,
            "count": len(messages)
        }