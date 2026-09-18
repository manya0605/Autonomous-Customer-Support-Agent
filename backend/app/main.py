import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.database.database import create_db_and_tables

from backend.app.models import (
    Customer,
    Product,
    Order,
    Payment,
    SupportTicket,
    ReturnRequest,
)

from backend.app.routers.customer import router as customer_router
from backend.app.routers.order import router as order_router
from backend.app.routers.payment import router as payment_router
from backend.app.routers.return_request import router as return_router
from backend.app.routers.ticket import router as ticket_router
from backend.app.routers.chat import router as chat_router
from backend.app.routers.agent import router as agent_router
from backend.app.routers.auth import router as auth_router


app = FastAPI(
    title="Autonomous AI Customer Support & Resolution Agent",
    description="Agentic AI platform for autonomous customer support",
    version="1.0.0"
)


# ==================================================
# CORS CONFIGURATION
# ==================================================
# Allows the frontend running on port 5500
# to communicate with the FastAPI backend on port 8000.

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
os.getenv("FRONTEND_URL",""),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(customer_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(return_router)
app.include_router(ticket_router)
app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Autonomous AI Customer Support Agent is running",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }