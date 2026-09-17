from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.refund import Refund


def create_refund_request(
    order_id: int,
    customer_id: int,
    reason: str
):
    """
    Create a refund request only for an order
    belonging to the authenticated customer.
    """

    with Session(engine) as session:

        # ====================================================
        # 1. VERIFY ORDER
        # ====================================================

        order = session.get(
            Order,
            order_id
        )

        if not order:
            return {
                "success": False,
                "message": "Order not found."
            }

        # ====================================================
        # 2. SECURITY: VERIFY CUSTOMER OWNERSHIP
        # ====================================================

        if order.customer_id != customer_id:
            return {
                "success": False,
                "message": (
                    "You can only create a refund "
                    "for your own order."
                )
            }

        # ====================================================
        # 3. CHECK PAYMENT
        # ====================================================

        payment = session.exec(
            select(Payment).where(
                Payment.order_id == order_id
            )
        ).first()

        if not payment:
            return {
                "success": False,
                "message": (
                    "No payment record was found "
                    "for this order."
                )
            }

        # ====================================================
        # 4. PAYMENT MUST BE SUCCESSFUL
        # ====================================================

        if payment.status != "successful":
            return {
                "success": False,
                "message": (
                    f"Refund cannot be created because "
                    f"the payment status is "
                    f"'{payment.status}'."
                ),
                "payment_status": payment.status
            }

        # ====================================================
        # 5. CHECK FOR EXISTING REFUND
        # ====================================================

        existing_refund = session.exec(
            select(Refund).where(
                Refund.order_id == order_id,
                Refund.customer_id == customer_id
            )
        ).first()

        if existing_refund:
            return {
                "success": False,
                "message": (
                    "A refund request already exists "
                    "for this order."
                ),
                "refund_id": existing_refund.id,
                "refund_reference": (
                    existing_refund.refund_reference
                ),
                "status": existing_refund.status
            }

        # ====================================================
        # 6. CREATE REFUND REFERENCE
        # ====================================================

        refund_reference = (
            f"REF-{order_id:04d}-{payment.id:04d}"
        )

        # ====================================================
        # 7. CREATE REFUND
        # ====================================================

        refund = Refund(
            order_id=order_id,
            customer_id=customer_id,
            payment_id=payment.id,
            amount=payment.amount,
            reason=reason,
            status="requested",
            refund_reference=refund_reference
        )

        session.add(refund)

        session.commit()

        session.refresh(refund)

        # ====================================================
        # 8. RETURN RESULT
        # ====================================================

        return {
            "success": True,
            "message": "Refund request created successfully.",
            "refund_id": refund.id,
            "refund_reference": refund.refund_reference,
            "order_id": refund.order_id,
            "customer_id": refund.customer_id,
            "payment_id": refund.payment_id,
            "amount": refund.amount,
            "reason": refund.reason,
            "status": refund.status
        }