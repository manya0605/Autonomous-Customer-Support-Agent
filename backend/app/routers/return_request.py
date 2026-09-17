from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import ReturnRequest, Order, Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/returns",
    tags=["Returns"]
)


@router.get("/order/{order_id}")
def get_order_return(
    order_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        # Verify that the order belongs to the
        # authenticated customer.
        order = session.get(Order, order_id)

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own return information"
            )

        statement = select(ReturnRequest).where(
            ReturnRequest.order_id == order_id,
            ReturnRequest.customer_id == current_customer.id
        )

        return_request = session.exec(
            statement
        ).first()

        if not return_request:
            return {
                "order_id": order_id,
                "return_exists": False
            }

        return return_request


@router.get("/{return_id}")
def get_return(
    return_id: int,
    current_customer: Customer = Depends(get_current_customer)
):

    with Session(engine) as session:

        return_request = session.get(
            ReturnRequest,
            return_id
        )

        if not return_request:
            raise HTTPException(
                status_code=404,
                detail="Return request not found"
            )

        # Verify that the return belongs to the
        # authenticated customer.
        if return_request.customer_id != current_customer.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access your own return information"
            )

        return return_request