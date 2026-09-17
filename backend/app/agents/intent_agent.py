import re


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def _normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text


# ============================================================
# ORDER ID DETECTION
# ============================================================

def detect_order_id(text: str):
    """
    Extract order IDs from messages such as:

        order #123
        order 123
        order number 123
        order no 123
        order id 123
        #123
    """

    if not text:
        return None

    patterns = [
        r"\border\s*(?:#|number|no\.?|id)?\s*(\d+)\b",
        r"#\s*(\d+)\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None

    return None


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(message: str) -> dict:

    text = _normalize(message)

    if not text:

        return {
            "success": False,
            "agent": "intent_agent",
            "intent": "general",
            "confidence": 0.0,
            "requires_order": False,
            "order_id": None
        }

    order_id = detect_order_id(text)

    # ========================================================
    # 1. EXPLICIT HUMAN SUPPORT
    # ========================================================

    human_phrases = [
        "speak to a human",
        "talk to a human",
        "speak with a human",
        "talk with a human",
        "human support",
        "speak to support",
        "talk to support",
        "live agent",
        "human agent",
        "real person",
        "customer representative",
        "speak to an agent",
        "talk to an agent",
        "connect me to support"
    ]

    if any(
        phrase in text
        for phrase in human_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "complaint",
            "confidence": 0.95,
            "requires_order": order_id is not None,
            "order_id": order_id
        }

    # ========================================================
    # 2. POLICY / KNOWLEDGE QUESTIONS
    # ========================================================
    #
    # IMPORTANT:
    # This section MUST appear before refund / cancellation /
    # return action detection.
    #
    # Examples:
    #
    # "What is your return policy?"
    # "What is your refund policy?"
    # "How long do I have to return?"
    # "What are the return requirements?"
    #
    # These are informational questions and should go to the
    # knowledge/RAG agent instead of creating a ticket or
    # performing an action.
    # ========================================================

    policy_phrases = [

        # ----------------------------------------------------
        # RETURN POLICY
        # ----------------------------------------------------

        "what is your return policy",
        "what's your return policy",
        "what is the return policy",
        "what's the return policy",
        "return policy",
        "return policies",

        # ----------------------------------------------------
        # REFUND POLICY
        # ----------------------------------------------------

        "what is your refund policy",
        "what's your refund policy",
        "what is the refund policy",
        "what's the refund policy",
        "refund policy",
        "refund policies",

        # ----------------------------------------------------
        # CANCELLATION POLICY
        # ----------------------------------------------------

        "what is your cancellation policy",
        "what's your cancellation policy",
        "what is the cancellation policy",
        "what's the cancellation policy",
        "cancellation policy",
        "cancellation policies",

        # ----------------------------------------------------
        # SHIPPING / DELIVERY POLICY
        # ----------------------------------------------------

        "what is your shipping policy",
        "what's your shipping policy",
        "what is the shipping policy",
        "what's the shipping policy",
        "shipping policy",
        "shipping policies",

        "what is your delivery policy",
        "what's your delivery policy",
        "what is the delivery policy",
        "what's the delivery policy",
        "delivery policy",
        "delivery policies",

        # ----------------------------------------------------
        # RETURN WINDOW / REFUND WINDOW
        # ----------------------------------------------------

        "how long do i have to return",
        "how long can i return",
        "how long do i have to get a refund",
        "how long can i get a refund",
        "how long do i have to request a refund",
        "how long do i have to cancel",
        "how long can i cancel",
        "return window",
        "refund window",
        "return period",
        "refund period",
        "cancellation period",

        # ----------------------------------------------------
        # RETURN REQUIREMENTS / RULES
        # ----------------------------------------------------

        "are returns free",
        "can products be returned",
        "what are the return requirements",
        "what are the refund requirements",
        "what are the cancellation rules",
        "what are the return rules",
        "what are the refund rules",
        "what are the return conditions",
        "what are the refund conditions",
        "what are the cancellation requirements",

        # ----------------------------------------------------
        # GENERAL POLICY QUESTIONS
        # ----------------------------------------------------

        "what are your policies",
        "what is your policy",
        "what are the rules",
        "what are your rules",
        "what are the requirements",
        "what is the eligibility",
        "what are the eligibility requirements",
        "what are the terms",
        "terms and conditions"
    ]

    if any(
        phrase in text
        for phrase in policy_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "policy_question",
            "confidence": 0.95,
            "requires_order": False,
            "order_id": order_id
        }

    # --------------------------------------------------------
    # POLICY DETECTION USING KEYWORD COMBINATIONS
    # --------------------------------------------------------
    #
    # This catches variations not explicitly listed above.
    #
    # Example:
    #
    # "What are the rules for returning a product?"
    #
    # policy keyword + return domain
    #
    # -> policy_question
    # --------------------------------------------------------

    policy_keywords = [
        "policy",
        "policies",
        "rules",
        "eligibility",
        "requirements",
        "terms",
        "how long do i have",
        "return window",
        "refund window",
        "return period",
        "refund period"
    ]

    policy_domains = [
        "return",
        "refund",
        "cancel",
        "cancellation",
        "shipping",
        "delivery",
        "exchange"
    ]

    has_policy_keyword = any(
        keyword in text
        for keyword in policy_keywords
    )

    has_policy_domain = any(
        domain in text
        for domain in policy_domains
    )

    if (
        has_policy_keyword
        and has_policy_domain
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "policy_question",
            "confidence": 0.95,
            "requires_order": False,
            "order_id": order_id
        }

    # ========================================================
    # 3. REFUND
    # ========================================================
    # Refund MUST be checked before generic payment.
    #
    # These are ACTION requests, not policy questions.
    #
    # Example:
    #
    # "I want a refund for order #123"
    #
    # -> refund
    # ========================================================

    refund_phrases = [
        "refund",
        "money back",
        "get my money back",
        "want my money back",
        "request a refund",
        "need a refund",
        "want a refund",
        "refund my order",
        "request money back"
    ]

    if any(
        phrase in text
        for phrase in refund_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "refund",
            "confidence": 0.95,
            "requires_order": True,
            "order_id": order_id
        }

    # ========================================================
    # 4. CANCELLATION
    # ========================================================

    cancellation_phrases = [
        "cancel my order",
        "cancel the order",
        "cancel order",
        "want to cancel",
        "need to cancel",
        "cancel this order",
        "i want to cancel",
        "please cancel"
    ]

    if any(
        phrase in text
        for phrase in cancellation_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "cancellation",
            "confidence": 0.95,
            "requires_order": True,
            "order_id": order_id
        }

    # ========================================================
    # 5. RETURN
    # ========================================================

    return_phrases = [
        "return my order",
        "return the order",
        "return order",
        "want to return",
        "need to return",
        "return this order",
        "return the product",
        "return product",
        "send it back",
        "send the product back",
        "i want to return",
        "i need to return",
        "please return",
        "request a return",
        "request return",
        "create a return",
        "start a return",
        "initiate a return"
    ]

    if any(
        phrase in text
        for phrase in return_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "return",
            "confidence": 0.95,
            "requires_order": True,
            "order_id": order_id
        }

    # ========================================================
    # 6. SUPPORT TICKET RETRIEVAL
    # ========================================================
    #
    # Examples:
    # "Show me my support tickets"
    # "Show my tickets"
    # "What are my support tickets?"
    # "List my support tickets"
    # "Check my support tickets"
    # ========================================================

    ticket_retrieval_phrases = [
        "show me my support tickets",
        "show my support tickets",
        "show me my tickets",
        "show my tickets",
        "what are my support tickets",
        "what are my tickets",
        "list my support tickets",
        "list my tickets",
        "check my support tickets",
        "check my tickets",
        "view my support tickets",
        "view my tickets",
        "my support tickets",
        "my tickets"
    ]

    if any(
        phrase in text
        for phrase in ticket_retrieval_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "ticket_retrieval",
            "confidence": 0.95,
            "requires_order": False,
            "order_id": None
        }

    # ========================================================
    # 7. PAYMENT
    # ========================================================
    #
    # IMPORTANT:
    # This uses keyword combinations instead of only exact
    # phrases.
    #
    # Example:
    # "Was my payment for order #1 successful?"
    #
    # contains:
    # payment + successful
    #
    # Therefore -> payment_issue
    # ========================================================

    payment_keywords = [
        "payment",
        "transaction",
        "charged",
        "charge",
        "money deducted",
        "amount deducted",
        "money was deducted",
        "amount was deducted"
    ]

    payment_status_words = [
        "successful",
        "success",
        "failed",
        "failure",
        "pending",
        "completed",
        "complete",
        "declined",
        "status",
        "went through",
        "go through",
        "not completed",
        "unsuccessful"
    ]

    has_payment_keyword = any(
        keyword in text
        for keyword in payment_keywords
    )

    has_payment_status_word = any(
        word in text
        for word in payment_status_words
    )

    # Normal payment/status questions
    if (
        has_payment_keyword
        and has_payment_status_word
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "payment_issue",
            "confidence": 0.95,
            "requires_order": order_id is not None,
            "order_id": order_id
        }

    # Payment questions without explicit status words
    payment_question_phrases = [
        "did i pay",
        "did i make a payment",
        "have i paid",
        "was i charged",
        "was i billed",
        "check my payment",
        "check the payment",
        "check payment",
        "payment details",
        "payment information",
        "transaction details",
        "transaction information"
    ]

    if any(
        phrase in text
        for phrase in payment_question_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "payment_issue",
            "confidence": 0.92,
            "requires_order": order_id is not None,
            "order_id": order_id
        }

    # Double-charge detection
    double_charge_phrases = [
        "charged twice",
        "double charged",
        "charged two times",
        "charged multiple times",
        "charged more than once"
    ]

    if any(
        phrase in text
        for phrase in double_charge_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "payment_issue",
            "confidence": 0.95,
            "requires_order": order_id is not None,
            "order_id": order_id
        }

    # ========================================================
    # 7. ORDER TRACKING
    # ========================================================

    order_tracking_phrases = [
        "where is my order",
        "where is the order",
        "where's my order",
        "track my order",
        "track the order",
        "order tracking",
        "track order",
        "order status",
        "status of my order",
        "status of the order",
        "check my order",
        "check the order",
        "order delayed",
        "my order is delayed",
        "order has been delayed",
        "order hasn't arrived",
        "order has not arrived",
        "my order has not arrived",
        "my order hasn't arrived",
        "where can i find my order",
        "when will my order arrive",
        "when is my order arriving",
        "delivery status",
        "delivery update"
    ]

    if any(
        phrase in text
        for phrase in order_tracking_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "order_tracking",
            "confidence": 0.95,
            "requires_order": True,
            "order_id": order_id
        }

    # ========================================================
    # 8. ORDER TRACKING FALLBACK
    # ========================================================

    has_order_word = (
        "order" in text
        or "delivery" in text
        or "shipment" in text
    )

    tracking_words = [
        "where",
        "track",
        "tracking",
        "status",
        "delayed",
        "delay",
        "arrive",
        "arrived",
        "delivery",
        "shipped",
        "shipping"
    ]

    if (
        has_order_word
        and any(
            word in text
            for word in tracking_words
        )
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "order_tracking",
            "confidence": 0.90,
            "requires_order": True,
            "order_id": order_id
        }

    # ========================================================
    # 9. PRODUCT QUESTION
    # ========================================================

    product_phrases = [
        "product information",
        "product details",
        "tell me about the product",
        "product question",
        "product features",
        "product specification",
        "product specifications",
        "does this product",
        "is this product",
        "how does this product work",
        "manual",
        "warranty"
    ]

    if any(
        phrase in text
        for phrase in product_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "product_question",
            "confidence": 0.90,
            "requires_order": False,
            "order_id": order_id
        }

    # ========================================================
    # 10. TECHNICAL ISSUE
    # ========================================================

    technical_words = [
        "router",
        "wifi",
        "wi-fi",
        "internet",
        "laptop",
        "computer",
        "desktop",
        "printer",
        "phone",
        "mobile",
        "headphone",
        "headphones",
        "earbuds",
        "television",
        "tv",
        "monitor",
        "screen",
        "not working",
        "doesn't work",
        "does not work",
        "not responding",
        "not connecting",
        "disconnecting",
        "disconnected",
        "overheating",
        "slow",
        "freezing",
        "frozen",
        "error",
        "won't turn on",
        "not turning on"
    ]

    if any(
        phrase in text
        for phrase in technical_words
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "technical_issue",
            "confidence": 0.90,
            "requires_order": False,
            "order_id": order_id
        }

    # ========================================================
    # 11. ACCOUNT ISSUE
    # ========================================================

    account_phrases = [
        "account problem",
        "account issue",
        "can't login",
        "cannot login",
        "unable to login",
        "login problem",
        "login issue",
        "password problem",
        "forgot password",
        "account locked",
        "change my password",
        "update my account",
        "profile problem"
    ]

    if any(
        phrase in text
        for phrase in account_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "account_issue",
            "confidence": 0.90,
            "requires_order": False,
            "order_id": order_id
        }

    # ========================================================
    # 12. COMPLAINT
    # ========================================================

    complaint_phrases = [
        "complaint",
        "very disappointed",
        "extremely disappointed",
        "terrible service",
        "bad service",
        "worst service",
        "this is ridiculous",
        "this is unacceptable",
        "not happy",
        "very unhappy"
    ]

    if any(
        phrase in text
        for phrase in complaint_phrases
    ):

        return {
            "success": True,
            "agent": "intent_agent",
            "intent": "complaint",
            "confidence": 0.90,
            "requires_order": order_id is not None,
            "order_id": order_id
        }

    # ========================================================
    # 13. GENERAL FALLBACK
    # ========================================================

    return {
        "success": True,
        "agent": "intent_agent",
        "intent": "general",
        "confidence": 0.40,
        "requires_order": order_id is not None,
        "order_id": order_id
    }


# ============================================================
# PUBLIC AGENT FUNCTION
# ============================================================

def run_intent_agent(message: str) -> dict:

    return detect_intent(message)