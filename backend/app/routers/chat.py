from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.app.core.ai import client, MODEL
from backend.app.models import Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/chat",
    tags=["AI Support Agent"]
)


class ChatRequest(BaseModel):
    message: str


@router.post("")
def chat(
    request: ChatRequest,
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
You are an intelligent customer support assistant.

Your responsibilities:
- Understand customer questions.
- Be helpful and professional.
- Never invent order, payment, or customer information.
- Ask for required information when necessary.
- Keep responses clear and concise.
"""
                },
                {
                    "role": "user",
                    "content": request.message
                }
            ]
        )

        return {
            "response": response.choices[0].message.content,
            "customer_id": current_customer.id
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="AI support service failed"
        )