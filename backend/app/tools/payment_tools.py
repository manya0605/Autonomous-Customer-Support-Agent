from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import Payment, Order


def get_payment_status(
    order_id: int,
    customer_id: int
) -> dict:
    """
    Retrieve the payment status for an order
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
        # another customer's payment information.
        if order.customer_id != customer_id:
            return {
                "success": False,
                "error": "You can only access your own payment information"
            }

        statement = select(Payment).where(
            Payment.order_id == order_id
        )

        payment = session.exec(statement).first()

        if not payment:
            return {
                "success": False,
                "error": "Payment not found for this order"
            }

        return {
            "success": True,
            "payment_id": payment.id,
            "order_id": payment.order_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method,
            "status": payment.status,
            "transaction_id": payment.transaction_id
        }