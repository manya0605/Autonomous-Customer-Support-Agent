from typing import Any, Dict, List

from backend.app.tools.rag_tools import search_company_policy
from backend.app.core.ai import client, MODEL


# ============================================================
# HELPERS
# ============================================================

def _clean_source(source: str) -> str:
    if not source:
        return "Unknown source"

    source = source.replace("\\", "/")

    return source.split("/")[-1]


def _retrieve_troubleshooting_knowledge(
    message: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Retrieve troubleshooting information from the
    enterprise knowledge base.
    """

    result = search_company_policy(message)

    if not result.get("success", False):
        return []

    return result.get("results", [])[:top_k]


# ============================================================
# IDENTIFY DEVICE / SYMPTOM
# ============================================================

def _identify_problem(message: str) -> Dict[str, str]:

    prompt = f"""
Identify the customer's technical problem.

Customer message:
{message}

Return ONLY this format:

DEVICE: <device>
SYMPTOM: <short symptom>

Examples:

DEVICE: router
SYMPTOM: internet connection keeps disconnecting

DEVICE: laptop
SYMPTOM: laptop does not connect to WiFi

DEVICE: printer
SYMPTOM: printer is not printing

If the device cannot be determined, use:
DEVICE: unknown
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You identify technical support problems. "
                    "Do not invent information."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    text = response.choices[0].message.content.strip()

    device = "unknown"
    symptom = "unknown"

    for line in text.splitlines():

        if line.upper().startswith("DEVICE:"):
            device = line.split(":", 1)[1].strip()

        elif line.upper().startswith("SYMPTOM:"):
            symptom = line.split(":", 1)[1].strip()

    return {
        "device": device,
        "symptom": symptom
    }


# ============================================================
# GENERATE TROUBLESHOOTING STEP
# ============================================================

def _generate_step(
    message: str,
    device: str,
    symptom: str,
    step_number: int,
    previous_steps: List[str],
    knowledge: List[Dict[str, Any]]
) -> str:

    context = ""

    for item in knowledge:

        context += f"""
SOURCE: {_clean_source(item.get("source", "Unknown"))}

{item.get("content", "")}

--------------------------------
"""

    previous = "\n".join(
        previous_steps
    ) if previous_steps else "None"

    prompt = f"""
You are an enterprise technical-support troubleshooting agent.

Customer problem:
{message}

Device:
{device}

Symptom:
{symptom}

Current troubleshooting step:
{step_number}

Previous troubleshooting steps:
{previous}

Relevant company documentation:
{context}

Generate ONE practical troubleshooting step.

Rules:

1. Prefer steps supported by the company documentation.
2. Do not invent company policies.
3. Do not repeat a previous step.
4. Keep the instructions simple.
5. Do not claim the issue is resolved.
6. Ask the customer to report whether the step worked.
7. If there is insufficient documentation, clearly say so.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a safe enterprise technical "
                    "support troubleshooting assistant."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()


# ============================================================
# MAIN TROUBLESHOOTING AGENT
# ============================================================

def run_troubleshooting_agent(
    message: str,
    device: str = None,
    symptom: str = None,
    step: int = 1,
    previous_steps: List[str] = None,
    resolved: bool = False
) -> Dict[str, Any]:

    if not message or not message.strip():

        return {
            "success": False,
            "agent": "troubleshooting_agent",
            "message": "Please describe the technical problem."
        }

    if previous_steps is None:
        previous_steps = []

    try:

        # ----------------------------------------------------
        # RESOLUTION CHECK
        # ----------------------------------------------------

        if resolved:

            return {
                "success": True,
                "agent": "troubleshooting_agent",
                "status": "resolved",
                "device": device,
                "symptom": symptom,
                "step": step,
                "message": (
                    "Great! The troubleshooting process "
                    "has been marked as resolved."
                ),
                "next_action": "close"
            }

        # ----------------------------------------------------
        # IDENTIFY DEVICE AND SYMPTOM
        # ----------------------------------------------------

        if not device or not symptom:

            problem = _identify_problem(
                message
            )

            device = device or problem["device"]
            symptom = symptom or problem["symptom"]

        # ----------------------------------------------------
        # RETRIEVE KNOWLEDGE
        # ----------------------------------------------------

        search_query = (
            f"{device} {symptom} troubleshooting "
            f"technical support"
        )

        knowledge = _retrieve_troubleshooting_knowledge(
            search_query,
            top_k=3
        )

        # ----------------------------------------------------
        # NO KNOWLEDGE FOUND
        # ----------------------------------------------------

        if not knowledge:

            return {
                "success": False,
                "agent": "troubleshooting_agent",
                "status": "knowledge_unavailable",
                "device": device,
                "symptom": symptom,
                "step": step,
                "message": (
                    "I couldn't find sufficient troubleshooting "
                    "information in the company knowledge base."
                ),
                "next_action": "escalate",
                "escalation_required": True
            }

        # ----------------------------------------------------
        # TOO MANY FAILED STEPS
        # ----------------------------------------------------

        if step > 3:

            return {
                "success": True,
                "agent": "troubleshooting_agent",
                "status": "escalation_required",
                "device": device,
                "symptom": symptom,
                "step": step,
                "message": (
                    "The recommended troubleshooting steps "
                    "have not resolved the issue. This should "
                    "now be reviewed by a human support "
                    "representative."
                ),
                "next_action": "escalate",
                "escalation_required": True,
                "reason": (
                    "Multiple troubleshooting attempts "
                    "were unsuccessful."
                )
            }

        # ----------------------------------------------------
        # GENERATE NEXT STEP
        # ----------------------------------------------------

        troubleshooting_step = _generate_step(
            message=message,
            device=device,
            symptom=symptom,
            step_number=step,
            previous_steps=previous_steps,
            knowledge=knowledge
        )

        # ----------------------------------------------------
        # ADD CURRENT STEP TO HISTORY
        # ----------------------------------------------------

        updated_steps = previous_steps + [
            troubleshooting_step
        ]

        # ----------------------------------------------------
        # BUILD SOURCES
        # ----------------------------------------------------

        sources = []

        for item in knowledge:

            source = {
                "document": _clean_source(
                    item.get(
                        "source",
                        "Unknown source"
                    )
                ),
                "score": round(
                    float(item.get("score", 0)),
                    4
                )
            }

            if source not in sources:
                sources.append(source)

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        return {
            "success": True,
            "agent": "troubleshooting_agent",
            "status": "awaiting_customer",
            "device": device,
            "symptom": symptom,
            "step": step,
            "instructions": troubleshooting_step,
            "sources": sources,
            "previous_steps": updated_steps,
            "next_action": "ask_customer",
            "escalation_required": False,
            "provenance": {
                "retrieval_method": "FAISS semantic search",
                "documents_retrieved": len(knowledge),
                "generation_method": "LLM grounded troubleshooting"
            }
        }

    except Exception as e:

        return {
            "success": False,
            "agent": "troubleshooting_agent",
            "status": "error",
            "message": (
                "The troubleshooting service is temporarily "
                "unavailable."
            ),
            "next_action": "escalate",
            "escalation_required": True,
            "error": str(e)
        }