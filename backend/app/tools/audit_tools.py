from typing import Optional

from sqlmodel import Session

from backend.app.database.database import engine
from backend.app.models import AuditLog


def create_audit_log(
    action: str,
    status: str = "success",
    customer_id: Optional[int] = None,
    conversation_id: Optional[str] = None,
    agent: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
):
    """
    Create a persistent audit log entry.
    """

    with Session(engine) as session:

        audit = AuditLog(
            customer_id=customer_id,
            conversation_id=conversation_id,
            action=action,
            agent=agent,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            details=details,
        )

        session.add(audit)
        session.commit()
        session.refresh(audit)

        return {
            "success": True,
            "audit_id": audit.id,
            "action": audit.action,
            "status": audit.status,
            "customer_id": audit.customer_id,
            "conversation_id": audit.conversation_id,
            "agent": audit.agent,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
        }