import re
from typing import Any, Dict


def run_sentiment_agent(message: str) -> Dict[str, Any]:
    """
    Customer Sentiment Agent.

    Detects:
    - positive
    - neutral
    - frustrated
    - angry
    - urgent

    Returns sentiment, confidence and priority.
    """

    if not message or not message.strip():
        return {
            "success": False,
            "agent": "sentiment_agent",
            "message": "Please provide a customer message."
        }

    text = message.strip()
    text_lower = text.lower()

    # --------------------------------------------------
    # Keyword groups
    # --------------------------------------------------

    urgent_words = [
        "urgent",
        "immediately",
        "emergency",
        "asap",
        "right now",
        "critical",
        "cannot access",
        "locked out",
        "security issue",
        "fraud",
        "hacked",
        "unauthorized"
    ]

    angry_words = [
        "ridiculous",
        "unacceptable",
        "terrible",
        "worst",
        "furious",
        "angry",
        "hate",
        "disgusting",
        "scam",
        "useless",
        "idiot",
        "complaint",
        "lawsuit",
        "never again"
    ]

    frustrated_words = [
        "frustrated",
        "annoyed",
        "disappointed",
        "still waiting",
        "keeps happening",
        "not working",
        "doesn't work",
        "does not work",
        "failed",
        "problem",
        "issue",
        "delay",
        "delayed",
        "waiting",
        "again",
        "already contacted",
        "nothing happened"
    ]

    positive_words = [
        "thank you",
        "thanks",
        "great",
        "good",
        "excellent",
        "perfect",
        "awesome",
        "helpful",
        "happy",
        "resolved",
        "works now",
        "working now",
        "appreciate"
    ]

    # --------------------------------------------------
    # Score each sentiment
    # --------------------------------------------------

    scores = {
        "positive": 0,
        "neutral": 0,
        "frustrated": 0,
        "angry": 0,
        "urgent": 0
    }

    for word in urgent_words:
        if word in text_lower:
            scores["urgent"] += 3

    for word in angry_words:
        if word in text_lower:
            scores["angry"] += 2

    for word in frustrated_words:
        if word in text_lower:
            scores["frustrated"] += 1

    for word in positive_words:
        if word in text_lower:
            scores["positive"] += 1

    # --------------------------------------------------
    # Special signals
    # --------------------------------------------------

    if "!!!" in text:
        scores["angry"] += 1

    if text.isupper() and len(text) > 5:
        scores["angry"] += 1

    # --------------------------------------------------
    # Determine sentiment
    # --------------------------------------------------

    highest_sentiment = max(
        scores,
        key=scores.get
    )

    highest_score = scores[highest_sentiment]

    # No strong emotional signal
    if highest_score == 0:
        sentiment = "neutral"
        confidence = 0.72

    else:
        sentiment = highest_sentiment

        # Base confidence
        confidence = min(
            0.55 + (highest_score * 0.08),
            0.98
        )

    # --------------------------------------------------
    # Priority
    # --------------------------------------------------

    if sentiment == "urgent":
        priority = "critical"

    elif sentiment == "angry":
        priority = "high"

    elif sentiment == "frustrated":
        priority = "high"

    elif sentiment == "positive":
        priority = "low"

    else:
        priority = "normal"

    # --------------------------------------------------
    # Human escalation recommendation
    # --------------------------------------------------

    escalation_required = sentiment in [
        "urgent",
        "angry"
    ]

    # Very strong frustration can also escalate
    if sentiment == "frustrated" and highest_score >= 3:
        escalation_required = True

    # --------------------------------------------------
    # Explanation
    # --------------------------------------------------

    explanations = {
        "positive": "The customer appears satisfied or appreciative.",
        "neutral": "The customer message appears neutral and informational.",
        "frustrated": "The customer appears frustrated with an ongoing problem or delay.",
        "angry": "The customer appears highly dissatisfied or angry.",
        "urgent": "The message contains signals indicating an urgent or sensitive issue."
    }

    return {
        "success": True,
        "agent": "sentiment_agent",
        "sentiment": sentiment,
        "confidence": round(confidence, 4),
        "priority": priority,
        "escalation_required": escalation_required,
        "explanation": explanations[sentiment],
        "scores": scores
    }