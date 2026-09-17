from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.agents.support_agent import run_agentic_support
from backend.app.models import Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/agent",
    tags=["Autonomous Agent"]
)


class AgentRequest(BaseModel):
    message: str
    conversation_id: str = "default"
    order_id: int | None = None


@router.post("/chat")
def agent_chat(
    request: AgentRequest,
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    try:

        # The customer ID MUST come from the
        # authenticated JWT, not from the request body.
        result = run_agentic_support(
            message=request.message,
            customer_id=current_customer.id,
            order_id=request.order_id,
            conversation_id=request.conversation_id
        )

        response = result.get(
            "response",
            "I was unable to process your request."
        )

        return {
            "success": result.get("success", False),
            "response": response,
            "conversation_id": result.get(
                "conversation_id",
                request.conversation_id
            ),
            "intent": result.get("intent"),
            "agent": result.get(
                "specialized_agent"
                or
                "support_orchestrator"
            ),
            "escalation_required": result.get(
                "escalation_required",
                False
            ),
            "customer_id": current_customer.id
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Autonomous support agent failed"
        )