from backend.app.rag.rag_engine import search_knowledge


def search_company_policy(query: str) -> dict:
    """
    Search the company knowledge base for relevant policies.

    Returns retrieved content together with provenance metadata.
    """

    try:

        results = search_knowledge(
            query=query,
            top_k=3,
            score_threshold=0.50
        )

        if not results:

            return {
                "success": True,
                "results": [],
                "message": (
                    "No relevant company policy was found."
                )
            }

        return {
            "success": True,
            "results": [
                {
                    "source": result.get(
                        "source",
                        "Unknown source"
                    ),
                    "chunk_id": result.get(
                        "chunk_id"
                    ),
                    "score": round(
                        float(
                            result.get(
                                "score",
                                0.0
                            )
                        ),
                        4
                    ),
                    "content": result.get(
                        "text",
                        ""
                    )
                }
                for result in results
            ]
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }