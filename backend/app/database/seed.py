from sqlmodel import Session

from backend.app.database.database import engine, create_db_and_tables
from backend.app.models import (
    Customer,
    Product,
    Order,
    Payment,
    SupportTicket,
    ReturnRequest,
)
from backend.app.core.security import hash_password


def seed_database():

    create_db_and_tables()

    with Session(engine) as session:

        # Prevent duplicate seed data
        existing_customer = session.query(Customer).first()

        if existing_customer:
            print("Database already contains data.")
            return

        # ==========================================
        # CUSTOMERS
        # ==========================================

        customers = [
            Customer(
                name="Manya Sharma",
                email="manya@example.com",
                password_hash=hash_password("Test1234"),
                phone="+91-9876543210",
                address="Mysuru, Karnataka",
                is_active=True
            ),

            Customer(
                name="Rahul Kumar",
                email="rahul@example.com",
                password_hash=hash_password("Test1234"),
                phone="+91-9876543211",
                address="Bengaluru, Karnataka",
                is_active=True
            ),

            Customer(
                name="Ananya Rao",
                email="ananya@example.com",
                password_hash=hash_password("Test1234"),
                phone="+91-9876543212",
                address="Chennai, Tamil Nadu",
                is_active=True
            ),
        ]

        for customer in customers:
            session.add(customer)

        session.commit()

        # Refresh IDs
        for customer in customers:
            session.refresh(customer)

        # ==========================================
        # PRODUCTS
        # ==========================================

        products = [
            Product(
                name="Wireless Headphones",
                description="Noise cancelling wireless headphones",
                price=4999.0,
                stock_quantity=50
            ),

            Product(
                name="Smart Watch",
                description="Fitness and health tracking smartwatch",
                price=6999.0,
                stock_quantity=30
            ),

            Product(
                name="Mechanical Keyboard",
                description="RGB mechanical gaming keyboard",
                price=3499.0,
                stock_quantity=40
            ),

            Product(
                name="Wireless Mouse",
                description="Ergonomic wireless mouse",
                price=1499.0,
                stock_quantity=100
            ),
        ]

        for product in products:
            session.add(product)

        session.commit()

        for product in products:
            session.refresh(product)

        # ==========================================
        # ORDERS
        # ==========================================

        orders = [
            Order(
                customer_id=customers[0].id,
                product_id=products[0].id,
                quantity=1,
                total_amount=4999.0,
                status="delayed",
                shipping_address=customers[0].address
            ),

            Order(
                customer_id=customers[1].id,
                product_id=products[1].id,
                quantity=1,
                total_amount=6999.0,
                status="out_for_delivery",
                shipping_address=customers[1].address
            ),

            Order(
                customer_id=customers[2].id,
                product_id=products[2].id,
                quantity=1,
                total_amount=3499.0,
                status="delivered",
                shipping_address=customers[2].address
            ),
        ]

        for order in orders:
            session.add(order)

        session.commit()

        for order in orders:
            session.refresh(order)

        # ==========================================
        # PAYMENTS
        # ==========================================

        payments = [
            Payment(
                order_id=orders[0].id,
                amount=4999.0,
                payment_method="UPI",
                status="successful",
                transaction_id="TXN10001"
            ),

            Payment(
                order_id=orders[1].id,
                amount=6999.0,
                payment_method="Credit Card",
                status="successful",
                transaction_id="TXN10002"
            ),

            Payment(
                order_id=orders[2].id,
                amount=3499.0,
                payment_method="UPI",
                status="successful",
                transaction_id="TXN10003"
            ),
        ]

        for payment in payments:
            session.add(payment)

        # ==========================================
        # SUPPORT TICKETS
        # ==========================================

        tickets = [
            SupportTicket(
                customer_id=customers[0].id,
                subject="Order delivery delayed",
                description="Customer has not received the order yet.",
                category="order",
                priority="high",
                status="open"
            ),

            SupportTicket(
                customer_id=customers[1].id,
                subject="Payment confirmation",
                description="Customer wants to confirm payment status.",
                category="payment",
                priority="medium",
                status="open"
            ),
        ]

        for ticket in tickets:
            session.add(ticket)

        # ==========================================
        # RETURN REQUEST
        # ==========================================

        return_request = ReturnRequest(
            order_id=orders[2].id,
            customer_id=customers[2].id,
            reason="Product does not meet expectations",
            status="requested",
            refund_amount=3499.0
        )

        session.add(return_request)

        session.commit()

        print("===================================")
        print("DATABASE SEEDED SUCCESSFULLY")
        print("===================================")
        print(f"Customers: {len(customers)}")
        print(f"Products: {len(products)}")
        print(f"Orders: {len(orders)}")
        print(f"Payments: {len(payments)}")
        print(f"Tickets: {len(tickets)}")
        print("Returns: 1")


if __name__ == "__main__":
    seed_database()