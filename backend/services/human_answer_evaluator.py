import os
import json

from google import genai


def evaluate_answer_human_like(
    question: str,
    answer: str,
    context: dict = None,
    analysis: dict = None
):
    """
    EDITH Step 32.5.1

    Human-like technical answer evaluation.

    Gemini evaluates the meaning of the candidate's answer
    instead of requiring exact keywords or wording.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "message": "Gemini API key not configured"
        }

    if not answer or not answer.strip():
        return {
            "status": "success",
            "correctness": 0,
            "relevance": 0,
            "technical_understanding": 0,
            "completeness": 0,
            "reasoning": 0,
            "overall_score": 0,
            "strengths": [],
            "missing_points": [],
            "misconceptions": [],
            "feedback": "No answer was provided."
        }

    context = context or {}
    analysis = analysis or {}

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are EDITH, an intelligent human-like technical interviewer.

Evaluate the candidate's answer like an experienced human
technical interviewer.

Do NOT judge the answer using exact keyword matching.

The candidate may explain the same idea using different
words, examples, structure, or terminology.

Understand the MEANING of the answer.

QUESTION:
{question}

CANDIDATE ANSWER:
{answer}

DETECTED CONTEXT:
{context}

PREVIOUS ANALYSIS:
{analysis}

Evaluate the following from 0 to 10:

1. correctness
   Is the technical information accurate?

2. relevance
   Does the answer actually address the question?

3. technical_understanding
   Does the candidate demonstrate real understanding?

4. completeness
   Does the answer cover the important parts?
   Do not require every possible detail.

5. reasoning
   Does the explanation make logical sense?

Also identify:

- strengths
- missing_points
- misconceptions

IMPORTANT:

- Do NOT require exact wording.
- Do NOT require exact keywords.
- Do NOT mark an answer wrong just because it is
  phrased differently.
- Accept technically valid alternative explanations.
- A short but correct answer can receive a high score.
- A long answer should not receive a high score simply
  because it is long.
- Identify incorrect technical claims as misconceptions.
- Give partial credit when appropriate.
- Evaluate the candidate's actual understanding.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "correctness": 0,
    "relevance": 0,
    "technical_understanding": 0,
    "completeness": 0,
    "reasoning": 0,
    "overall_score": 0,
    "strengths": [],
    "missing_points": [],
    "misconceptions": [],
    "feedback": ""
}}
"""

    try:

        print("🤖 Sending answer to Gemini for evaluation...")

        interaction = client.interactions.create(
            model="gemini-3.5-flash",
            input=prompt
        )

        response_text = interaction.output_text.strip()

        print("✅ Gemini evaluation received.")

        # Remove markdown JSON fences if Gemini adds them
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "")
            response_text = response_text.replace("```", "")
            response_text = response_text.strip()

        result = json.loads(response_text)

        result["status"] = "success"

        return result

    except json.JSONDecodeError as e:

        return {
            "status": "error",
            "message": "Gemini returned invalid JSON.",
            "raw_response": response_text
            if "response_text" in locals()
            else "",
            "details": str(e)
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ============================================================
# TEST 32.5.1
# ============================================================

if __name__ == "__main__":

    print("\n🧠 EDITH HUMAN-LIKE ANSWER EVALUATOR")
    print("===================================")

    test_question = (
        "Why did you use PostgreSQL in your EDITH project?"
    )

    test_answer = (
        "I chose PostgreSQL because EDITH needs to store "
        "structured information such as interview sessions, "
        "answers, and analysis results. SQL makes it easier "
        "to manage and retrieve that information."
    )

    test_context = {
        "technologies": [
            "postgresql",
            "sql"
        ],
        "concepts": [
            "database"
        ],
        "important_terms": [
            "sessions",
            "answers",
            "analysis",
            "structured data"
        ]
    }

    test_analysis = {
        "overall_score": 8
    }

    print("\nQuestion:")
    print(test_question)

    print("\nCandidate Answer:")
    print(test_answer)

    result = evaluate_answer_human_like(
        question=test_question,
        answer=test_answer,
        context=test_context,
        analysis=test_analysis
    )

    print("\n-----------------------------------")

    print("Status:")
    print(result.get("status"))

    if result.get("status") == "success":

        print("\nCorrectness:")
        print(result.get("correctness"))

        print("\nRelevance:")
        print(result.get("relevance"))

        print("\nTechnical Understanding:")
        print(result.get("technical_understanding"))

        print("\nCompleteness:")
        print(result.get("completeness"))

        print("\nReasoning:")
        print(result.get("reasoning"))

        print("\nOverall Score:")
        print(result.get("overall_score"))

        print("\nStrengths:")
        print(result.get("strengths"))

        print("\nMissing Points:")
        print(result.get("missing_points"))

        print("\nMisconceptions:")
        print(result.get("misconceptions"))

        print("\nFeedback:")
        print(result.get("feedback"))

    else:

        print("\nError:")
        print(result.get("message"))