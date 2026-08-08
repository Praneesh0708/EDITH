import re


def analyze_answer(question: str, answer: str):
    """
    Basic Answer Analysis Engine for EDITH.
    """

    question = question.strip()
    answer = answer.strip()

    # Empty answer
    if not answer:
        return {
            "relevance": 0,
            "clarity": 0,
            "completeness": 0,
            "keywords": [],
            "overall_score": 0,
            "feedback": "No answer was provided."
        }

    # --------------------------------
    # Word count
    # --------------------------------
    words = answer.split()
    word_count = len(words)

    # --------------------------------
    # Clarity Analysis
    # --------------------------------
    sentences = re.split(r"[.!?]+", answer)
    sentences = [s.strip() for s in sentences if s.strip()]

    if sentences:
        average_sentence_length = word_count / len(sentences)
    else:
        average_sentence_length = word_count

    if 5 <= average_sentence_length <= 25:
        clarity = 9
    elif 3 <= average_sentence_length <= 35:
        clarity = 7
    else:
        clarity = 5

    # --------------------------------
    # Completeness Analysis
    # --------------------------------
    if word_count >= 80:
        completeness = 10
    elif word_count >= 50:
        completeness = 8
    elif word_count >= 30:
        completeness = 6
    elif word_count >= 15:
        completeness = 4
    else:
        completeness = 2

    # --------------------------------
    # Keyword Detection
    # --------------------------------
    common_keywords = [
        "python",
        "java",
        "javascript",
        "sql",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "fastapi",
        "react",
        "database",
        "api",
        "project",
        "team",
        "problem solving",
        "communication",
        "leadership"
    ]

    answer_lower = answer.lower()

    detected_keywords = [
        keyword
        for keyword in common_keywords
        if keyword in answer_lower
    ]

    # --------------------------------
    # Relevance Analysis
    # --------------------------------
    question_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", question.lower())
    )

    answer_words = set(
        re.findall(r"\b[a-zA-Z]{4,}\b", answer_lower)
    )

    overlap = question_words.intersection(answer_words)

    if len(overlap) >= 3:
        relevance = 9
    elif len(overlap) >= 2:
        relevance = 7
    elif len(overlap) >= 1:
        relevance = 6
    else:
        relevance = 5

    # --------------------------------
    # Overall Score
    # --------------------------------
    overall_score = round(
        (relevance + clarity + completeness) / 3,
        1
    )

    # --------------------------------
    # Feedback
    # --------------------------------
    feedback = []

    if relevance >= 8:
        feedback.append(
            "Your answer is relevant to the question."
        )
    else:
        feedback.append(
            "Try to connect your answer more directly to the question."
        )

    if clarity >= 8:
        feedback.append(
            "Your answer is clear and easy to follow."
        )
    else:
        feedback.append(
            "Try using shorter and more structured sentences."
        )

    if completeness >= 8:
        feedback.append(
            "You provided a good amount of detail."
        )
    else:
        feedback.append(
            "Add more details, examples, or specific experiences."
        )

    return {
        "relevance": relevance,
        "clarity": clarity,
        "completeness": completeness,
        "keywords": detected_keywords,
        "overall_score": overall_score,
        "feedback": " ".join(feedback)
    }