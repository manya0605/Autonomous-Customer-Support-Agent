from sqlmodel import Session

from backend.app.database.database import engine
from backend.app.models.order import Order
from backend.app.tools.audit_tools import create_audit_log


def cancel_order(
    order_id: int,
    customer_id: int,
    conversation_id: str = None
):
    """
    Cancel an order only when it belongs to the
    authenticated customer and cancellation is permitted.

    Every cancellation attempt is recorded in the audit log.
    """

    with Session(engine) as session:

        # --------------------------------------------------
        # 1. FIND ORDER
        # --------------------------------------------------

        order = session.get(
            Order,
            order_id
        )

        if not order:

            create_audit_log(
                action="order_cancellation",
                status="failed",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="order_agent",
                entity_type="order",
                entity_id=order_id,
                details="Order not found."
            )

            return {
                "success": False,
                "message": "Order not found."
            }

        # --------------------------------------------------
        # 2. SECURITY: VERIFY CUSTOMER OWNERSHIP
        # --------------------------------------------------

        if order.customer_id != customer_id:

            create_audit_log(
                action="order_cancellation",
                status="denied",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="order_agent",
                entity_type="order",
                entity_id=order_id,
                details="Customer attempted to cancel an order they do not own."
            )

            return {
                "success": False,
                "message": (
                    "You can only cancel "
                    "your own order."
                )
            }

        # --------------------------------------------------
        # 3. CHECK CURRENT STATUS
        # --------------------------------------------------

        status = (
            order.status or ""
        ).lower()

        # Already cancelled
        if status == "cancelled":

            create_audit_log(
                action="order_cancellation",
                status="rejected",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="order_agent",
                entity_type="order",
                entity_id=order_id,
                details="Order was already cancelled."
            )

            return {
                "success": False,
                "message": (
                    "This order has already been cancelled."
                ),
                "order_id": order_id,
                "status": "cancelled"
            }

        # Delivered orders cannot be cancelled
        if status == "delivered":

            create_audit_log(
                action="order_cancellation",
                status="rejected",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="order_agent",
                entity_type="order",
                entity_id=order_id,
                details="Delivered orders cannot be cancelled."
            )

            return {
                "success": False,
                "message": (
                    "A delivered order cannot be cancelled."
                ),
                "order_id": order_id,
                "status": status
            }

        # Out-for-delivery orders cannot be automatically cancelled
        if status == "out_for_delivery":

            create_audit_log(
                action="order_cancellation",
                status="rejected",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="order_agent",
                entity_type="order",
                entity_id=order_id,
                details=(
                    "Order is already out for delivery "
                    "and cannot be cancelled automatically."
                )
            )

            return {
                "success": False,
                "message": (
                    "This order is already out for delivery "
                    "and cannot be cancelled automatically."
                ),
                "order_id": order_id,
                "status": status
            }

        # --------------------------------------------------
        # 4. CANCEL ORDER
        # --------------------------------------------------

        previous_status = status

        order.status = "cancelled"

        session.add(order)
        session.commit()
        session.refresh(order)

        # --------------------------------------------------
        # 5. AUDIT SUCCESSFUL CANCELLATION
        # --------------------------------------------------

        create_audit_log(
            action="order_cancellation",
            status="success",
            customer_id=customer_id,
            conversation_id=conversation_id,
            agent="order_agent",
            entity_type="order",
            entity_id=order_id,
            details=(
                f"Order cancelled successfully. "
                f"Previous status: {previous_status}."
            )
        )

        # --------------------------------------------------
        # 6. RETURN RESULT
        # --------------------------------------------------

        return {
            "success": True,
            "message": "Order cancelled successfully.",
            "order_id": order_id,
            "customer_id": customer_id,
            "previous_status": previous_status,
            "status": order.status,
            "total_amount": order.total_amount
        }