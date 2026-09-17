from sqlmodel import Session

from backend.app.database.database import engine
from backend.app.models import Order


def get_order_status(
    order_id: int,
    customer_id: int
) -> dict:
    """
    Retrieve the current status of an order
    belonging to the authenticated customer.
    """

    with Session(engine) as session:

        order = session.get(Order, order_id)

        if not order:
            return {
                "success": False,
                "error": "Order not found"
            }

        # SECURITY:
        # Never allow one customer to access
        # another customer's order.
        if order.customer_id != customer_id:
            return {
                "success": False,
                "error": "You can only access your own order"
            }

        return {
            "success": True,
            "order_id": order.id,
            "customer_id": order.customer_id,
            "status": order.status,
            "total_amount": order.total_amount,
            "shipping_address": order.shipping_address
        }