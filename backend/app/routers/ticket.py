from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import SupportTicket, Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/tickets",
    tags=["Support Tickets"]
)


@router.get("/customer/{customer_id}")
def get_customer_tickets(
    customer_id: int,
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own support tickets"
        )

    with Session(engine) as session:

        statement = select(SupportTicket).where(
            SupportTicket.customer_id == customer_id
        )

        tickets = session.exec(statement).all()

        return tickets


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    with Session(engine) as session:

        ticket = session.get(
            SupportTicket,
            ticket_id
        )

        if not ticket:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        if ticket.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own support tickets"
            )

        return ticket