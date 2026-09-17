import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from backend.app.database.database import engine
from backend.app.models import Customer
from backend.app.core.security import decode_access_token


# ============================================================
# JWT BEARER AUTHENTICATION
# ============================================================

security = HTTPBearer()


# ============================================================
# GET CURRENT CUSTOMER
# ============================================================

def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Customer:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    token = credentials.credentials

    try:

        payload = decode_access_token(token)

        customer_id = payload.get("sub")

        if customer_id is None:
            raise credentials_exception

        customer_id = int(customer_id)

    except (
        ValueError,
        TypeError,
        jwt.InvalidTokenError
    ):
        raise credentials_exception

    with Session(engine) as session:

        customer = session.get(
            Customer,
            customer_id
        )

        if customer is None:
            raise credentials_exception

        if not customer.is_active:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customer account is inactive"
            )

        return customer