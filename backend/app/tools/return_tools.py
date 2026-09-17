from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import ReturnRequest, Order


def get_return_status(
    order_id: int,
    customer_id: int
) -> dict:
    """
    Check whether an order has a return request
    belonging to the authenticated customer.
    """

    with Session(engine) as session:

        # First verify that the order exists.
        order = session.get(Order, order_id)

        if not order:
            return {
                "success": False,
                "error": "Order not found"
            }

        # SECURITY:
        # Never allow one customer to access
        # another customer's return information.
        if order.customer_id != customer_id:
            return {
                "success": False,
                "error": "You can only access your own return information"
            }

        statement = select(ReturnRequest).where(
            ReturnRequest.order_id == order_id,
            ReturnRequest.customer_id == customer_id
        )

        return_request = session.exec(
            statement
        ).first()

        if not return_request:
            return {
                "success": True,
                "order_id": order_id,
                "return_exists": False,
                "message": "No return request exists for this order."
            }

        return {
            "success": True,
            "order_id": order_id,
            "return_exists": True,
            "return_id": return_request.id,
            "customer_id": return_request.customer_id,
            "reason": return_request.reason,
            "status": return_request.status,
            "refund_amount": return_request.refund_amount
        }