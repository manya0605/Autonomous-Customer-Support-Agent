from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from backend.app.database.database import engine
from backend.app.models import Customer
from backend.app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# REQUEST MODELS
# ============================================================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: str | None = None
    address: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ============================================================
# REGISTER
# ============================================================

@router.post("/register")
def register(request: RegisterRequest):

    with Session(engine) as session:

        existing_customer = session.exec(
            select(Customer).where(
                Customer.email == request.email
            )
        ).first()

        if existing_customer:

            raise HTTPException(
                status_code=400,
                detail="Email is already registered"
            )

        customer = Customer(
            name=request.name,
            email=request.email,
            password_hash=hash_password(
                request.password
            ),
            phone=request.phone,
            address=request.address,
            is_active=True
        )

        session.add(customer)
        session.commit()
        session.refresh(customer)

        return {
            "message": "Customer registered successfully",
            "customer_id": customer.id,
            "email": customer.email
        }


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(request: LoginRequest):

    with Session(engine) as session:

        customer = session.exec(
            select(Customer).where(
                Customer.email == request.email
            )
        ).first()

        if not customer:

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not customer.is_active:

            raise HTTPException(
                status_code=403,
                detail="Customer account is inactive"
            )

        # Existing customers currently have no password.
        if not customer.password_hash:

            raise HTTPException(
                status_code=400,
                detail=(
                    "This customer account does not have "
                    "a password configured."
                )
            )

        if not verify_password(
            request.password,
            customer.password_hash
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        token = create_access_token(
            customer.id
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "customer_id": customer.id
        }