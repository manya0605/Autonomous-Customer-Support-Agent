import json
import re

from backend.app.core.ai import client, MODEL

from backend.app.tools.order_tools import get_order_status
from backend.app.tools.payment_tools import get_payment_status
from backend.app.tools.return_tools import get_return_status
from backend.app.tools.ticket_tools import get_customer_tickets
from backend.app.tools.rag_tools import search_company_policy

from backend.app.tools.return_action_tools import create_return_request
from backend.app.tools.refund_tools import check_refund_eligibility
from backend.app.tools.refund_action_tools import create_refund_request
from backend.app.tools.cancel_action_tools import cancel_order
from backend.app.tools.ticket_action_tools import create_support_ticket
from backend.app.agents.intent_agent import run_intent_agent
from backend.app.agents.knowledge_agent import run_knowledge_agent
from backend.app.agents.order_agent import run_order_agent
from backend.app.agents.payment_agent import run_payment_agent
from backend.app.agents.sentiment_agent import run_sentiment_agent
from backend.app.agents.escalation_agent import run_escalation_agent
from backend.app.agents.ticket_agent import run_ticket_agent
from backend.app.agents.troubleshooting_agent import run_troubleshooting_agent
from backend.app.tools.memory_tools import (
    save_message,
    get_conversation_history
)
from backend.app.tools.memory_tools import (
    save_message,
    get_conversation_history
)
from backend.app.tools.audit_tools import create_audit_log


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the current status and details of an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    },
                    "customer_id":{
                        "type": "integer"
                    }
                },
                "required": ["order_id",
                             "customer_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_payment_status",
            "description": "Check the payment status associated with an order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_return_status",
            "description": "Check whether an order already has a return request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    }
                },
                "required": ["order_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_customer_tickets",
            "description": "Retrieve support tickets belonging to a customer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    }
                },
                "required": ["customer_id"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_company_policy",
            "description": "Search trusted company policies and FAQ documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_return_request",
            "description": "Create a return request after verifying the order and existing return status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    },
                    "customer_id": {
                        "type": "integer"
                    },
                    "reason": {
                        "type": "string"
                    }
                },
                "required": [
                    "order_id",
                    "customer_id",
                    "reason"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_refund_eligibility",
            "description": "Check refund eligibility using order, payment, return and policy information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    },
                    "customer_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "order_id",
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_refund_request",
            "description": "Create a refund request only after eligibility is confirmed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    },
                    "customer_id": {
                        "type": "integer"
                    },
                    "reason": {
                        "type": "string"
                    }
                },
                "required": [
                    "order_id",
                    "customer_id",
                    "reason"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "cancel_order",
            "description": "Cancel an order when cancellation is permitted.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer"
                    },
                    "customer_id": {
                        "type": "integer"
                    }
                },
                "required": [
                    "order_id",
                    "customer_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "Create a support ticket for human assistance or unresolved issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer"
                    },
                    "subject": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "category": {
                        "type": "string"
                    },
                    "priority": {
                        "type": "string"
                    }
                },
                "required": [
                    "customer_id",
                    "subject",
                    "description",
                    "category",
                    "priority"
                ]
            }
        }
    }
]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an autonomous customer support agent.

You assist customers with:

- Order status
- Payment status
- Delivery problems
- Returns
- Refunds
- Cancellation
- Company policies
- Existing support tickets
- Human support escalation

============================================================
STRICT SAFETY AND ACCURACY RULES
============================================================

1. Never invent information.

2. Never fabricate order information.

3. Never fabricate payment information.

4. Never fabricate tracking information.

5. Never invent a delivery date.

6. Never guarantee a refund unless eligibility is confirmed
   by trusted system information.

7. Never claim an action succeeded unless the corresponding
   tool confirms success.

8. Never expose internal tool names or function calls.

9. Never output XML, JSON function calls, or tool-call syntax
   to the customer.

10. Use trusted database information and company policy only.

11. Currency in this system is Indian Rupees (₹).

12. NEVER convert ₹4,999 into $49.99 or any other currency.

13. When displaying an amount returned by a tool, preserve
    the exact numerical value and use ₹ unless the customer
    explicitly requests another currency.

============================================================
ORDER RULES
============================================================

- Always verify the order before taking an action.
- Verify customer ownership.
- Do not invent tracking information.
- Do not invent delivery dates.
- Report the actual order status returned by the database.

============================================================
PAYMENT RULES
============================================================

- Check the payment record for payment questions.
- Possible states include:
  successful
  pending
  failed
  refunded

- Report the actual amount from the payment record.
- Use ₹ for monetary amounts.

============================================================
RETURN RULES
============================================================

- Check the order.
- Check existing return status.
- Never create a duplicate return.
- Follow the company return policy.
- Never claim a return was created unless the action tool
  confirms success.

============================================================
REFUND RULES
============================================================

- Policy questions are informational questions.
- A refund action requires an order number.
- Check company refund policy.
- Check refund eligibility.
- Check payment and return information.
- Never create a duplicate refund.
- Never guarantee a completed refund.
- A refund request is not the same as a completed refund.

============================================================
CANCELLATION RULES
============================================================

When the customer asks to cancel a specific order:

1. This is an ACTION request, not a general policy question.

2. You MUST use the cancellation workflow.

3. First call get_order_status with the requested order_id.

4. The authenticated customer_id must always be used.
   Never trust or use a customer_id supplied by the model/user.

5. Verify that the order belongs to the authenticated customer.

6. If the order does not belong to the authenticated customer,
   do not reveal any order information and do not call
   cancel_order. Escalate or return a safe access-denied response.

7. If the order belongs to the authenticated customer,
   check its current status.

8. Never cancel a delivered order.

9. Never automatically cancel an order that is already
   out_for_delivery.

10. If cancellation is permitted, call cancel_order.

11. Never claim cancellation succeeded unless cancel_order
    returns success=true.

12. If cancellation cannot safely be completed automatically,
    escalate to human support.

IMPORTANT:
A request such as "Cancel order #2" or "I want to cancel order 2"
MUST NOT be answered only with the cancellation policy.
It must enter the cancellation workflow and verify the order.

============================================================
HUMAN ESCALATION
============================================================

Create a support ticket when:

- The customer explicitly asks for a human.
- The customer asks to speak to support.
- The customer requests a representative.
- The issue cannot safely be resolved automatically.
- The system cannot determine the answer.
- A serious unresolved issue requires human intervention.

For human escalation:

