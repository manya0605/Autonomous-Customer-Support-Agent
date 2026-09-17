from backend.app.tools.order_tools import get_order_status
from backend.app.tools.payment_tools import get_payment_status
from backend.app.tools.return_tools import get_return_status
from backend.app.tools.ticket_tools import get_customer_tickets


def test_customer_can_access_own_order():
    result = get_order_status(
        order_id=1,
        customer_id=1
    )

    assert result["success"] is True
    assert result["order_id"] == 1


def test_customer_cannot_access_another_customers_order():
    result = get_order_status(
        order_id=2,
        customer_id=1
    )

    assert result["success"] is False
    assert "own order" in result["error"].lower()


def test_customer_cannot_access_another_customers_payment():
    result = get_payment_status(
        order_id=2,
        customer_id=1
    )

    assert result["success"] is False
    assert "own payment" in result["error"].lower()


def test_customer_cannot_access_another_customers_return():
    result = get_return_status(
        order_id=2,
        customer_id=1
    )

    assert result["success"] is False
    assert "own return" in result["error"].lower()


def test_customer_ticket_isolation():
    result = get_customer_tickets(
        customer_id=1
    )

    assert result["success"] is True
    assert result["customer_id"] == 1

    for ticket in result["tickets"]:
        # Every returned ticket must belong to customer 1.
        # This protects against cross-customer data leakage.
        assert ticket["ticket_id"] is not None
        assert ticket["customer_id"] == 1