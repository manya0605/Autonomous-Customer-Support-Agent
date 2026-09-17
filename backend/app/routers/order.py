from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import Order, Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/customer/{customer_id}")
def get_customer_orders(
    customer_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own orders"
        )

    with Session(engine) as session:

        statement = select(Order).where(
            Order.customer_id == customer_id
        )

        orders = session.exec(statement).all()

        return orders


@router.get("/{order_id}/status")
def get_order_status(
    order_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        order = session.get(Order, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own orders"
            )

        return {
            "order_id": order.id,
            "status": order.status
        }


@router.get("/{order_id}")
def get_order(
    order_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        order = session.get(Order, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own orders"
            )

        return order