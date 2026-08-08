def generate_next_question(
    previous_question: str,
    answer: str,
    analysis: dict
):
    """
    EDITH Adaptive Question Engine.

    Chooses the next interview question based
    on the candidate's previous answer and analysis.
    """

    score = analysis.get("overall_score", 0)
    keywords = analysis.get("keywords", [])

    answer_lower = answer.lower()

    # --------------------------------
    # Python
    # --------------------------------
    if "python" in keywords or "python" in answer_lower:
        if score >= 8:
            return {
                "question": (
                    "You mentioned Python. Can you explain "
                    "how you would handle exceptions in Python?"
                ),
                "difficulty": "medium",
                "topic": "Python"
            }

        return {
            "question": (
                "What are the basic data types available in Python?"
            ),
            "difficulty": "easy",
            "topic": "Python"
        }

    # --------------------------------
    # FastAPI / API
    # --------------------------------
    if "fastapi" in keywords or "api" in keywords:
        if score >= 8:
            return {
                "question": (
                    "How would you design authentication and "
                    "authorization for a FastAPI application?"
                ),
                "difficulty": "hard",
                "topic": "FastAPI"
            }

        return {
            "question": (
                "What is an API and why would you use FastAPI "
                "to build one?"
            ),
            "difficulty": "easy",
            "topic": "FastAPI"
        }

    # --------------------------------
    # Database
    # --------------------------------
    if "database" in keywords or "sql" in keywords:
        if score >= 8:
            return {
                "question": (
                    "Can you explain the difference between "
                    "INNER JOIN and LEFT JOIN in SQL?"
                ),
                "difficulty": "medium",
                "topic": "Database"
            }

        return {
            "question": (
                "What is a database and why is it useful "
                "in an application?"
            ),
            "difficulty": "easy",
            "topic": "Database"
        }

    # --------------------------------
    # Machine Learning
    # --------------------------------
    if (
        "machine learning" in keywords
        or "machine learning" in answer_lower
    ):
        if score >= 8:
            return {
                "question": (
                    "Can you explain the difference between "
                    "supervised and unsupervised learning?"
                ),
                "difficulty": "medium",
                "topic": "Machine Learning"
            }

        return {
            "question": (
                "What is machine learning, and where is it "
                "commonly used?"
            ),
            "difficulty": "easy",
            "topic": "Machine Learning"
        }

    # --------------------------------
    # Team / Communication
    # --------------------------------
    if "team" in keywords or "communication" in keywords:
        return {
            "question": (
                "Tell me about a situation where you worked "
                "with a team to solve a difficult problem."
            ),
            "difficulty": "medium",
            "topic": "Behavioral"
        }

    # --------------------------------
    # Low score fallback
    # --------------------------------
    if score < 5:
        return {
            "question": (
                "Can you explain your answer with a simple "
                "example?"
            ),
            "difficulty": "easy",
            "topic": "Follow-up"
        }

    # --------------------------------
    # General fallback
    # --------------------------------
    return {
        "question": (
            "Can you describe one technical project you "
            "have worked on and explain your contribution?"
        ),
        "difficulty": "medium",
        "topic": "Projects"
    }