from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import SupportTicket


def get_customer_tickets(customer_id: int) -> dict:
    """
    Retrieve support tickets belonging to a customer.
    """

    with Session(engine) as session:

        statement = select(SupportTicket).where(
            SupportTicket.customer_id == customer_id
        )

        tickets = session.exec(statement).all()

        if not tickets:
            return {
                "success": True,
                "customer_id": customer_id,
                "ticket_count": 0,
                "tickets": []
            }

        return {
            "success": True,
            "customer_id": customer_id,
            "ticket_count": len(tickets),
            "tickets": [
                {
                    "ticket_id": ticket.id,
                    "subject": ticket.subject,
                    "description": ticket.description,
                    "category": ticket.category,
                    "priority": ticket.priority,
                    "status": ticket.status
                }
                for ticket in tickets
            ]
        }