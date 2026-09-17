from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import Payment, Order, Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.get("/order/{order_id}")
def get_order_payment(
    order_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        # First verify that the order belongs to
        # the logged-in customer.
        order = session.get(Order, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own payment information"
            )

        statement = select(Payment).where(
            Payment.order_id == order_id
        )

        payment = session.exec(statement).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        return payment


@router.get("/{payment_id}")
def get_payment(
    payment_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        payment = session.get(
            Payment,
            payment_id
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found"
            )

        # Find the order associated with this payment.
        order = session.get(
            Order,
            payment.order_id
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Associated order not found"
            )

        # Verify ownership.
        if order.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own payment information"
            )

        return payment