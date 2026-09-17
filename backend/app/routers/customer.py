from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.app.database.database import engine
from backend.app.models import Customer
from backend.app.core.dependencies import get_current_customer


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


# ==================================================
# CURRENT CUSTOMER PROFILE
# ==================================================

@router.get("/me")
def get_my_profile(
    current_customer: Customer = Depends(
        get_current_customer
    )
):
    return {
        "id": current_customer.id,
        "name": current_customer.name,
        "email": current_customer.email,
        "phone": current_customer.phone,
        "address": current_customer.address,
        "is_active": current_customer.is_active
    }


# ==================================================
# GET CUSTOMER BY ID
# ==================================================

@router.get("/{customer_id}")
def get_customer(
    customer_id: int,
    current_customer: Customer = Depends(
        get_current_customer
    )
):

    if current_customer.id != customer_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own customer profile"
        )

    with Session(engine) as session:

        customer = session.get(
            Customer,
            customer_id
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer not found"
            )

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address,
            "is_active": customer.is_active
        }