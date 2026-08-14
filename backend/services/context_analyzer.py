import re


def extract_answer_context(answer: str):
    """
    EDITH Step 32.3.1

    Extract useful context from the candidate's answer.

    Returns:
    - topics
    - technologies
    - concepts
    - important_terms
    """

    if not answer:
        return {
            "topics": [],
            "technologies": [],
            "concepts": [],
            "important_terms": [],
            "context": ""
        }

    answer = answer.strip()
    answer_lower = answer.lower()

    # --------------------------------------------------------
    # Technology Detection
    # --------------------------------------------------------

    technology_list = [
        "python",
        "java",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "node",
        "fastapi",
        "django",
        "flask",
        "sql",
        "mysql",
        "postgresql",
        "mongodb",
        "firebase",
        "html",
        "css",
        "opencv",
        "tensorflow",
        "pytorch",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "git",
        "github"
    ]

    technologies = []

    for technology in technology_list:

        if technology in answer_lower:
            technologies.append(technology)

    # --------------------------------------------------------
    # Concept Detection
    # --------------------------------------------------------

    concept_list = [
        "api",
        "rest api",
        "authentication",
        "authorization",
        "database",
        "frontend",
        "backend",
        "full stack",
        "machine learning",
        "deep learning",
        "computer vision",
        "natural language processing",
        "voice recognition",
        "speech recognition",
        "face detection",
        "face recognition",
        "session management",
        "error handling",
        "debugging",
        "testing",
        "deployment",
        "security",
        "data analysis",
        "model training",
        "data preprocessing",
        "teamwork",
        "leadership",
        "communication"
    ]

    concepts = []

    for concept in concept_list:

        if concept in answer_lower:
            concepts.append(concept)

    # --------------------------------------------------------
    # Project Detection
    # --------------------------------------------------------

    project_terms = [
        "project",
        "application",
        "system",
        "website",
        "platform",
        "software",
        "developed",
        "built",
        "created",
        "implemented"
    ]

    project_references = []

    for term in project_terms:

        if term in answer_lower:
            project_references.append(term)

    # --------------------------------------------------------
    # Important Technical Terms
    # --------------------------------------------------------

    words = re.findall(
        r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b",
        answer
    )

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "have",
        "used",
        "using",
        "was",
        "were",
        "are",
        "our",
        "their",
        "they",
        "then",
        "also",
        "into",
        "about",
        "which",
        "when",
        "where",
        "what",
        "how",
        "why",
        "can",
        "could",
        "would",
        "should"
    }

    important_terms = []

    for word in words:

        word_lower = word.lower()

        if (
            word_lower not in stop_words
            and word_lower not in important_terms
        ):
            important_terms.append(word_lower)

    # Keep the list manageable
    important_terms = important_terms[:20]

    # --------------------------------------------------------
    # Build Context
    # --------------------------------------------------------

    context_parts = []

    if technologies:

        context_parts.append(
            "Technologies: "
            + ", ".join(technologies)
        )

    if concepts:

        context_parts.append(
            "Concepts: "
            + ", ".join(concepts)
        )

    if project_references:

        context_parts.append(
            "Project references: "
            + ", ".join(project_references)
        )

    context = ". ".join(context_parts)

    # --------------------------------------------------------
    # Topics
    # --------------------------------------------------------

    topics = []

    topics.extend(technologies)
    topics.extend(concepts)

    # Remove duplicates while preserving order
    topics = list(dict.fromkeys(topics))

    # --------------------------------------------------------
    # Return Context
    # --------------------------------------------------------

    return {
        "topics": topics,
        "technologies": technologies,
        "concepts": concepts,
        "important_terms": important_terms,
        "context": context
    }


# ============================================================
# TEST 32.3.1
# ============================================================

if __name__ == "__main__":

    test_answer = (
        "I developed EDITH using FastAPI for the backend "
        "and React for the frontend. I created APIs to "
        "manage interview sessions."
    )

    result = extract_answer_context(test_answer)

    print("\nEDITH CONTEXT ANALYSIS")
    print("======================")

    print("Topics:", result["topics"])

    print(
        "Technologies:",
        result["technologies"]
    )

    print(
        "Concepts:",
        result["concepts"]
    )

    print(
        "Important Terms:",
        result["important_terms"]
    )

    print(
        "Context:",
        result["context"]
    )