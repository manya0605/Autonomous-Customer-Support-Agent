from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models.ticket import SupportTicket


def create_support_ticket(
    customer_id: int,
    subject: str,
    description: str,
    category: str = "general",
    priority: str = "medium"
):

    with Session(engine) as session:

        # Check for an existing open ticket with the same subject
        existing = session.exec(
            select(SupportTicket).where(
                SupportTicket.customer_id == customer_id,
                SupportTicket.subject == subject,
                SupportTicket.status == "open"
            )
        ).first()

        if existing:

            return {
                "success": False,
                "message": "A similar support ticket is already open.",
                "ticket_id": existing.id,
                "status": existing.status
            }

        ticket = SupportTicket(
            customer_id=customer_id,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            status="open",
            assigned_to=None
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        return {
            "success": True,
            "message": "Support ticket created successfully.",
            "ticket_id": ticket.id,
            "customer_id": ticket.customer_id,
            "subject": ticket.subject,
            "description": ticket.description,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status
        }