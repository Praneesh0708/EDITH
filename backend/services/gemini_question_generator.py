import os
import re

from google import genai

from backend.services.dynamic_question_generator import (
    generate_dynamic_question
)


# ============================================================
# QUESTION NORMALIZATION
# ============================================================

def normalize_question(question: str) -> str:
    """
    Normalize a question so small formatting differences
    cannot bypass duplicate detection.
    """

    if not isinstance(question, str):
        return ""

    question = question.lower().strip()

    question = re.sub(
        r"[^\w\s]",
        "",
        question
    )

    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate_question(
    question: str,
    asked_questions: list
) -> bool:

    normalized_question = normalize_question(
        question
    )

    if not normalized_question:
        return True

    for old_question in asked_questions:

        if normalize_question(
            old_question
        ) == normalized_question:

            return True

    return False


# ============================================================
# CLEAN GEMINI QUESTION
# ============================================================

def clean_question(question: str) -> str:

    if not isinstance(question, str):
        return ""

    question = question.strip()

    # Remove markdown formatting
    question = question.replace(
        "**",
        ""
    )

    question = question.replace(
        "*",
        ""
    )

    question = question.replace(
        '"',
        ""
    )

    # Remove common prefixes Gemini may return
    prefixes = [
        "question:",
        "next question:",
        "here is the question:",
        "here's the question:"
    ]

    lower_question = question.lower()

    for prefix in prefixes:

        if lower_question.startswith(prefix):

            question = question[
                len(prefix):
            ].strip()

            break

    return question


# ============================================================
# GEMINI QUESTION GENERATOR
# ============================================================

