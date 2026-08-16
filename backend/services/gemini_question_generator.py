import os

from google import genai

from backend.services.dynamic_question_generator import (
    generate_dynamic_question
)


def generate_gemini_question(
    previous_question: str,
    answer: str,
    context: dict,
    analysis: dict,
    conversation_memory: list = None
):
    """
    EDITH Step 32.4.2

    Uses Gemini to generate a personalized
    interview follow-up question using:
    - Current answer
    - Current context
    - Current analysis
    - Previous conversation memory
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

    if conversation_memory is None:
        conversation_memory = []

    # --------------------------------------------------------
    # Build Conversation Memory
    # --------------------------------------------------------

    memory_text = ""

    for item in conversation_memory:

        question_number = item.get(
            "question_number",
            ""
        )

        memory_question = item.get(
            "question",
            ""
        )

        memory_answer = item.get(
            "answer",
            ""
        )

        memory_analysis = item.get(
            "analysis",
            {}
        )

        memory_score = memory_analysis.get(
            "overall_score",
            0
        )

        memory_keywords = memory_analysis.get(
            "keywords",
            []
        )

        memory_text += f"""
Question {question_number}:
{memory_question}

Candidate Answer:
{memory_answer}

Score:
{memory_score}

Keywords:
{memory_keywords}

---
"""

    if not memory_text:
        memory_text = "No previous conversation history available."

    # --------------------------------------------------------
    # Gemini Prompt
    # --------------------------------------------------------

    prompt = f"""
You are EDITH, an intelligent adaptive technical interviewer.

Your job is to generate ONE personalized follow-up
interview question.

CURRENT INTERACTION
===================

Previous question:
{previous_question}

Current candidate answer:
{answer}

Detected technologies:
{technologies}

Detected concepts:
{concepts}

Important terms:
{important_terms}

Current answer score:
{score}


PREVIOUS INTERVIEW MEMORY
=========================

{memory_text}


QUESTION GENERATION RULES
=========================

1. Ask exactly ONE question.

2. The question must be based on the candidate's
   actual technical experience and answers.

3. Use the current answer as the primary source.

4. Use previous interview memory to understand
   what the candidate has already discussed.

5. Do NOT ask a generic technical question.

6. Do NOT repeat a question already asked.

7. Do NOT ask the same topic repeatedly unless
   the new question explores a deeper aspect.

8. If the candidate mentioned a technology,
   ask about how they actually used it.

9. If the candidate mentioned a project,
   ask about implementation, architecture,
   technical decisions, challenges, or solutions.

10. If the candidate mentioned a problem,
    ask how they solved it.

11. If the candidate mentioned multiple technologies,
    choose the most relevant one for the next question.

12. If previous memory shows that a topic was already
    discussed, move to a related deeper topic.

13. Increase difficulty when the current answer score
    is high.

14. Decrease difficulty when the current answer score
    is low.

15. Keep the question suitable for a technical interview.

16. Return ONLY the question.
"""

    # --------------------------------------------------------
    # Gemini Request
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Gemini Failure → Dynamic Fallback
    # --------------------------------------------------------

    except Exception as e:

        fallback_question = generate_dynamic_question(
            previous_question=previous_question,
            answer=answer,
            context=context,
            analysis=analysis
        )

        fallback_question["status"] = "fallback"
        fallback_question["gemini_error"] = str(e)

        return fallback_question


# ============================================================
# TEST 32.4.2
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
        "overall_score": 8,
        "keywords": [
            "fastapi",
            "react",
            "api"
        ]
    }

    test_memory = [
        {
            "question_number": 1,
            "question": "Tell me about your project.",
            "answer": (
                "I developed EDITH using FastAPI "
                "for the backend and React for "
                "the frontend."
            ),
            "analysis": {
                "overall_score": 8,
                "keywords": [
                    "fastapi",
                    "react"
                ]
            }
        },
        {
            "question_number": 2,
            "question": (
                "How did you use FastAPI in EDITH?"
            ),
            "answer": (
                "I used FastAPI to create REST APIs "
                "for managing interview sessions."
            ),
            "analysis": {
                "overall_score": 9,
                "keywords": [
                    "fastapi",
                    "api",
                    "session management"
                ]
            }
        }
    ]

    result = generate_gemini_question(
        previous_question=(
            "How did you use FastAPI in EDITH?"
        ),
        answer=(
            "I created REST APIs using FastAPI "
            "to manage interview sessions."
        ),
        context=test_context,
        analysis=test_analysis,
        conversation_memory=test_memory
    )

    print("\n🤖 EDITH CONVERSATION MEMORY TEST")
    print("=================================")

    print("\nStatus:")
    print(result.get("status"))

    print("\nGenerated Question:")
    print(result.get("question"))

    print("\nDifficulty:")
    print(result.get("difficulty"))

    print("\nSource:")
    print(result.get("source"))

    if result.get("status") == "error":

        print("\nError:")
        print(result.get("message"))

    elif result.get("status") == "fallback":

        print("\nGemini Error:")
        print(result.get("gemini_error"))