category = escalation
priority = high

If a ticket already exists, do not create a duplicate.
Tell the customer about the existing ticket.

============================================================
POLICY QUESTIONS
============================================================

Questions such as:

"What is your refund policy?"
"What is your return policy?"
"What is your cancellation policy?"
"How does the refund process work?"
"Can I return an item?"

when asking for general policy information should use
search_company_policy.

Do NOT ask for an order number for a general policy question.

If the customer wants to perform an action, such as:

"Refund order #2"
"Return order #2"
"Cancel order #2"

then use the appropriate workflow.
"""


# ============================================================
# ORDER ID EXTRACTION
# ============================================================

def extract_order_id(message):

    patterns = [
        r"order\s*#?\s*(\d+)",
        r"order\s+number\s*#?\s*(\d+)",
        r"order\s+no\.?\s*#?\s*(\d+)",
        r"#\s*(\d+)"
    ]

    text = message.lower()

    for pattern in patterns:

        match = re.search(
            pattern,
            text
        )

        if match:
            return int(match.group(1))

    return None


# ============================================================
# REASON EXTRACTION
# ============================================================

def extract_reason(message):

    text = message.lower()

    if "defective" in text:
        return "Product is defective"

    if "damaged" in text:
        return "Product is damaged"

    if "wrong product" in text:
        return "Wrong product received"

    if "wrong item" in text:
        return "Wrong item received"

    if "not meet expectations" in text:
        return "Product does not meet expectations"

    if "delayed" in text:
        return "Customer requested refund for delayed order"

    return "Customer requested refund"


# ============================================================
# POLICY QUESTION DETECTION
# ============================================================

REFUND_POLICY_PHRASES = [
    "what is your refund policy",
    "what is the refund policy",
    "refund policy",
    "refund rules",
    "refund process",
    "how does refund work",
    "how do refunds work",
    "how does the refund work",
    "explain refund policy"
]


RETURN_POLICY_PHRASES = [
    "what is your return policy",
    "what is the return policy",
    "return policy",
    "return rules",
    "return process",
    "how does return work",
    "how do returns work"
]


CANCELLATION_POLICY_PHRASES = [
    "what is your cancellation policy",
    "what is the cancellation policy",
    "cancellation policy",
    "cancellation rules",
    "cancellation process",
    "how does cancellation work",
    "how do cancellations work"
]


def is_refund_policy_question(text):

    return any(
        phrase in text
        for phrase in REFUND_POLICY_PHRASES
    )


def is_return_policy_question(text):

    return any(
        phrase in text
        for phrase in RETURN_POLICY_PHRASES
    )


def is_cancellation_policy_question(text):

    return any(
        phrase in text
        for phrase in CANCELLATION_POLICY_PHRASES
    )

# ============================================================
# TOOL EXECUTION WITH GUARDRAILS
# ============================================================

def execute_tool(
    tool_name,
    arguments
):

    # --------------------------------------------------------
    # INPUT GUARDRAILS
    # --------------------------------------------------------

    if not isinstance(tool_name, str) or not tool_name.strip():

        return {
            "success": False,
            "error": "Invalid tool name."
        }

    if not isinstance(arguments, dict):

        return {
            "success": False,
            "error": "Invalid tool arguments."
        }

    # --------------------------------------------------------
    # ALLOWED TOOLS
    # --------------------------------------------------------

    allowed_tools = {
        "get_order_status",
        "get_payment_status",
        "get_return_status",
        "get_customer_tickets",
        "search_company_policy",
        "create_return_request",
        "check_refund_eligibility",
        "create_refund_request",
        "cancel_order",
        "create_support_ticket"
    }

    if tool_name not in allowed_tools:

        return {
            "success": False,
            "error": "Tool execution is not permitted."
        }

    # --------------------------------------------------------
    # HELPER VALIDATORS
    # --------------------------------------------------------

    def require_fields(*fields):

        missing = [
            field
            for field in fields
            if field not in arguments
            or arguments[field] is None
            or (
                isinstance(arguments[field], str)
                and not arguments[field].strip()
            )
        ]

        if missing:

            return {
                "success": False,
                "error": (
                    "Missing required tool arguments: "
                    + ", ".join(missing)
                )
            }

        return None

    def validate_id(value, field_name):

        if isinstance(value, bool) or not isinstance(value, int):

            return {
                "success": False,
                "error": f"Invalid {field_name}."
            }

        if value <= 0:

            return {
                "success": False,
                "error": f"Invalid {field_name}."
            }

        return None

    # --------------------------------------------------------
    # READ-ONLY TOOLS
    # --------------------------------------------------------

    if tool_name == "get_order_status":

        error = require_fields(
            "order_id",
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return get_order_status(
            arguments["order_id"],
            arguments["customer_id"]
        )

    if tool_name == "get_payment_status":

        error = require_fields(
            "order_id",
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return get_payment_status(
            arguments["order_id"],
            arguments["customer_id"]
        )

    if tool_name == "get_return_status":

        error = require_fields(
            "order_id",
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return get_return_status(
            arguments["order_id"],
            arguments["customer_id"]
        )

    if tool_name == "get_customer_tickets":

        error = require_fields(
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return get_customer_tickets(
            arguments["customer_id"]
        )

    # --------------------------------------------------------
    # RAG / POLICY TOOL
    # --------------------------------------------------------

    if tool_name == "search_company_policy":

        error = require_fields("query")

        if error:
            return error

        query = arguments["query"]

        if not isinstance(query, str):

            return {
                "success": False,
                "error": "Invalid policy search query."
            }

        query = query.strip()

        if not query:

            return {
                "success": False,
                "error": "Policy search query cannot be empty."
            }

        if len(query) > 2000:

            return {
                "success": False,
                "error": "Policy search query is too long."
            }

        return search_company_policy(query)

    # --------------------------------------------------------
    # RETURN CREATION
    # --------------------------------------------------------

    if tool_name == "create_return_request":

        error = require_fields(
            "order_id",
            "customer_id",
            "reason"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        reason = arguments["reason"]

        if not isinstance(reason, str):

            return {
                "success": False,
                "error": "Invalid return reason."
            }

        reason = reason.strip()

        if not reason or len(reason) > 1000:

            return {
                "success": False,
                "error": "Invalid return reason."
            }

        return create_return_request(
            arguments["order_id"],
            arguments["customer_id"],
            reason
        )

    # --------------------------------------------------------
    # REFUND ELIGIBILITY
    # --------------------------------------------------------

    if tool_name == "check_refund_eligibility":

        error = require_fields(
            "order_id",
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return check_refund_eligibility(
            arguments["order_id"],
            arguments["customer_id"]
        )

    # --------------------------------------------------------
    # REFUND CREATION
    # --------------------------------------------------------

    if tool_name == "create_refund_request":

        error = require_fields(
            "order_id",
            "customer_id",
            "reason"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        reason = arguments["reason"]

        if not isinstance(reason, str):

            return {
                "success": False,
                "error": "Invalid refund reason."
            }

        reason = reason.strip()

        if not reason or len(reason) > 1000:

            return {
                "success": False,
                "error": "Invalid refund reason."
            }

        return create_refund_request(
            arguments["order_id"],
            arguments["customer_id"],
            reason
        )

    # --------------------------------------------------------
    # ORDER CANCELLATION
    # --------------------------------------------------------

    if tool_name == "cancel_order":

        error = require_fields(
            "order_id",
            "customer_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["order_id"],
            "order_id"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        return cancel_order(
            arguments["order_id"],
            arguments["customer_id"]
        )

    # --------------------------------------------------------
    # SUPPORT TICKET
    # --------------------------------------------------------

    if tool_name == "create_support_ticket":

        error = require_fields(
            "customer_id",
            "subject",
            "description"
        )

        if error:
            return error

        error = validate_id(
            arguments["customer_id"],
            "customer_id"
        )

        if error:
            return error

        subject = arguments["subject"]
        description = arguments["description"]

        if not isinstance(subject, str) or not isinstance(
            description,
            str
        ):

            return {
                "success": False,
                "error": "Invalid ticket fields."
            }

        subject = subject.strip()
        description = description.strip()

        if (
            not subject
            or not description
            or len(subject) > 500
            or len(description) > 5000
        ):

            return {
                "success": False,
                "error": "Invalid ticket fields."
            }

        category = arguments.get(
            "category",
            "general"
        )

        priority = arguments.get(
            "priority",
            "medium"
        )

        allowed_categories = {
            "general",
            "order",
            "payment",
            "refund",
            "return",
            "cancellation",
            "technical"
        }

        allowed_priorities = {
            "low",
            "medium",
            "high",
            "urgent"
        }

        if category not in allowed_categories:

            return {
                "success": False,
                "error": "Invalid ticket category."
            }

        if priority not in allowed_priorities:

            return {
                "success": False,
                "error": "Invalid ticket priority."
            }

        return create_support_ticket(
            customer_id=arguments["customer_id"],
            subject=subject,
            description=description,
            category=category,
            priority=priority
        )

    # --------------------------------------------------------
    # FINAL SAFETY FALLBACK
    # --------------------------------------------------------

    return {
        "success": False,
        "error": "Tool execution is not permitted."
    }

# ============================================================
# HUMAN ESCALATION
# ============================================================

def handle_human_escalation(
    message,
    customer_id
):

    result = create_support_ticket(
        customer_id=customer_id,
        subject="Human support requested",
        description=message,
        category="escalation",
        priority="high"
    )

    # --------------------------------------------------------
    # NEW TICKET CREATED
    # --------------------------------------------------------

    if result.get("success") is True:

        ticket_id = result.get("ticket_id")

        create_audit_log(
            action="human_escalation",
            status="success",
            customer_id=customer_id,
            agent="escalation_agent",
            entity_type="support_ticket",
            entity_id=ticket_id,
            details="Human support ticket created."
        )

        return {
            "response": (
                "I've created a support ticket for you "
                "and escalated your request to human support.\n\n"
                f"Ticket ID: #{ticket_id}\n"
                f"Status: {result.get('status', 'open')}\n"
                f"Priority: {result.get('priority', 'high')}\n\n"
                "A support representative can assist you "
                "with your request."
            ),
            "tool_used": [
                "create_support_ticket"
            ]
        }

    # --------------------------------------------------------
    # EXISTING TICKET
    # --------------------------------------------------------

    existing_ticket_id = result.get(
        "ticket_id"
    )

    if existing_ticket_id is not None:

        create_audit_log(
            action="human_escalation",
            status="existing",
            customer_id=customer_id,
            agent="escalation_agent",
            entity_type="support_ticket",
            entity_id=existing_ticket_id,
            details="Existing open human-support ticket reused."
        )

        return {
            "response": (
                "You already have an open support ticket "
                "for this request.\n\n"
                f"Ticket ID: #{existing_ticket_id}\n"
                f"Status: {result.get('status', 'open')}\n\n"
                "A support representative can assist you "
                "through this existing ticket."
            ),
            "tool_used": [
                "create_support_ticket"
            ]
        }

    # --------------------------------------------------------
    # TICKET CREATION FAILED
    # --------------------------------------------------------

    create_audit_log(
        action="human_escalation",
        status="failed",
        customer_id=customer_id,
        agent="escalation_agent",
        entity_type="support_ticket",
        details="Unable to create or locate a support ticket."
    )

    return {
        "response": (
            "I was unable to create the support ticket "
            "automatically. Please allow me to escalate "
            "this request to a support representative."
        ),
        "tool_used": [
            "create_support_ticket"
        ]
    }

# ============================================================
# POLICY WORKFLOW
# ============================================================

def handle_policy_question(query):

    result = search_company_policy(query)

    # RAG tool returns:
    # {
    #   "success": True,
    #   "results": [
    #       {
    #           "source": "...",
    #           "score": ...,
    #           "content": "..."
    #       }
    #   ]
    # }

    if isinstance(result, dict):

        results = result.get("results", [])

        if results:

            # Best matching document
            best_result = results[0]

            content = best_result.get(
                "content",
                ""
            )

            if content:

                return {
                    "response": content,
                    "tool_used": [
                        "search_company_policy"
                    ]
                }

        message = result.get(
            "message"
        )

        if message:

            return {
                "response": message,
                "tool_used": [
                    "search_company_policy"
                ]
            }

    return {
        "response": (
            "I couldn't retrieve the requested company policy "
            "at the moment."
        ),
        "tool_used": [
            "search_company_policy"
        ]
    }

# ============================================================
# REFUND WORKFLOW
# ============================================================

def handle_refund_request(
    message,
    customer_id
):

    order_id = extract_order_id(
        message
    )

    if order_id is None:

        return {
            "response": (
                "Please provide the order number for "
                "the refund request."
            ),
            "tool_used": []
        }

    tools_used = []

    search_company_policy(
        "refund policy eligibility refund process"
    )

    tools_used.append(
        "search_company_policy"
    )

    eligibility = check_refund_eligibility(
        order_id,
        customer_id
    )

    tools_used.append(
        "check_refund_eligibility"
    )

    if not eligibility.get("eligible"):

        return {
            "response": eligibility.get(
                "message",
                "This order is not currently eligible "
                "for a refund."
            ),
            "tool_used": tools_used
        }

    result = create_refund_request(
        order_id,
        customer_id,
        extract_reason(message)
    )

    tools_used.append(
        "create_refund_request"
    )

    if not result.get("success"):

        return {
            "response": result.get(
                "message",
                "I could not create the refund request."
            ),
            "tool_used": tools_used
        }

    amount = result.get(
        "amount",
        eligibility.get(
            "amount",
            0
        )
    )

    return {
        "response": (
            f"Your refund request has been successfully "
            f"created for order #{order_id}.\n\n"
            f"**Refund details:**\n"
            f"- Amount: ₹{float(amount):.2f}\n"
            f"- Refund ID: {result.get('refund_id')}\n"
            f"- Reference: {result.get('refund_reference')}\n"
            f"- Status: {result.get('status', 'requested')}\n\n"
            "The refund request has been recorded. "
            "Actual processing time depends on the payment provider."
        ),
        "tool_used": tools_used
    }


# ============================================================
# RETURN WORKFLOW
# ============================================================

def handle_return_request(
    message,
    customer_id
):

    order_id = extract_order_id(
        message
    )

    if order_id is None:

        return {
            "response": (
                "Please provide the order number for "
                "the return request."
            ),
            "tool_used": []
        }

    tools_used = []

    order = get_order_status(
        order_id,
        customer_id
    )

    tools_used.append(
        "get_order_status"
    )

    if not order.get("success"):

        return {
            "success": False,
            "agent": "return_agent",
            "response":order.get(
                "message",
                order.get(
                    "error",
                    "I couldn't verify this order."
                )
            ),
            "tool_used": tools_used
        }

    if order.get("customer_id") != customer_id:

        return {
            "success": False,
            "agent": "return_agent",
            "response": (
                "I couldn't verify that this order "
                "belongs to your account."
            ),
            "tool_used": tools_used
        }

    existing = get_return_status(
        order_id,
        customer_id
    )

    tools_used.append(
        "get_return_status"
    )

    #Check whether a return request already exists.
    # get_return_status() returns a single return record,
    # not a "returns" list.

    if existing.get("return_exists", False):

        return_id = existing.get("return_id")

        response = (
            f"A return request already exists "
            f"for order #{order_id}."
        )

        if return_id:

            response += (
                f"\n\nReturn ID: {return_id}"
            )

        response += (
            "\n\nI have not created a duplicate return request."
        )

        return {
            "success": True,
            "agent": "return_agent",
            "response": response,
            "tool_used": tools_used
        }

        
    search_company_policy(
        "return policy defective damaged wrong product"
    )

    tools_used.append(
        "search_company_policy"
    )

    result = create_return_request(
        order_id,
        customer_id,
        extract_reason(message)
    )

    tools_used.append(
        "create_return_request"
    )

    if not result.get("success"):

        return {
            "success": False,
            "agent": "return_agent",
            "response": result.get(
                "message",
                "I couldn't create the return request."
            ),
            "tool_used": tools_used
        }

    return {
        "success": True,
        "agent": "return_agent",
        "response": (
            f"Your return request for order #{order_id} "
            "has been successfully created.\n\n"
            f"Return ID: {result.get('return_id')}\n"
            f"Status: {result.get('status', 'requested')}"
        ),
        "tool_used": tools_used
    }


# ============================================================
# CANCELLATION WORKFLOW
# ============================================================

def handle_cancellation_request(
    message,
    customer_id
):

    order_id = extract_order_id(
        message
    )

    if order_id is None:

        return {
            "response": (
                "Please provide the order number you "
                "would like to cancel."
            ),
            "tool_used": []
        }

    tools_used = []

    order = get_order_status(
        order_id,
        customer_id
    )

    tools_used.append(
        "get_order_status"
    )

    if not order.get("success"):

        return {
            "response": (
                f"I couldn't find order #{order_id}."
            ),
            "tool_used": tools_used
        }

    if order.get("customer_id") != customer_id:

        return {
            "response": (
                "I couldn't verify that this order "
                "belongs to your account."
            ),
            "tool_used": tools_used
        }

    search_company_policy(
        "cancellation policy order cancellation shipment"
    )

    tools_used.append(
        "search_company_policy"
    )

    result = cancel_order(
        order_id,
        customer_id
    )

    tools_used.append(
        "cancel_order"
    )

    return {
        "response": result.get(
            "message",
            "The cancellation request could not be completed."
        ),
        "tool_used": tools_used
    }


# ============================================================
# MAIN AUTONOMOUS SUPPORT AGENT
# ============================================================

def run_support_agent(
    message,
    customer_id=None
):

    text = message.lower().strip()

    # ========================================================
    # GENERAL POLICY QUESTIONS FIRST
    # ========================================================

    if is_refund_policy_question(text):

        return handle_policy_question(
            "refund policy eligibility refund process"
        )

    if is_return_policy_question(text):

        return handle_policy_question(
            "return policy eligibility return process"
        )

    if is_cancellation_policy_question(text):

        return handle_policy_question(
            "cancellation policy cancellation process"
        )

    # ========================================================
    # HUMAN SUPPORT
    # ========================================================

    human_keywords = [
        "speak to a human",
        "talk to a human",
        "speak with a human",
        "talk with a human",
        "human support",
        "speak to support",
        "talk to support",
        "contact support",
        "support representative",
        "customer representative",
        "speak with support",
        "talk with support",
        "real person",
        "live agent",
        "human agent"
    ]

    if (
        customer_id is not None
        and any(
            keyword in text
            for keyword in human_keywords
        )
    ):

        return {
            "response": (
                "I've created a support ticket for you "
                "and escalated your request to human support.\n\n"
                f"Ticket ID: #{result.get('ticket_id')}\n"
                f"Status: {result.get('status', 'open')}\n"
                f"Priority: {result.get('priority', 'high')}\n\n"
                "A support representative can assist you "
                "with your request."
            ),
            "tool_used": [
                "create_support_ticket"
            ],
            "escalation_required": True
        }

    # ========================================================
    # REFUND ACTION
    # ========================================================

    refund_action_phrases = [
        "get a refund",
        "get refund",
        "want a refund",
        "need a refund",
        "request a refund",
        "refund my order",
        "refund order",
        "money back",
        "give me my money back"
    ]

    if (
        customer_id is not None
        and any(
            phrase in text
            for phrase in refund_action_phrases
        )
    ):

        return handle_refund_request(
            message,
            customer_id
        )

    # ========================================================
    # CANCELLATION ACTION
    # ========================================================

    cancellation_phrases = [
        "cancel my order",
        "cancel order",
        "cancel the order",
        "want to cancel",
        "need to cancel",
        "cancel this order"
    ]

    if (
        customer_id is not None
        and any(
            phrase in text
            for phrase in cancellation_phrases
        )
    ):

        return handle_cancellation_request(
            message,
            customer_id
        )

    # ========================================================
    # RETURN ACTION
    # ========================================================

    return_action = (
        "return my order" in text
        or "return order" in text
        or "want to return" in text
        or "need to return" in text
        or "return this order" in text
    )

    if (
        customer_id is not None
        and return_action
    ):

        return handle_return_request(
            message,
            customer_id
        )

    # ========================================================
    # GENERAL LLM + TOOLS
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": message
        }
    ]

    if customer_id is not None:

        messages[0]["content"] += (
            f"\nAuthenticated customer ID: {customer_id}"
        )

    tools_used = []

    try:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # ----------------------------------------------------
        # NO TOOL REQUIRED
        # ----------------------------------------------------

        if not assistant_message.tool_calls:

            return {
                "response": assistant_message.content,
                "tool_used": []
            }

        # ----------------------------------------------------
        # EXECUTE TOOL CALLS
        # ----------------------------------------------------

        tool_results = []

        for call in assistant_message.tool_calls:

            tool_name = call.function.name

            try:

                arguments = json.loads(
                    call.function.arguments
                )

            except Exception:

                arguments = {}

            # SECURITY:
            # Never trust customer_id supplied by the AI.
            # Always use the authenticated customer's ID.

            if customer_id is not None:
                arguments["customer_id"] = customer_id

            result = execute_tool(
                tool_name,
                arguments
            )

            # --------------------------------------------------------
            # OUTPUT GUARDRAIL
            # --------------------------------------------------------
            # Never allow malformed tool output to continue through
            # the agent pipeline.
            # --------------------------------------------------------

            if not isinstance(result, dict):

                result = {
                    "success": False,
                    "error": "Tool returned an invalid response."
                }

            else:

                # Normalize missing success field.
                if "success" not in result:

                    result["success"] = False
                    result["error"] = (
                        "Tool returned an incomplete response."
                    )

                # Never expose raw internal exception details.
                if "exception" in result:

                    result.pop("exception", None)

                    result["success"] = False
                    result["error"] = (
                       "The tool encountered an internal error."
                    )

            tools_used.append(
               tool_name
            )

            tool_results.append(
                {
                    "tool": tool_name,
                    "result": result
                }
            )

        # ----------------------------------------------------
        # FINAL CUSTOMER RESPONSE
        # ----------------------------------------------------

        final_messages = list(messages)

        final_messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or ""
            }
        )

        for item in tool_results:

            final_messages.append(
                {
                    "role": "system",
                    "content": (
                        "Trusted database/tool result:\n"
                        + json.dumps(
                            item,
                            default=str
                        )
                    )
                }
            )

        final_messages.append(
            {
                "role": "system",
                "content": """
