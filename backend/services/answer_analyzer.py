import re


def analyze_answer(question: str, answer: str):
    """
    EDITH Step 32.2
    Structured Answer Analysis Engine.
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
            "feedback": "No answer was provided.",
            "strength": "No answer provided",
            "weakness": "The question was not answered.",
            "knowledge_gap": "Unable to determine",
            "recommended_difficulty": "easy"
        }

    # Word count
    words = answer.split()
    word_count = len(words)

    # Clarity analysis
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

    # Completeness analysis
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

    # Keyword detection
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

    # Relevance analysis
    question_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            question.lower()
        )
    )

    answer_words = set(
        re.findall(
            r"\b[a-zA-Z]{4,}\b",
            answer_lower
        )
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

    # Overall score
    overall_score = round(
        (relevance + clarity + completeness) / 3,
        1
    )

    # Strength detection
    if relevance >= 8:
        strength = "Strong relevance to the question"
    elif clarity >= 8:
        strength = "Clear communication"
    elif completeness >= 8:
        strength = "Good level of detail"
    elif detected_keywords:
        strength = "Uses relevant concepts"
    else:
        strength = "Shows an attempt to answer the question"

    # Weakness detection
    if relevance < 8:
        weakness = "The answer could connect more directly to the question"
    elif clarity < 8:
        weakness = "The explanation could be clearer and more structured"
    elif completeness < 8:
        weakness = "The answer needs more supporting detail or examples"
    elif not detected_keywords:
        weakness = "Few relevant concepts were identified"
    else:
        weakness = "No major weakness detected"

    # Knowledge gap detection
    if completeness <= 4:
        knowledge_gap = "Needs deeper explanation of the topic"
    elif relevance <= 5:
        knowledge_gap = "Needs better understanding of the question topic"
    elif clarity <= 5:
        knowledge_gap = "Needs improvement in structured explanation"
    elif not detected_keywords:
        knowledge_gap = "Relevant concepts were not demonstrated"
    else:
        knowledge_gap = "No major knowledge gap detected"

    # Recommended difficulty
    if overall_score >= 8:
        recommended_difficulty = "hard"
    elif overall_score >= 6:
        recommended_difficulty = "medium"
    else:
        recommended_difficulty = "easy"

    # Feedback
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

    # Final result
    return {
        "relevance": relevance,
        "clarity": clarity,
        "completeness": completeness,
        "keywords": detected_keywords,
        "overall_score": overall_score,
        "feedback": " ".join(feedback),
        "strength": strength,
        "weakness": weakness,
        "knowledge_gap": knowledge_gap,
        "recommended_difficulty": recommended_difficulty
    }