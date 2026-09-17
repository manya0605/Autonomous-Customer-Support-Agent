from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models.order import Order
from backend.app.models.return_request import ReturnRequest


def create_return_request(
    order_id: int,
    customer_id: int,
    reason: str
) -> dict:
    """
    Create a return request only for an order
    belonging to the authenticated customer.
    """

    with Session(engine) as session:

        # ----------------------------------------------------
        # CHECK ORDER
        # ----------------------------------------------------

        order = session.exec(
            select(Order).where(
                Order.id == order_id
            )
        ).first()

        if not order:
            return {
                "success": False,
                "message": f"Order {order_id} was not found."
            }

        # ----------------------------------------------------
        # SECURITY: VERIFY CUSTOMER OWNS ORDER
        # ----------------------------------------------------

        if order.customer_id != customer_id:
            return {
                "success": False,
                "message": (
                    "You can only create a return "
                    "for your own order."
                )
            }

        # ----------------------------------------------------
        # CHECK EXISTING RETURN
        # ----------------------------------------------------

        existing_return = session.exec(
            select(ReturnRequest).where(
                ReturnRequest.order_id == order_id,
                ReturnRequest.customer_id == customer_id
            )
        ).first()

        if existing_return:
            return {
                "success": False,
                "message": (
                    f"A return request already exists "
                    f"for order {order_id}."
                ),
                "return_id": existing_return.id,
                "status": existing_return.status
            }

        # ----------------------------------------------------
        # CREATE RETURN REQUEST
        # ----------------------------------------------------

        new_return = ReturnRequest(
            order_id=order_id,
            customer_id=customer_id,
            reason=reason,
            status="requested"
        )

        session.add(new_return)
        session.commit()
        session.refresh(new_return)

        return {
            "success": True,
            "message": "Return request created successfully.",
            "return_id": new_return.id,
            "order_id": order_id,
            "customer_id": customer_id,
            "reason": reason,
            "status": new_return.status,
            "refund_amount": new_return.refund_amount
        }