Generate the final customer-facing response.

Important:

- Never mention internal tools.
- Never mention function calls.
- Never invent information.
- Never claim an action succeeded unless the tool result
  confirms success=true.
- Use the exact database values.
- Currency is Indian Rupees.
- Display monetary amounts using ₹.
- Never convert ₹4,999 into $49.99.
- Do not invent tracking information.
- Do not invent delivery dates.
- Keep the response concise and professional.
"""
            }
        )

        final_response = client.chat.completions.create(
            model=MODEL,
            messages=final_messages,
            tool_choice="none"
        )

        return {
            "response": final_response.choices[0].message.content,
            "tool_used": tools_used
        }

    except Exception as e:

        return {
            "response": (
                "I was unable to complete this request "
                "automatically. Please allow me to escalate "
                "this request to a support representative."
            ),
            "tool_used": tools_used,
            "error": str(e)
        }

def run_agentic_support(
    message: str,
    customer_id: int = None,
    order_id: int = None,
    conversation_id: str = "default",
    troubleshooting_step: int = 1,
    previous_steps=None,
    resolved: bool = False
):
    """
    Main Agentic Customer Support Orchestrator.

    Flow:

        Customer Message
              |
        Intent Agent
              |
        Sentiment Agent
              |
        Escalation Agent
              |
        Specialized Agent
              |
        Ticket / Human Handoff
              |
        Final Response
    """

    if not message or not message.strip():

        return {
            "success": False,
            "response": "Please describe your issue.",
            "agent": "support_orchestrator",
            "execution_trace": []
        }

    message = message.strip()

    # ==========================================================
    # CONVERSATION MEMORY
    # ==========================================================

    conversation_history = []

    if customer_id is not None:

        try:

            history_result = get_conversation_history(
                customer_id=customer_id,
                conversation_id=conversation_id
            )

            if history_result.get("success", False):

                conversation_history = history_result.get(
                    "messages",
                    []
                )

        except Exception:
            conversation_history = []

        try:

            save_message(
                customer_id=customer_id,
                conversation_id=conversation_id,
                role="user",
                message=message
            )

        except Exception:
            pass

    if previous_steps is None:
        previous_steps = []

    execution_trace = []

    # ==========================================================
    # 1. INTENT AGENT
    # ==========================================================

    try:

        # Build context-aware message for intent detection
        intent_message = message

        if conversation_history:

           recent_context = []

           for item in conversation_history[-10:]:

                recent_context.append(
                   f"{item['role']}: {item['message']}"
                )

           intent_message = (
               "Conversation context:\n"
               + "\n".join(recent_context)
               + "\n\nCurrent customer message:\n"
               + message
    )

        intent_result = run_intent_agent(intent_message)

        execution_trace.append({
            "step": 1,
            "agent": "intent_agent",
            "status": "completed",
            "result": intent_result
        })

    except Exception as e:

        intent_result = {
            "success": False,
            "intent": None,
            "confidence": 0.0,
            "error": str(e)
        }

        execution_trace.append({
            "step": 1,
            "agent": "intent_agent",
            "status": "failed",
            "error": str(e)
        })

    intent = intent_result.get(
        "intent"
    )

    intent_confidence = intent_result.get(
        "confidence",
        0.0
    )

    # ==========================================================
    # 2. SENTIMENT AGENT
    # ==========================================================

    try:

        sentiment_result = run_sentiment_agent(
            message
        )

        execution_trace.append({
            "step": 2,
            "agent": "sentiment_agent",
            "status": "completed",
            "result": sentiment_result
        })

    except Exception as e:

        sentiment_result = {
            "success": False,
            "sentiment": "neutral",
            "confidence": 0.0,
            "error": str(e)
        }

        execution_trace.append({
            "step": 2,
            "agent": "sentiment_agent",
            "status": "failed",
            "error": str(e)
        })

    sentiment = sentiment_result.get(
        "sentiment"
    )

    # ==========================================================
    # 3. ESCALATION AGENT
    # ==========================================================

    try:

        escalation_result = run_escalation_agent(
            message=message,
            confidence=intent_confidence,
            intent=intent,
            sentiment=sentiment
        )

        execution_trace.append({
            "step": 3,
            "agent": "escalation_agent",
            "status": "completed",
            "result": escalation_result
        })

    except Exception as e:

        escalation_result = {
            "success": False,
            "escalation_required": True,
            "priority": "high",
            "reason": "Escalation service failed",
            "error": str(e)
        }

        execution_trace.append({
            "step": 3,
            "agent": "escalation_agent",
            "status": "failed",
            "error": str(e)
        })

    # ==========================================================
    # 4. HUMAN ESCALATION
    # ==========================================================

    if escalation_result.get(
        "escalation_required",
        False
    ):

        if customer_id is not None:

            try:

                ticket_result = run_ticket_agent(
                    customer_id=customer_id,
                    message=message,
                    category="escalation",
                    priority=escalation_result.get(
                        "priority",
                        "high"
                    ),
                    conversation_id=conversation_id
                )

                execution_trace.append({
                    "step": 4,
                    "agent": "ticket_agent",
                    "status": "completed",
                    "result": ticket_result
                })

            except Exception as e:

                ticket_result = {
                    "success": False,
                    "error": str(e)
                }

                execution_trace.append({
                    "step": 4,
                    "agent": "ticket_agent",
                    "status": "failed",
                    "error": str(e)
                })

        else:

            ticket_result = {
                "success": False,
                "message": (
                    "Customer ID is required to create "
                    "a support ticket."
                )
            }

        return {
            "success": True,
            "agent": "support_orchestrator",
            "response": (
                "I've identified that this issue should be "
                "handled by a human support representative. "
                "I've created a support request and included "
                "the relevant conversation context."
            ),
            "intent": intent,
            "sentiment": sentiment,
            "escalation": escalation_result,
            "ticket": ticket_result,
            "execution_trace": execution_trace,
            "escalation_required":True
        }

    # ==========================================================
    # 5. SPECIALIZED AGENT ROUTING
    # ==========================================================

    specialized_result = None

    # ----------------------------------------------------------
    # TECHNICAL ISSUE
    # ----------------------------------------------------------

    if intent in (
        "technical_issue",
        "technical",
        "troubleshooting"
    ):

        try:

            specialized_result = run_troubleshooting_agent(
                message=message,
                device=None,
                symptom=None,
                step=troubleshooting_step,
                previous_steps=previous_steps,
                resolved=resolved
            )

            execution_trace.append({
                "step": 4,
                "agent": "troubleshooting_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "troubleshooting_agent",
                "status": "failed",
                "error": str(e)
            })

    # ----------------------------------------------------------
    # PAYMENT / REFUND
    # ----------------------------------------------------------
    
    elif intent == "ticket_retrieval":
        try:
            ticket_result = get_customer_tickets(
                customer_id=customer_id
            )

            if ticket_result.get("success", False):

                tickets = ticket_result.get(
                    "tickets",
                    []
                )

                if not tickets:
                    response = (
                        "You do not have any support tickets."
                    )

                else:
                    ticket_lines = []

                    for ticket in tickets:
                        ticket_lines.append(
                            f"Ticket #{ticket.get('ticket_id')}: "
                            f"{ticket.get('subject')} "
                            f"(Status: {ticket.get('status')}, "
                            f"Priority: {ticket.get('priority')})"
                        )

                    response = (
                        "Here are your support tickets:\n"
                        + "\n".join(ticket_lines)
                    )

                specialized_result = {
                    "success": True,
                    "agent": "ticket_agent",
                    "response": response,
                    "ticket_count": len(tickets),
                    "tickets": tickets
                }

            else:
                specialized_result = {
                    "success": False,
                    "agent": "ticket_agent",
                    "message": (
                        "I was unable to retrieve your "
                        "support tickets."
                    )
                }

        except Exception as e:
            specialized_result = {
                "success": False,
                "agent": "ticket_agent",
                "message": (
                    "I was unable to retrieve your "
                    "support tickets."
                ),
                "error": str(e)
            }

    elif intent in (
        "payment_issue",
        "payment",
        "refund"
    ):

        try:

            # Default action
            action = "payment_status"

            message_lower = message.lower()

            # Refund requests
            if intent == "refund" or "refund" in message_lower:
                action = "refund"

            # Resolve order ID
            if order_id is None:
                order_id = intent_result.get("order_id")

            # Missing order ID
            if order_id is None:

                specialized_result = {
                    "success": False,
                    "agent": "payment_agent",
                    "action": action,
                    "message": (
                        "Please provide your order ID "
                        "so I can process your request."
                    )
                }

            else:

                specialized_result = run_payment_agent(
                    action=action,
                    order_id=order_id,
                    customer_id=customer_id,
                    reason=(
                        message
                        if action == "refund"
                        else None
                    )
                )

            execution_trace.append({
                "step": 4,
                "agent": "payment_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "agent": "payment_agent",
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "payment_agent",
                "status": "failed",
                "error": str(e)
            })


    # ----------------------------------------------------------
    # RETURN REQUEST
    # ----------------------------------------------------------

    elif intent == "return":

        try:

            specialized_result = handle_return_request(
                message=message,
                customer_id=customer_id
            )

            execution_trace.append({
                "step": 4,
                "agent": "return_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "agent": "return_agent",
                "action": "return",
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "return_agent",
                "status": "failed",
                "error": str(e)
            })

    # ----------------------------------------------------------
    # ORDER RELATED
    # ----------------------------------------------------------

    elif intent in (
        "order_tracking",
        "order_status",
        "order_issue"
    ):

        try:

            if order_id is None:

                order_id = intent_result.get(
                    "order_id"
                )

            if order_id is None:

                specialized_result = {
                    "success": False,
                    "agent": "order_agent",
                    "message": (
                        "Please provide your order ID "
                        "so I can check the order."
                    )
                }

            else:

                specialized_result = run_order_agent(
                    action="status",
                    order_id=order_id,
                    customer_id=customer_id,
                    conversation_id=conversation_id
                )

            execution_trace.append({
                "step": 4,
                "agent": "order_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "order_agent",
                "status": "failed",
                "error": str(e)
            })

    # ----------------------------------------------------------
    # ORDER CANCELLATION
    # ----------------------------------------------------------

    elif intent == "cancellation":

        try:

            if order_id is None:

                order_id = intent_result.get(
                    "order_id"
                )

            if order_id is None:

                specialized_result = {
                    "success": False,
                    "agent": "cancellation_agent",
                    "action": "cancel",
                    "message": (
                        "Please provide your order ID "
                        "so I can process the cancellation."
                    )
                }

            else:

                specialized_result = cancel_order(
                    order_id=order_id,
                    customer_id=customer_id,
                    conversation_id=conversation_id
                )

            execution_trace.append({
                "step": 4,
                "agent": "cancellation_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "agent": "order_agent",
                "action": "cancel",
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "order_agent",
                "status": "failed",
                "error": str(e)
            })
            
    # ----------------------------------------------------------
    # GENERAL / CASUAL CONVERSATION
    # ----------------------------------------------------------

    elif intent == "general":

        specialized_result = {
            "success": True,
            "agent": "general_agent",
            "response": (
                "Sure! Here's a dinosaur joke: "
                "Why can't you hear a pterodactyl go to the bathroom? "
                "Because the P is silent!"
            )
        }

        execution_trace.append({
            "step": 4,
            "agent": "general_agent",
            "status": "completed",
            "result": specialized_result
        })        

    # ----------------------------------------------------------
    # KNOWLEDGE / POLICY / PRODUCT QUESTION
    # ----------------------------------------------------------

    elif intent in (
        "product_question",
        "policy_question",
        "knowledge",
        "faq"
    ):

        try:

            specialized_result = run_knowledge_agent(
                query=message,
                top_k=3
            )

            execution_trace.append({
                "step": 4,
                "agent": "knowledge_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "knowledge_agent",
                "status": "failed",
                "error": str(e)
            })

    # ==========================================================
    # 6. FALLBACK TO KNOWLEDGE AGENT
    # ==========================================================

    if specialized_result is None:

        try:

            specialized_result = run_knowledge_agent(
                query=message,
                top_k=3
            )

            execution_trace.append({
                "step": 4,
                "agent": "knowledge_agent",
                "status": "completed",
                "result": specialized_result
            })

        except Exception as e:

            specialized_result = {
                "success": False,
                "error": str(e)
            }

            execution_trace.append({
                "step": 4,
                "agent": "knowledge_agent",
                "status": "failed",
                "error": str(e)
            })

    # ==========================================================
    # 7. HANDLE SPECIALIZED AGENT FAILURE / BUSINESS OUTCOME
    # ==========================================================

    # ==========================================================
    # 7A. HANDLE CANCELLATION BUSINESS OUTCOMES
    # ==========================================================

    if (
        intent == "cancellation"
        and specialized_result is not None
        and not specialized_result.get("success", False)
    ):

        cancellation_status = (
            specialized_result.get("status") or ""
        ).lower()

        cancellation_message = (
            specialized_result.get("message")
            or "The order could not be cancelled."
        )

        # ------------------------------------------------------
        # Already cancelled
        # ------------------------------------------------------

        if cancellation_status == "cancelled":

            response = cancellation_message

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "completed",
                "event": "Cancellation business outcome handled",
                "outcome": "already_cancelled"
            })

            if customer_id is not None:
                try:
                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )
                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "cancellation_agent"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": False
            }

        # ------------------------------------------------------
        # Out for delivery
        # ------------------------------------------------------

        if cancellation_status == "out_for_delivery":

            response = (
                f"Order #{order_id} is already out for delivery "
                "and cannot be cancelled automatically. "
                "I'll escalate this to human support for further assistance."
            )

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "escalated",
                "event": "Cancellation requires human support",
                "reason": "Order is out for delivery"
            })

            if customer_id is not None:
                try:
                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )
                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "cancellation_agent"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": True
            }

    if not specialized_result.get(
        "success",
        False
    ):

        # ------------------------------------------------------
        # CANCELLATION BUSINESS OUTCOMES
        # ------------------------------------------------------
        # These are NOT technical failures.
        # cancel_order() uses success=False for rejected
        # business operations such as already cancelled,
        # delivered, out-for-delivery, or unauthorized orders.
        # ------------------------------------------------------

        if intent == "cancellation":

            cancellation_message = specialized_result.get(
                "message"
            )

            if cancellation_message:

                response = cancellation_message

                execution_trace.append({
                    "step": 5,
                    "agent": "support_orchestrator",
                    "status": "completed",
                    "event": "Cancellation business outcome handled"
                })

                # Save assistant response
                if customer_id is not None:

                    try:

                        save_message(
                            customer_id=customer_id,
                            conversation_id=conversation_id,
                            role="assistant",
                            message=response
                        )

                    except Exception:
                        pass

                return {
                    "success": True,
                    "agent": "support_orchestrator",
                    "response": response,
                    "intent": intent,
                    "sentiment": sentiment,
                    "conversation_id": conversation_id,
                    "conversation_history_count": len(
                        conversation_history
                    ),
                    "specialized_agent": specialized_result.get(
                        "agent",
                        "cancellation_agent"
                    ),
                    "specialized_result": specialized_result,
                    "execution_trace": execution_trace,
                    "escalation_required": False
                }

        
        # ------------------------------------------------------
        # RETURN BUSINESS OUTCOMES
        # ------------------------------------------------------
        # Authorization failures are expected business outcomes,
        # not technical/system failures.
        # Do not escalate when the customer is trying to
        # access another customer's return.
        # ------------------------------------------------------

        if (
            specialized_result.get("agent") == "return_agent"
            and specialized_result.get("response")
        ):

            return_message = specialized_result.get(
                "response"
            )

            response = return_message

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "completed",
                "event": "Return business outcome handled"
            })

            # Save assistant response
            if customer_id is not None:

                try:

                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )

                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "return_agent"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": False
            }

        # ------------------------------------------------------
        # PAYMENT BUSINESS OUTCOMES
        # ------------------------------------------------------
        # Authorization failures are expected business outcomes,
        # not technical/system failures.
        # Do not escalate when the customer is trying to
        # access another customer's payment information.
        # ------------------------------------------------------

        if (
            specialized_result.get("agent") == "payment_agent"
            and specialized_result.get("message")
        ):

            payment_message = specialized_result.get(
                "message"
            )

            response = payment_message

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "completed",
                "event": "Payment business outcome handled"
            })

            if customer_id is not None:
                try:
                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )
                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "payment_agent"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": False
            }

        # ------------------------------------------------------
        # EXISTING REFUND REQUEST
        # ------------------------------------------------------

        if (
            specialized_result.get("agent") == "payment_agent"
            and specialized_result.get("action") == "refund"
            and not specialized_result.get("success",False)
            and specialized_result.get("refund_id") is not None
            and specialized_result.get("refund_reference")
        ):

            refund_reference = specialized_result.get(
                "refund_reference"
            )

            refund_amount = specialized_result.get(
                "amount"
            )

            refund_status = specialized_result.get(
                "refund_status",
                "requested"
            )

            response = (
                f"A refund request for order #{order_id} "
                f"has already been created. "
                f"Refund reference: {refund_reference}. "
            )

            if refund_amount is not None:
                response += (
                    f"Refund amount: ₹{refund_amount:.2f}. "
                )

            response += (
                f"Current status: {refund_status}."
            )

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "completed",
                "event": "Existing refund request identified"
            })

            # Save assistant response
            if customer_id is not None:

                try:

                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )

                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "support_orchestrator"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": specialized_result.get(
                    "escalation_required",
                    False
                )
            }
            
        # ------------------------------------------------------
        # REFUND BUSINESS OUTCOMES
        # ------------------------------------------------------
        # These are NOT technical failures.
        # payment_agent uses success=False for rejected
        # business operations such as:
        # - unauthorized order
        # - existing refund
        # - ineligible refund
        # ------------------------------------------------------

        if intent == "refund":

            refund_message = specialized_result.get(
                "message"
            )

            if refund_message:

                response = refund_message

                execution_trace.append({
                    "step": 5,
                    "agent": "support_orchestrator",
                    "status": "completed",
                    "event": "Refund business outcome handled"
                })

                # Save assistant response
                if customer_id is not None:

                    try:

                        save_message(
                            customer_id=customer_id,
                            conversation_id=conversation_id,
                            role="assistant",
                            message=response
                        )

                    except Exception:
                        pass

                return {
                    "success": True,
                    "agent": "support_orchestrator",
                    "response": response,
                    "intent": intent,
                    "sentiment": sentiment,
                    "conversation_id": conversation_id,
                    "conversation_history_count": len(
                        conversation_history
                    ),
                    "specialized_agent": specialized_result.get(
                        "agent"
                    ),
                    "specialized_result": specialized_result,
                    "execution_trace": execution_trace,
                    "escalation_required": False
                }
             
        # ------------------------------------------------------
        # ORDER BUSINESS OUTCOMES
        # ------------------------------------------------------
        # Authorization failures are expected business outcomes,
        # not technical/system failures.
        # Do not escalate when the customer is simply trying to
        # access another customer's order.
        # ------------------------------------------------------

        if (
            specialized_result.get("agent") == "order_agent"
            and specialized_result.get("message")
        ):

            order_message = specialized_result.get(
                "message"
            )

            response = order_message

            execution_trace.append({
                "step": 5,
                "agent": "support_orchestrator",
                "status": "completed",
                "event": "Order business outcome handled"
            })

            # Save assistant response
            if customer_id is not None:

                try:

                    save_message(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        role="assistant",
                        message=response
                    )

                except Exception:
                    pass

            return {
                "success": True,
                "agent": "support_orchestrator",
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "conversation_id": conversation_id,
                "conversation_history_count": len(
                    conversation_history
                ),
                "specialized_agent": specialized_result.get(
                    "agent",
                    "order_agent"
                ),
                "specialized_result": specialized_result,
                "execution_trace": execution_trace,
                "escalation_required": False
            }   

        # ------------------------------------------------------
        # GENUINE SPECIALIZED-AGENT FAILURE
        # ------------------------------------------------------

        return {
            "success": False,
            "agent": "support_orchestrator",
            "response": (
                "I wasn't able to complete this request "
                "reliably. I recommend escalating this "
                "issue to human support."
            ),
            "intent": intent,
            "sentiment": sentiment,
            "specialized_agent": specialized_result.get(
                "agent"
            ),
            "specialized_result": specialized_result,
            "execution_trace": execution_trace,
            "escalation_required": True
        }

    # ==========================================================
    # 8. FINAL RESPONSE
    # ==========================================================

    response = specialized_result.get(
        "response"
    )

    if not response:

        response = specialized_result.get(
            "answer"
        )

    if not response:

        response = specialized_result.get(
            "message"
        )

    if not response:

        response = (
            "I found information relevant to your request."
        )

    execution_trace.append({
        "step": 5,
        "agent": "support_orchestrator",
        "status": "completed",
        "event": "Final response generated"
    })

    # Save assistant response to conversation memory
    if customer_id is not None:

        try:

            save_message(
                customer_id=customer_id,
                conversation_id=conversation_id,
                role="assistant",
                message=response
            )

        except Exception:
            pass

    return {
        "success": True,
        "agent": "support_orchestrator",
        "response": response,
        "intent": intent,
        "sentiment": sentiment,
        "conversation_id": conversation_id,
        "conversation_history_count": len(conversation_history),
        "specialized_agent": specialized_result.get(
            "agent"
        ),
        "specialized_result": specialized_result,
        # RAG provenance
        "sources": specialized_result.get(
            "sources",
            []
        ),

        "provenance": specialized_result.get(
            "provenance",
            {}
        ),

        "retrieved_documents": specialized_result.get(
            "retrieved_documents",
            0
        ),
        
        "execution_trace": execution_trace,
        "escalation_required": specialized_result.get(
            "escalation_required",
            False
        )
    }


