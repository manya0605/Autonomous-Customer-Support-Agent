from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models.order import Order
from backend.app.models.payment import Payment
from backend.app.models.return_request import ReturnRequest
from backend.app.models.refund import Refund


def check_refund_eligibility(
    order_id: int,
    customer_id: int
):
    """
    Check refund eligibility only for an order
    belonging to the authenticated customer.
    """

    with Session(engine) as session:

        # ----------------------------------------------------
        # 1. CHECK ORDER
        # ----------------------------------------------------

        order = session.get(Order, order_id)

        if not order:
            return {
                "eligible": False,
                "message": "Order not found."
            }

        # ----------------------------------------------------
        # 2. SECURITY: VERIFY OWNERSHIP
        # ----------------------------------------------------

        if order.customer_id != customer_id:
            return {
                "eligible": False,
                "message": "This order does not belong to this customer."
            }

        # ----------------------------------------------------
        # 3. CHECK PAYMENT
        # ----------------------------------------------------

        payment = session.exec(
            select(Payment).where(
                Payment.order_id == order_id
            )
        ).first()

        if not payment:
            return {
                "eligible": False,
                "message": "No payment record was found for this order."
            }

        # ----------------------------------------------------
        # 4. PAYMENT MUST BE SUCCESSFUL
        # ----------------------------------------------------

        if payment.status != "successful":
            return {
                "eligible": False,
                "message": (
                    f"Refund is not currently eligible because "
                    f"payment status is '{payment.status}'."
                ),
                "payment_status": payment.status
            }

        # ----------------------------------------------------
        # 5. PREVENT DUPLICATE REFUND
        # ----------------------------------------------------

        existing_refund = session.exec(
            select(Refund).where(
                Refund.order_id == order_id,
                Refund.customer_id == customer_id
            )
        ).first()

        if existing_refund:
            return {
                "eligible": False,
                "message": (
                    "A refund request already exists for this order."
                ),
                "refund_id": existing_refund.id,
                "refund_reference": existing_refund.refund_reference,
                "refund_status": existing_refund.status
            }

        # ----------------------------------------------------
        # 6. CHECK RETURN
        # ----------------------------------------------------

        existing_return = session.exec(
            select(ReturnRequest).where(
                ReturnRequest.order_id == order_id,
                ReturnRequest.customer_id == customer_id
            )
        ).first()

        # ----------------------------------------------------
        # 7. DETERMINE ELIGIBILITY
        # ----------------------------------------------------

        eligible_reasons = [
            "cancelled before shipment",
            "returned eligible product",
            "defective",
            "damaged",
            "wrong product",
            "significant delivery failure"
        ]

        order_status = (order.status or "").lower()

        # Cancelled orders qualify.
        if order_status == "cancelled":
            return {
                "eligible": True,
                "message": (
                    "Order was cancelled and payment was successful."
                ),
                "order_id": order_id,
                "customer_id": customer_id,
                "payment_id": payment.id,
                "amount": payment.amount,
                "reason": "Order cancelled"
            }

        # Existing return can qualify if the reason
        # matches an eligible condition.
        if existing_return:

            return_reason = (
                existing_return.reason or ""
            ).lower()

            if any(
                reason in return_reason
                for reason in eligible_reasons
            ):
                return {
                    "eligible": True,
                    "message": (
                        "The order has an eligible return "
                        "associated with it."
                    ),
                    "order_id": order_id,
                    "customer_id": customer_id,
                    "payment_id": payment.id,
                    "amount": payment.amount,
                    "reason": existing_return.reason,
                    "return_id": existing_return.id
                }

        # Significant delivery failure.
        if order_status in [
            "delayed",
            "delivery_failed"
        ]:
            return {
                "eligible": True,
                "message": (
                    "The order has a significant delivery issue "
                    "and payment was successfully processed."
                ),
                "order_id": order_id,
                "customer_id": customer_id,
                "payment_id": payment.id,
                "amount": payment.amount,
                "reason": "Significant delivery failure"
            }

        # Otherwise not automatically eligible.
        return {
            "eligible": False,
            "message": (
                "The available order, payment and return "
                "information does not confirm refund eligibility."
            ),
            "order_id": order_id,
            "customer_id": customer_id,
            "payment_id": payment.id,
            "amount": payment.amount,
            "order_status": order.status,
            "payment_status": payment.status
        }