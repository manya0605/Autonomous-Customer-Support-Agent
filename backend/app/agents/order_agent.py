from typing import Any, Dict, Optional

from backend.app.tools.order_tools import get_order_status
from backend.app.tools.cancel_action_tools import cancel_order


def run_order_agent(
    action: str,
    order_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Order Agent

    Supported actions:
        - status
        - tracking
        - cancel
    """

    # --------------------------------------------------
    # Validate action
    # --------------------------------------------------

    if not action:
        return {
            "success": False,
            "agent": "order_agent",
            "message": "No order action was provided."
        }

    action = action.lower().strip()

    supported_actions = {
        "status",
        "tracking",
        "cancel"
    }

    if action not in supported_actions:
        return {
            "success": False,
            "agent": "order_agent",
            "message": (
                f"Unsupported order action: {action}. "
                f"Supported actions: status, tracking, cancel."
            )
        }
    
    # --------------------------------------------------
    # Validate authenticated customer ID
    # --------------------------------------------------

    if customer_id is None:
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Authenticated customer ID is required."
        }

    try:
        customer_id = int(customer_id)
    except (TypeError, ValueError):
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Customer ID must be a valid number."
        }

    if customer_id <= 0:
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Customer ID must be greater than zero."
        }


    # --------------------------------------------------
    # Validate order ID
    # --------------------------------------------------

    if order_id is None:
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Order ID is required."
        }

    try:
        order_id = int(order_id)
    except (TypeError, ValueError):
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Order ID must be a valid number."
        }

    if order_id <= 0:
        return {
            "success": False,
            "agent": "order_agent",
            "message": "Order ID must be greater than zero."
        }
    
    # ==================================================
    # GET ORDER STATUS
    # ==================================================

    if action == "status":

        result = get_order_status(order_id,
                                  customer_id)

        if not result.get("success"):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "status",
                "order_id": order_id,
                "message": result.get(
                    "error",
                    "Unable to retrieve order status."
                )
            }

        # Optional customer ownership verification
        if (
            customer_id is not None
            and result.get("customer_id") != customer_id
        ):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "status",
                "order_id": order_id,
                "message": (
                    "This order does not belong "
                    "to this customer."
                )
            }

        return {
            "success": True,
            "agent": "order_agent",
            "action": "status",
            "order_id": result.get("order_id"),
            "customer_id": result.get("customer_id"),
            "status": result.get("status"),
            "total_amount": result.get("total_amount"),
            "shipping_address": result.get(
                "shipping_address"
            ),
            "message": (
                f"Order #{result.get('order_id')} is "
                f"currently {result.get('status')}."
            )
        }

    # ==================================================
    # ORDER TRACKING
    # ==================================================

    if action == "tracking":

        result = get_order_status(order_id,
                                  customer_id
                                  )

        if not result.get("success"):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "tracking",
                "order_id": order_id,
                "message": result.get(
                    "error",
                    "Unable to retrieve tracking information."
                )
            }

        # Verify ownership
        if (
            customer_id is not None
            and result.get("customer_id") != customer_id
        ):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "tracking",
                "order_id": order_id,
                "message": (
                    "This order does not belong "
                    "to this customer."
                )
            }

        status = result.get("status")

        # Human-readable tracking message
        tracking_messages = {
            "pending": "Your order is pending processing.",
            "processing": "Your order is currently being processed.",
            "shipped": "Your order has been shipped.",
            "out_for_delivery": (
                "Your order is out for delivery."
            ),
            "delivered": "Your order has been delivered.",
            "delayed": (
                "Your order is currently delayed."
            ),
            "cancelled": (
                "Your order has been cancelled."
            )
        }

        tracking_message = tracking_messages.get(
            status,
            f"Your order is currently {status}."
        )

        return {
            "success": True,
            "agent": "order_agent",
            "action": "tracking",
            "order_id": result.get("order_id"),
            "customer_id": result.get("customer_id"),
            "status": status,
            "shipping_address": result.get(
                "shipping_address"
            ),
            "total_amount": result.get(
                "total_amount"
            ),
            "message": tracking_message
        }

    # ==================================================
    # CANCEL ORDER
    # ==================================================

    if action == "cancel":

        if customer_id is None:

            return {
                "success": False,
                "agent": "order_agent",
                "action": "cancel",
                "order_id": order_id,
                "message": (
                    "Customer ID is required to "
                    "cancel an order."
                )
            }

        try:
            customer_id = int(customer_id)
        except (TypeError, ValueError):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "cancel",
                "order_id": order_id,
                "message": (
                    "Customer ID must be a valid number."
                )
            }

        if customer_id <= 0:

            return {
                "success": False,
                "agent": "order_agent",
                "action": "cancel",
                "order_id": order_id,
                "message": (
                    "Customer ID must be greater than zero."
                )
            }

        result = cancel_order(
            order_id=order_id,
            customer_id=customer_id,
            conversation_id=conversation_id
        )

        if not result.get("success"):

            return {
                "success": False,
                "agent": "order_agent",
                "action": "cancel",
                "order_id": order_id,
                "customer_id": customer_id,
                "status": result.get("status"),
                "message": result.get(
                    "message",
                    "The order could not be cancelled."
                )
            }

        return {
          "success": True,
          "agent": "order_agent",
          "action": "cancel",
          "order_id": result.get("order_id"),
          "customer_id": result.get("customer_id"),
          "conversation_id": conversation_id,
          "previous_status": result.get("previous_status"),
          "status": result.get("status"),
          "total_amount": result.get("total_amount"),
          "message": result.get(
            "message",
            "Order cancelled successfully."
          )
        }

    # --------------------------------------------------
    # Safety fallback
    # --------------------------------------------------

    return {
        "success": False,
        "agent": "order_agent",
        "message": "Unable to process the order request."
    }