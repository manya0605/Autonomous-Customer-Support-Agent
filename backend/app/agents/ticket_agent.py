from typing import Any, Dict, Optional

from backend.app.tools.ticket_action_tools import create_support_ticket
from backend.app.tools.audit_tools import create_audit_log

def run_ticket_agent(
    customer_id: int,
    message: str,
    category: str = "general",
    priority: str = "medium",
    subject: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> Dict[str, Any]:

    # --------------------------------------------------------
    # VALIDATE CUSTOMER ID
    # --------------------------------------------------------

    if customer_id is None or customer_id <= 0:
        return {
            "success": False,
            "agent": "ticket_agent",
            "message": "A valid customer ID is required."
        }

    # --------------------------------------------------------
    # VALIDATE MESSAGE
    # --------------------------------------------------------

    if not message or not message.strip():
        return {
            "success": False,
            "agent": "ticket_agent",
            "message": "Please provide a description of the issue."
        }

    message = message.strip()

    # --------------------------------------------------------
    # CLEAN CATEGORY
    # --------------------------------------------------------

    if not category:
        category = "general"

    category = category.strip().lower()

    # --------------------------------------------------------
    # VALIDATE PRIORITY
    # --------------------------------------------------------

    allowed_priorities = {
        "low",
        "medium",
        "high",
        "urgent"
    }

    if not priority:
        priority = "medium"

    priority = priority.strip().lower()

    if priority not in allowed_priorities:
        priority = "medium"

    # --------------------------------------------------------
    # GENERATE SUBJECT
    # --------------------------------------------------------

    if not subject or not subject.strip():
        subject = "Customer Support Request"

    subject = subject.strip()

    # --------------------------------------------------------
    # CREATE SUPPORT TICKET
    # --------------------------------------------------------

    try:

        result = create_support_ticket(
            customer_id=customer_id,
            subject=subject,
            description=message,
            category=category,
            priority=priority
        )

    except Exception as exc:

        # Audit ticket creation failure
        try:

            create_audit_log(
                action="support_ticket_creation",
                status="failed",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="ticket_agent",
                entity_type="support_ticket",
                details="Support ticket creation failed."
            )

        except Exception:
            pass

        return {
            "success": False,
            "agent": "ticket_agent",
            "message": "Unable to create the support ticket.",
            "error": str(exc)
        }

    # --------------------------------------------------------
    # EXISTING TICKET
    # --------------------------------------------------------

    if not result.get("success"):

        existing_ticket_id = result.get(
            "ticket_id"
        )

        try:

            create_audit_log(
                action="support_ticket_creation",
                status="existing",
                customer_id=customer_id,
                conversation_id=conversation_id,
                agent="ticket_agent",
                entity_type="support_ticket",
                entity_id=existing_ticket_id,
                details="Existing open support ticket reused."
            )

        except Exception:
            pass

        return {
            "success": True,
            "agent": "ticket_agent",
            "ticket_created": False,
            "message": result.get(
                "message",
                "A similar support ticket is already open."
            ),
            "ticket_id": existing_ticket_id,
            "status": result.get(
                "status",
                "open"
            )
        }

    # --------------------------------------------------------
    # SUCCESSFULLY CREATED
    # --------------------------------------------------------

    ticket_id = result.get(
        "ticket_id"
    )

    try:

        create_audit_log(
            action="support_ticket_creation",
            status="success",
            customer_id=customer_id,
            conversation_id=conversation_id,
            agent="ticket_agent",
            entity_type="support_ticket",
            entity_id=ticket_id,
            details="Support ticket created successfully."
        )

    except Exception:
        pass

    return {
        "success": True,
        "agent": "ticket_agent",
        "ticket_created": True,
        "message": "Support ticket created successfully.",
        "ticket_id": ticket_id,
        "customer_id": result.get(
            "customer_id"
        ),
        "subject": result.get(
            "subject"
        ),
        "category": result.get(
            "category"
        ),
        "priority": result.get(
            "priority"
        ),
        "status": result.get(
            "status"
        )
    }