from typing import Any, Dict, Optional


def run_escalation_agent(
    message: str,
    confidence: float = 1.0,
    intent: Optional[str] = None,
    sentiment: Optional[str] = None,
    troubleshooting_failures: int = 0,
    high_value_transaction: bool = False,
    sensitive_issue: bool = False,
    policy_exception: bool = False,
    tool_failure: bool = False,
    security_concern: bool = False
) -> Dict[str, Any]:
    """
    Determines whether a customer conversation should continue
    with AI or be escalated to human support.
    """

    if not message or not message.strip():
        return {
            "success": False,
            "agent": "escalation_agent",
            "decision": "CONTINUE_AI",
            "status": "invalid_request",
            "escalation_required": False,
            "priority": "normal",
            "confidence": 0.0,
            "intent": intent,
            "sentiment": sentiment,
            "reasons": ["Empty customer message."],
            "recommended_action": "Request a valid customer message.",
            "signals": {}
        }

    text = message.lower().strip()

    # ---------------------------------------------------------
    # SIGNAL DETECTION
    # ---------------------------------------------------------

    human_keywords = [
        "speak to a human",
        "talk to a human",
        "speak with a human",
        "talk with a human",
        "need help from a human",
        "need urgent help from a human",
        "need help from human",
        "need urgent help from human",
        "want a human",
        "need a human",
        "human support",
        "speak to support",
        "talk to support",
        "support representative",
        "customer representative",
        "real person",
        "live agent",
        "human agent"
    ]

    urgent_keywords = [
        "urgent",
        "immediately",
        "as soon as possible",
        "emergency",
        "right now"
    ]

    angry_keywords = [
        "ridiculous",
        "furious",
        "extremely angry",
        "very angry",
        "this is unacceptable",
        "worst service",
        "terrible service",
        "fed up"
    ]

    explicit_human_request = any(
        keyword in text
        for keyword in human_keywords
    )

    urgent_detected = any(
        keyword in text
        for keyword in urgent_keywords
    )

    angry_detected = (
        sentiment == "angry"
        or any(
            keyword in text
            for keyword in angry_keywords
        )
    )

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------

    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0

    low_confidence = confidence < 0.50

    # ---------------------------------------------------------
    # TROUBLESHOOTING FAILURE
    # ---------------------------------------------------------

    multiple_troubleshooting_failures = (
        troubleshooting_failures >= 3
    )

    # ---------------------------------------------------------
    # SIGNAL SUMMARY
    # ---------------------------------------------------------

    signals = {
        "explicit_human_request": explicit_human_request,
        "low_confidence": low_confidence,
        "angry_detected": angry_detected,
        "urgent_detected": urgent_detected,
        "multiple_troubleshooting_failures":
            multiple_troubleshooting_failures,
        "high_value_transaction": high_value_transaction,
        "sensitive_issue": sensitive_issue,
        "policy_exception": policy_exception,
        "tool_failure": tool_failure,
        "security_concern": security_concern
    }

    # ---------------------------------------------------------
    # ESCALATION REASONS
    # ---------------------------------------------------------

    reasons = []

    if explicit_human_request:
        reasons.append(
            "Customer explicitly requested human support."
        )

    if low_confidence:
        reasons.append(
            f"AI confidence is low ({confidence:.2f})."
        )

    if angry_detected:
        reasons.append(
            "Customer message contains strong anger signals."
        )

    if urgent_detected:
        reasons.append(
            "Customer message contains urgent language."
        )

    if multiple_troubleshooting_failures:
        reasons.append(
            "Multiple troubleshooting attempts have failed."
        )

    if high_value_transaction:
        reasons.append(
            "The request involves a high-value transaction."
        )

    if sensitive_issue:
        reasons.append(
            "The request involves a sensitive customer issue."
        )

    if policy_exception:
        reasons.append(
            "The request requires a policy exception."
        )

    if tool_failure:
        reasons.append(
            "A required support tool or API failed."
        )

    if security_concern:
        reasons.append(
            "A potential security concern was detected."
        )

    # ---------------------------------------------------------
    # ESCALATION DECISION
    # ---------------------------------------------------------

    # Strong signals that should ALWAYS escalate.
    mandatory_escalation = (
        explicit_human_request
        or security_concern
        or sensitive_issue
        or policy_exception
        or tool_failure
        or multiple_troubleshooting_failures
    )

    # IMPORTANT:
    # Frustration alone does NOT cause escalation.
    #
    # Angry + urgent is considered strong enough to escalate.
    # Low confidence alone can also escalate because the AI
    # should not confidently answer something it doesn't know.
    strong_emotional_escalation = (
        angry_detected
        and urgent_detected
    )

    if mandatory_escalation or strong_emotional_escalation:

        priority = "high"

        if high_value_transaction:
            priority = "high"

        return {
            "success": True,
            "agent": "escalation_agent",
            "decision": "ESCALATE_HUMAN",
            "status": "escalation_required",
            "escalation_required": True,
            "priority": priority,
            "confidence": round(confidence, 4),
            "intent": intent,
            "sentiment": sentiment,
            "reasons": reasons,
            "recommended_action": (
                "Create or update a support ticket and "
                "handoff the conversation to a human "
                "support representative."
            ),
            "signals": signals
        }

    # ---------------------------------------------------------
    # LOW CONFIDENCE
    # ---------------------------------------------------------

    if low_confidence and intent not in (
    "general",
    None
    ):

        return {
        "success": True,
        "agent": "escalation_agent",
        "decision": "ESCALATE_HUMAN",
        "status": "escalation_required",
        "escalation_required": True,
        "priority": "medium",
        "confidence": round(confidence, 4),
        "intent": intent,
        "sentiment": sentiment,
        "reasons": reasons,
        "recommended_action": (
            "Create or update a support ticket and "
            "handoff the conversation to a human "
            "support representative."
        ),
        "signals": signals
        }

    # ---------------------------------------------------------
    # CONTINUE WITH AI
    # ---------------------------------------------------------

    return {
        "success": True,
        "agent": "escalation_agent",
        "decision": "CONTINUE_AI",
        "status": "ai_can_continue",
        "escalation_required": False,
        "priority": "normal",
        "confidence": round(confidence, 4),
        "intent": intent,
        "sentiment": sentiment,
        "reasons": [],
        "recommended_action": (
            "Continue handling the conversation "
            "with the AI support system."
        ),
        "signals": signals
    }