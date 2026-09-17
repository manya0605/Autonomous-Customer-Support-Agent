from typing import Any, Dict, Optional

from backend.app.tools.payment_tools import get_payment_status
from backend.app.tools.refund_tools import check_refund_eligibility
from backend.app.tools.refund_action_tools import create_refund_request


def run_payment_agent(
    action: str,
    order_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    reason: Optional[str] = None
) -> Dict[str, Any]:
    """
    Payment Agent

    Supported actions:
        - payment_status
        - refund_eligibility
        - refund

    The agent never claims that a refund was completed
    unless the refund action actually succeeds.
    """

    # --------------------------------------------------
    # Validate action
    # --------------------------------------------------

    if not action:

        return {
            "success": False,
            "agent": "payment_agent",
            "message": "No payment action was provided."
        }

    action = action.lower().strip()

    supported_actions = {
        "payment_status",
        "refund_eligibility",
        "refund"
    }

    if action not in supported_actions:

        return {
            "success": False,
            "agent": "payment_agent",
            "message": (
                f"Unsupported payment action: {action}. "
                "Supported actions: payment_status, "
                "refund_eligibility, refund."
            )
        }

    # --------------------------------------------------
    # Validate order ID
    # --------------------------------------------------

    if order_id is None:

        return {
            "success": False,
            "agent": "payment_agent",
            "message": "Order ID is required."
        }

    try:

        order_id = int(order_id)

    except (TypeError, ValueError):

        return {
            "success": False,
            "agent": "payment_agent",
            "message": "Order ID must be a valid number."
        }

    if order_id <= 0:

        return {
            "success": False,
            "agent": "payment_agent",
            "message": "Order ID must be greater than zero."
        }

    # ==================================================
    # PAYMENT STATUS
    # ==================================================

    if action == "payment_status":

        result = get_payment_status(order_id, customer_id)

        if not result.get("success"):

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "payment_status",
                "order_id": order_id,
                "message": result.get(
                    "error",
                    "Unable to retrieve payment information."
                )
            }

        return {
            "success": True,
            "agent": "payment_agent",
            "action": "payment_status",
            "payment_id": result.get("payment_id"),
            "order_id": result.get("order_id"),
            "amount": result.get("amount"),
            "payment_method": result.get(
                "payment_method"
            ),
            "status": result.get("status"),
            "transaction_id": result.get(
                "transaction_id"
            ),
            "message": (
                f"Payment for order #{order_id} "
                f"is {result.get('status')}."
            )
        }

    # ==================================================
    # REFUND ELIGIBILITY
    # ==================================================

    if action == "refund_eligibility":

        if customer_id is None:

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund_eligibility",
                "order_id": order_id,
                "message": (
                    "Customer ID is required to "
                    "check refund eligibility."
                )
            }

        try:

            customer_id = int(customer_id)

        except (TypeError, ValueError):

            return {
                "success": False,
                "agent": "payment_agent",
                "message": (
                    "Customer ID must be a valid number."
                )
            }

        result = check_refund_eligibility(
            order_id,
            customer_id
        )

        if not result.get("eligible"):

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund_eligibility",
                "order_id": order_id,
                "customer_id": customer_id,
                "eligible": False,
                "message": result.get(
                    "message",
                    "Refund eligibility could not be confirmed."
                ),
                "refund_id": result.get("refund_id"),
                "refund_reference": result.get(
                    "refund_reference"
                ),
                "refund_status": result.get(
                    "refund_status"
                )
            }

        return {
            "success": True,
            "agent": "payment_agent",
            "action": "refund_eligibility",
            "order_id": result.get("order_id"),
            "customer_id": result.get(
                "customer_id"
            ),
            "eligible": True,
            "payment_id": result.get(
                "payment_id"
            ),
            "amount": result.get("amount"),
            "reason": result.get("reason"),
            "return_id": result.get(
                "return_id"
            ),
            "message": result.get(
                "message",
                "Refund is eligible."
            )
        }

    # ==================================================
    # REFUND REQUEST
    # ==================================================

    if action == "refund":

        if customer_id is None:

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund",
                "order_id": order_id,
                "message": (
                    "Customer ID is required to "
                    "request a refund."
                )
            }

        try:

            customer_id = int(customer_id)

        except (TypeError, ValueError):

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund",
                "order_id": order_id,
                "message": (
                    "Customer ID must be a valid number."
                )
            }

        # --------------------------------------------------
        # IMPORTANT:
        # Always check eligibility before executing refund.
        # --------------------------------------------------

        eligibility = check_refund_eligibility(
            order_id,
            customer_id
        )

        if not eligibility.get("eligible"):

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund",
                "order_id": order_id,
                "customer_id": customer_id,
                "eligible": False,
                "message": eligibility.get(
                    "message",
                    "Refund cannot be processed."
                ),
                "refund_id": eligibility.get(
                    "refund_id"
                ),
                "refund_reference": eligibility.get(
                    "refund_reference"
                ),
                "refund_status": eligibility.get(
                    "refund_status"
                )
            }

        # --------------------------------------------------
        # Determine refund reason
        # --------------------------------------------------

        refund_reason = (
            reason
            or eligibility.get("reason")
            or "Customer requested refund"
        )

        # --------------------------------------------------
        # Execute refund request
        # --------------------------------------------------

        refund_result = create_refund_request(
            order_id,
            customer_id,
            refund_reason
        )

        if not refund_result.get("success"):

            return {
                "success": False,
                "agent": "payment_agent",
                "action": "refund",
                "order_id": order_id,
                "customer_id": customer_id,
                "message": refund_result.get(
                    "message",
                    "Refund request could not be created."
                )
            }

        return {
            "success": True,
            "agent": "payment_agent",
            "action": "refund",
            "order_id": refund_result.get(
                "order_id"
            ),
            "customer_id": refund_result.get(
                "customer_id"
            ),
            "refund_id": refund_result.get(
                "refund_id"
            ),
            "refund_reference": refund_result.get(
                "refund_reference"
            ),
            "payment_id": refund_result.get(
                "payment_id"
            ),
            "amount": refund_result.get(
                "amount"
            ),
            "reason": refund_result.get(
                "reason"
            ),
            "status": refund_result.get(
                "status"
            ),
            "message": (
                "Refund request created successfully."
            )
        }

    # --------------------------------------------------
    # Safety fallback
    # --------------------------------------------------

    return {
        "success": False,
        "agent": "payment_agent",
        "message": (
            "Unable to process the payment request."
        )
    }