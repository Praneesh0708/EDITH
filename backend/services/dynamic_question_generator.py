def generate_dynamic_question(
    previous_question: str,
    answer: str,
    context: dict,
    analysis: dict
):
    """
    EDITH Step 32.3.3

    Generates a personalized follow-up question
    from the candidate's actual answer and context.
    """

    technologies = context.get("technologies", [])
    concepts = context.get("concepts", [])
    topics = context.get("topics", [])

    score = analysis.get("overall_score", 0)

    # --------------------------------------------------------
    # Select the strongest available topic
    # --------------------------------------------------------

    topic = None

    if technologies:
        topic = technologies[0]

    elif concepts:
        topic = concepts[0]

    elif topics:
        topic = topics[0]

    # --------------------------------------------------------
    # No useful context
    # --------------------------------------------------------

    if not topic:

        return {
            "question": (
                "Can you explain one important technical "
                "concept related to your answer?"
            ),
            "difficulty": "easy",
            "topic": "General",
            "source": "context_fallback"
        }

    # --------------------------------------------------------
    # High score
    # --------------------------------------------------------

    if score >= 8:

        return {
            "question": (
                f"You mentioned {topic} in your answer. "
                f"Can you explain how you implemented "
                f"{topic} in your project and what "
                f"technical decisions you made?"
            ),
            "difficulty": "hard",
            "topic": topic,
            "source": "dynamic_context"
        }

    # --------------------------------------------------------
    # Medium score
    # --------------------------------------------------------

    if score >= 5:

        return {
            "question": (
                f"You mentioned {topic}. Can you explain "
                f"how {topic} works in the context of "
                f"your project?"
            ),
            "difficulty": "medium",
            "topic": topic,
            "source": "dynamic_context"
        }

    # --------------------------------------------------------
    # Low score
    # --------------------------------------------------------

    return {
        "question": (
            f"You mentioned {topic}. Can you explain "
            f"the basic idea of {topic} with a simple "
            f"example?"
        ),
        "difficulty": "easy",
        "topic": topic,
        "source": "dynamic_context"
    }
if __name__ == "__main__":

    test_context = {
        "topics": [
            "fastapi",
            "react",
            "api",
            "backend"
        ],
        "technologies": [
            "fastapi",
            "react"
        ],
        "concepts": [
            "api",
            "backend",
            "session management"
        ],
        "important_terms": [
            "edith",
            "fastapi",
            "react"
        ],
        "context": (
            "Technologies: fastapi, react. "
            "Concepts: api, backend, session management."
        )
    }

    test_analysis = {
        "overall_score": 8
    }

    result = generate_dynamic_question(
        previous_question="Tell me about your project.",
        answer=(
            "I developed EDITH using FastAPI for the "
            "backend and React for the frontend."
        ),
        context=test_context,
        analysis=test_analysis
    )

    print("\n🤖 EDITH DYNAMIC QUESTION GENERATOR")
    print("===================================")

    print("Question:")
    print(result["question"])

    print("\nDifficulty:")
    print(result["difficulty"])

    print("\nTopic:")
    print(result["topic"])

    print("\nSource:")
    print(result["source"])