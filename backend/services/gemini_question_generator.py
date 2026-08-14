import os

from google import genai


def generate_gemini_question(
    previous_question: str,
    answer: str,
    context: dict,
    analysis: dict
):
    """
    EDITH Step 32.3.5

    Uses Gemini to generate a personalized
    interview follow-up question.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "Gemini API key not configured"
        }

    client = genai.Client(api_key=api_key)

    technologies = context.get("technologies", [])
    concepts = context.get("concepts", [])
    important_terms = context.get("important_terms", [])

    score = analysis.get("overall_score", 0)

    prompt = f"""
You are EDITH, an intelligent adaptive technical interviewer.

Your job is to generate ONE personalized follow-up
interview question based ONLY on the candidate's answer.

Previous question:
{previous_question}

Candidate's answer:
{answer}

Detected technologies:
{technologies}

Detected concepts:
{concepts}

Important terms:
{important_terms}

Answer score:
{score}

Rules:
1. Ask exactly ONE question.
2. The question must directly relate to something
   the candidate actually mentioned.
3. Do not ask a generic question.
4. Do not repeat the previous question.
5. If the candidate mentioned a project, ask about
   their actual implementation or technical decisions.
6. If a technology was mentioned, ask about how
   they used it.
7. Increase difficulty when the answer score is high.
8. Keep the question suitable for a technical interview.
9. Return ONLY the question.
"""

    try:

        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input=prompt
        )

        question = interaction.output_text.strip()

        return {
            "status": "success",
            "question": question,
            "difficulty": (
                "hard"
                if score >= 8
                else "medium"
                if score >= 5
                else "easy"
            ),
            "source": "gemini"
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# TEST 32.3.5
# ============================================================

if __name__ == "__main__":

    test_context = {
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
            "react",
            "sessions"
        ]
    }

    test_analysis = {
        "overall_score": 8
    }

    result = generate_gemini_question(
        previous_question="Tell me about your project.",
        answer=(
            "I developed EDITH using FastAPI for the backend "
            "and React for the frontend. I created REST APIs "
            "to manage interview sessions."
        ),
        context=test_context,
        analysis=test_analysis
    )

    print("\n🤖 EDITH GEMINI QUESTION GENERATOR")
    print("=================================")

    print("Status:", result.get("status"))

    if result.get("status") == "success":

        print("\nGenerated Question:")
        print(result["question"])

        print("\nDifficulty:")
        print(result["difficulty"])

        print("\nSource:")
        print(result["source"])

    else:

        print("\nError:")
        print(result.get("message"))