def generate_gemini_question(
    previous_question: str,
    answer: str,
    context: dict,
    analysis: dict,
    conversation_memory: list = None,
    asked_questions: list = None
):
    """
    EDITH Step 32.4.2

    Generates adaptive interview questions using Gemini.

    Duplicate protection:
    - Receives all previously asked questions
    - Checks Gemini output before returning it
    - Rejects repeated questions
    - Retries Gemini
    - Uses dynamic fallback if necessary
    """

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        return {
            "status": "error",
            "message": (
                "Gemini API key not configured"
            )
        }

    # --------------------------------------------------------
    # Initialize lists
    # --------------------------------------------------------

    if conversation_memory is None:
        conversation_memory = []

    if asked_questions is None:
        asked_questions = []

    # --------------------------------------------------------
    # Build complete asked-question list
    # --------------------------------------------------------

    all_asked_questions = []

    for question in asked_questions:

        if isinstance(question, str):

            if question.strip():

                all_asked_questions.append(
                    question.strip()
                )

    # Also collect questions from conversation memory
    for item in conversation_memory:

        if not isinstance(item, dict):
            continue

        memory_question = item.get(
            "question",
            ""
        )

        if isinstance(
            memory_question,
            str
        ):

            if memory_question.strip():

                all_asked_questions.append(
                    memory_question.strip()
                )

    # Add current previous question
    if previous_question:

        all_asked_questions.append(
            previous_question
        )

    # Remove duplicates from our internal list
    unique_asked_questions = []

    seen = set()

    for question in all_asked_questions:

        normalized = normalize_question(
            question
        )

        if normalized and normalized not in seen:

            seen.add(normalized)

            unique_asked_questions.append(
                question
            )

    all_asked_questions = (
        unique_asked_questions
    )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    technologies = context.get(
        "technologies",
        []
    )

    concepts = context.get(
        "concepts",
        []
    )

    important_terms = context.get(
        "important_terms",
        []
    )

    score = analysis.get(
        "overall_score",
        0
    )

    # --------------------------------------------------------
    # Conversation memory text
    # --------------------------------------------------------

    memory_text = ""

    for item in conversation_memory:

        if not isinstance(item, dict):
            continue

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

        memory_score = (
            memory_analysis.get(
                "overall_score",
                0
            )
            if isinstance(
                memory_analysis,
                dict
            )
            else 0
        )

        memory_keywords = (
            memory_analysis.get(
                "keywords",
                []
            )
            if isinstance(
                memory_analysis,
                dict
            )
            else []
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

        memory_text = (
            "No previous conversation history available."
        )

    # --------------------------------------------------------
    # Asked questions text
    # --------------------------------------------------------

    asked_questions_text = "\n".join(
        f"{index + 1}. {question}"
        for index, question
        in enumerate(
            all_asked_questions
        )
    )

    if not asked_questions_text:

        asked_questions_text = (
            "No questions have been asked yet."
        )

    # --------------------------------------------------------
    # Gemini client
    # --------------------------------------------------------

    client = genai.Client(
        api_key=api_key
    )

    # ========================================================
    # TRY GEMINI MULTIPLE TIMES
    # ========================================================

    maximum_attempts = 3

    for attempt in range(
        maximum_attempts
    ):

        # ----------------------------------------------------
        # Strong duplicate-prevention prompt
        # ----------------------------------------------------

        prompt = f"""
You are EDITH, an intelligent adaptive technical interviewer.

Generate exactly ONE new interview question.

CURRENT QUESTION
================
{previous_question}

CURRENT CANDIDATE ANSWER
=======================
{answer}

DETECTED TECHNOLOGIES
=====================
{technologies}

DETECTED CONCEPTS
=================
{concepts}

IMPORTANT TERMS
===============
{important_terms}

CURRENT ANSWER SCORE
====================
{score}


QUESTIONS ALREADY ASKED
=======================

{asked_questions_text}


CONVERSATION MEMORY
===================

{memory_text}


STRICT RULES
============

1. Generate exactly ONE interview question.

2. The new question MUST NOT be identical or substantially
   identical to ANY question in the "QUESTIONS ALREADY ASKED"
   section.

3. NEVER return:
   "Tell me about yourself."

   unless there are no previous questions at all.

4. Do not repeat the same question using slightly different
   wording.

5. Do not repeatedly ask about the same exact concept.

6. The current candidate answer is the PRIMARY source for
   the next question.

7. If the candidate mentioned a technology, ask a deeper
   question about how they used it.

8. If the candidate mentioned a project, ask about its
   implementation, architecture, technical decisions,
   challenges, debugging, testing, or improvements.

9. If the candidate mentioned a problem, ask how they solved it.

10. If the candidate mentioned multiple technologies,
    choose ONE relevant technology that has not already
    been deeply discussed.

11. Use previous conversation memory to avoid repeating
    previously discussed topics.

12. If the previous answer was strong, increase difficulty.

13. If the previous answer was weak, ask a simpler
    follow-up that tests understanding.

14. Do NOT use a generic question bank when the candidate's
    answer contains useful technical information.

15. Do NOT ask:
    "Tell me about yourself."

16. Do NOT ask:
    "Tell me about your project."
    if the project has already been discussed.

17. Do NOT ask a question that already appears in the
    QUESTIONS ALREADY ASKED section.

18. Return ONLY the question.
19. Do not add explanations.
20. Do not add numbering.
"""

        try:

            interaction = client.interactions.create(
                model="gemini-3.5-flash",
                input=prompt
            )

            generated_question = (
                interaction.output_text
                .strip()
            )

            generated_question = clean_question(
                generated_question
            )

            print(
                f"\n🤖 Gemini attempt "
                f"{attempt + 1}"
            )

            print(
                "Generated:",
                generated_question
            )

            # ------------------------------------------------
            # Validate Gemini result
            # ------------------------------------------------

            if not generated_question:

                print(
                    "❌ Gemini returned empty question"
                )

                continue

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            if is_duplicate_question(
                generated_question,
                all_asked_questions
            ):

                print(
                    "❌ Duplicate question rejected"
                )

                continue

            # ------------------------------------------------
            # Prevent generic first question
            # ------------------------------------------------

            if normalize_question(
                generated_question
            ) == normalize_question(
                "Tell me about yourself."
            ):

                print(
                    "❌ Generic opening question rejected"
                )

                continue

            # ------------------------------------------------
            # Valid question
            # ------------------------------------------------

            difficulty = (
                "hard"
                if score >= 8
                else
                "medium"
                if score >= 5
                else
                "easy"
            )

            print(
                "✅ New unique question accepted"
            )

            return {
                "status": "success",
                "question": generated_question,
                "difficulty": difficulty,
                "source": "gemini"
            }

        except Exception as e:

            print(
                "\n⚠️ Gemini generation failed:"
            )

            print(str(e))

            break

    # ========================================================
    # GEMINI FAILED OR GENERATED DUPLICATES
    # USE DYNAMIC FALLBACK
    # ========================================================

    print(
        "\n⚠️ Gemini could not generate "
        "a unique question."
    )

    print(
        "🔄 Using dynamic question fallback."
    )

    try:

        fallback_question = (
            generate_dynamic_question(

                previous_question=previous_question,

                answer=answer,

                context=context,

                analysis=analysis
            )
        )

        if isinstance(
            fallback_question,
            dict
        ):

            fallback_text = (
                fallback_question.get(
                    "question",
                    ""
                )
            )

            fallback_text = clean_question(
                fallback_text
            )

            # ----------------------------------------------
            # Validate fallback
            # ----------------------------------------------

            if (
                fallback_text
                and
                not is_duplicate_question(
                    fallback_text,
                    all_asked_questions
                )
            ):

                fallback_question[
                    "question"
                ] = fallback_text

                fallback_question[
                    "status"
                ] = "fallback"

                print(
                    "✅ Unique fallback question accepted"
                )

                return fallback_question

    except Exception as e:

        print(
            "❌ Dynamic fallback failed:",
            str(e)
        )

    # ========================================================
    # FINAL UNIQUE FALLBACK
    # ========================================================

    question_number = (
        len(all_asked_questions) + 1
    )

    final_question = (
        f"What technical skill have you "
        f"used recently, and how did you "
        f"apply it in practice?"
    )

    # If somehow duplicate, make it unique
    if is_duplicate_question(
        final_question,
        all_asked_questions
    ):

        final_question = (
            f"What is one technical challenge "
            f"you would like to solve in "
            f"question {question_number}?"
        )

    return {

        "status": "fallback",

        "question": final_question,

        "difficulty": "medium",

        "topic": "General",

        "source": "local_fallback"
    }


# ============================================================
# TEST
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

            "question": (
                "Tell me about yourself."
            ),

            "answer": (
                "I am a developer working "
                "on EDITH."
            ),

            "analysis": {
                "overall_score": 7,
                "keywords": [
                    "edith"
                ]
            }
        },

        {
            "question_number": 2,

            "question": (
                "How did you use FastAPI "
                "in EDITH?"
            ),

            "answer": (
                "I used FastAPI to create "
                "REST APIs for interview "
                "session management."
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

    test_asked_questions = [

        "Tell me about yourself.",

        "How did you use FastAPI in EDITH?"

    ]

    result = generate_gemini_question(

        previous_question=(
            "How did you use FastAPI in EDITH?"
        ),

        answer=(
            "I created REST APIs using "
            "FastAPI to manage interview sessions."
        ),

        context=test_context,

        analysis=test_analysis,

        conversation_memory=test_memory,

        asked_questions=test_asked_questions
    )

    print(
        "\n================================="
    )

    print(
        "EDITH QUESTION TEST"
    )

    print(
        "================================="
    )

    print(
        "\nStatus:",
        result.get("status")
    )

    print(
        "\nQuestion:",
        result.get("question")
    )

    print(
        "\nDifficulty:",
        result.get("difficulty")
    )

    print(
        "\nSource:",
        result.get("source")
    )