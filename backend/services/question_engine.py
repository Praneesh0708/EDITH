def generate_next_question(
    previous_question: str,
    answer: str,
    analysis: dict,
    asked_questions: list = None
):
    """
    EDITH Step 32.2
    Adaptive Question Engine

    Features:
    - Prevents repeated questions
    - Handles pass/skip answers
    - Uses answer score
    - Uses detected topics
    - Changes difficulty
    - Provides many fallback questions
    """

    if asked_questions is None:
        asked_questions = []

    score = analysis.get("overall_score", 0)
    keywords = analysis.get("keywords", [])

    answer_lower = answer.strip().lower()

    # --------------------------------------------------------
    # Normalize asked questions
    # --------------------------------------------------------

    asked_normalized = {
        q.strip().lower()
        for q in asked_questions
        if isinstance(q, str)
    }

    # --------------------------------------------------------
    # Check whether question was already asked
    # --------------------------------------------------------

    def is_new_question(question):
        return question.strip().lower() not in asked_normalized

    # --------------------------------------------------------
    # Create response
    # --------------------------------------------------------

    def make_question(question, difficulty, topic):
        return {
            "question": question,
            "difficulty": difficulty,
            "topic": topic
        }

    # ========================================================
    # PASS / SKIP HANDLING
    # ========================================================

    pass_words = {
        "pass",
        "skip",
        "next",
        "skip this",
        "pass this",
        "i don't know",
        "dont know",
        "don't know"
    }

    if answer_lower in pass_words:

        pass_questions = [
            (
                "What programming language are you most "
                "comfortable working with?",
                "easy",
                "Technical Skills"
            ),
            (
                "Which technical skill do you think is "
                "your strongest?",
                "easy",
                "Technical Skills"
            ),
            (
                "What type of software projects do you "
                "enjoy building?",
                "easy",
                "Projects"
            ),
            (
                "Which technology have you learned recently "
                "and why did you learn it?",
                "medium",
                "Learning"
            ),
            (
                "What technical concept would you like "
                "to improve further?",
                "medium",
                "Self Improvement"
            )
        ]

        for question, difficulty, topic in pass_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    topic
                )

    # ========================================================
    # PYTHON
    # ========================================================

    if "python" in keywords or "python" in answer_lower:

        python_questions = [
            (
                "You mentioned Python. Can you explain how "
                "you would handle exceptions in Python?",
                "medium"
            ),
            (
                "What is the difference between a list, "
                "tuple, and set in Python?",
                "medium"
            ),
            (
                "How does object-oriented programming work "
                "in Python?",
                "hard"
            ),
            (
                "What are decorators in Python and when "
                "would you use them?",
                "hard"
            ),
            (
                "What is the difference between shallow "
                "copy and deep copy in Python?",
                "hard"
            ),
            (
                "How does Python manage memory?",
                "hard"
            ),
            (
                "What are Python generators and why are "
                "they useful?",
                "medium"
            )
        ]

        for question, difficulty in python_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "Python"
                )

    # ========================================================
    # FASTAPI / API
    # ========================================================

    if "fastapi" in keywords or "api" in keywords:

        api_questions = [
            (
                "How would you design authentication and "
                "authorization for a FastAPI application?",
                "hard"
            ),
            (
                "What is an API and why would you use "
                "FastAPI to build one?",
                "easy"
            ),
            (
                "How would you handle errors and validation "
                "in a FastAPI application?",
                "medium"
            ),
            (
                "How would you connect a FastAPI application "
                "to a database?",
                "medium"
            ),
            (
                "What is the difference between GET and "
                "POST requests?",
                "easy"
            ),
            (
                "How would you secure an API?",
                "hard"
            )
        ]

        for question, difficulty in api_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "FastAPI"
                )

    # ========================================================
    # DATABASE / SQL
    # ========================================================

    if "database" in keywords or "sql" in keywords:

        database_questions = [
            (
                "Can you explain the difference between "
                "INNER JOIN and LEFT JOIN in SQL?",
                "medium"
            ),
            (
                "What is database normalization and why "
                "is it useful?",
                "medium"
            ),
            (
                "How would you improve the performance "
                "of a slow SQL query?",
                "hard"
            ),
            (
                "What is the difference between a primary "
                "key and a foreign key?",
                "easy"
            ),
            (
                "What is an index in a database and "
                "why is it useful?",
                "medium"
            ),
            (
                "What is the difference between SQL and "
                "NoSQL databases?",
                "medium"
            )
        ]

        for question, difficulty in database_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "Database"
                )

    # ========================================================
    # MACHINE LEARNING
    # ========================================================

    if (
        "machine learning" in keywords
        or "machine learning" in answer_lower
    ):

        ml_questions = [
            (
                "Can you explain the difference between "
                "supervised and unsupervised learning?",
                "medium"
            ),
            (
                "What is overfitting in machine learning "
                "and how can you reduce it?",
                "medium"
            ),
            (
                "How would you evaluate the performance "
                "of a machine learning model?",
                "hard"
            ),
            (
                "What is the difference between classification "
                "and regression?",
                "medium"
            ),
            (
                "What is a training dataset and a testing "
                "dataset?",
                "easy"
            ),
            (
                "What is feature engineering and why is "
                "it important?",
                "hard"
            )
        ]

        for question, difficulty in ml_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "Machine Learning"
                )

    # ========================================================
    # TEAM / COMMUNICATION
    # ========================================================

    if (
        "team" in keywords
        or "communication" in keywords
    ):

        behavioral_questions = [
            (
                "Tell me about a situation where you worked "
                "with a team to solve a difficult problem.",
                "medium"
            ),
            (
                "How do you handle disagreements with "
                "team members?",
                "medium"
            ),
            (
                "Describe a time when you took leadership "
                "during a project.",
                "hard"
            ),
            (
                "How do you communicate a technical idea "
                "to a non-technical person?",
                "medium"
            )
        ]

        for question, difficulty in behavioral_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "Behavioral"
                )

    # ========================================================
    # LOW SCORE FOLLOW-UP
    # ========================================================

    if score < 5:

        follow_up_questions = [
            (
                "Can you explain that concept using "
                "a simple example?",
                "easy"
            ),
            (
                "Can you explain the main idea in "
                "your own words?",
                "easy"
            ),
            (
                "Can you give a practical example "
                "related to this topic?",
                "easy"
            ),
            (
                "What is the most important point "
                "about this topic?",
                "easy"
            )
        ]

        for question, difficulty in follow_up_questions:

            if is_new_question(question):

                return make_question(
                    question,
                    difficulty,
                    "Follow-up"
                )

    # ========================================================
    # PROJECT QUESTIONS
    # ========================================================

    project_questions = [
        (
            "Can you describe one technical project you "
            "have worked on and explain your contribution?",
            "medium"
        ),
        (
            "What was the biggest technical challenge "
            "you faced in your project?",
            "medium"
        ),
        (
            "Why did you choose the technologies used "
            "in your project?",
            "medium"
        ),
        (
            "How would you improve your project if you "
            "had more development time?",
            "hard"
        ),
        (
            "How did you test and debug your project?",
            "medium"
        ),
        (
            "How did you handle errors or unexpected "
            "problems in your project?",
            "medium"
        ),
        (
            "What did you learn from developing "
            "your project?",
            "medium"
        ),
        (
            "How did you divide the project into "
            "different modules?",
            "medium"
        ),
        (
            "How did you make important technical "
            "decisions during the project?",
            "hard"
        ),
        (
            "If you rebuilt the project today, what "
            "would you do differently?",
            "hard"
        )
    ]

    for question, difficulty in project_questions:

        if is_new_question(question):

            return make_question(
                question,
                difficulty,
                "Projects"
            )

    # ========================================================
    # GENERAL TECHNICAL QUESTIONS
    # ========================================================

    general_questions = [
        (
            "What is the most important technical skill "
            "you have learned so far?",
            "easy"
        ),
        (
            "How do you debug a program when you "
            "encounter an unexpected error?",
            "medium"
        ),
        (
            "How do you learn a new programming language "
            "or technology?",
            "medium"
        ),
        (
            "What is the difference between a compiler "
            "and an interpreter?",
            "medium"
        ),
        (
            "What is object-oriented programming?",
            "easy"
        ),
        (
            "What is the purpose of version control "
            "in software development?",
            "easy"
        ),
        (
            "What is Git and why is it useful for "
            "software development?",
            "easy"
        ),
        (
            "How would you improve the performance "
            "of a software application?",
            "hard"
        ),
        (
            "What makes software maintainable and "
            "easy to extend?",
            "hard"
        ),
        (
            "How do you ensure the quality of your code?",
            "medium"
        )
    ]

    for question, difficulty in general_questions:

        if is_new_question(question):

            return make_question(
                question,
                difficulty,
                "General Technical"
            )

    # ========================================================
    # FINAL UNIQUE FALLBACK
    # ========================================================

    # Instead of returning the same fallback forever,
    # generate a question based on the interview count.

    question_number = len(asked_questions) + 1

    fallback_questions = [
        (
            "What is one technical concept you are "
            "currently learning?",
            "medium"
        ),
        (
            "Which area of computer science would you "
            "like to become stronger in?",
            "medium"
        ),
        (
            "What technical problem would you like "
            "to learn how to solve?",
            "medium"
        ),
        (
            "Which technology would you like to explore "
            "in your next project?",
            "medium"
        ),
        (
            "What is one software engineering concept "
            "you think every developer should understand?",
            "hard"
        )
    ]

    for question, difficulty in fallback_questions:

        if is_new_question(question):

            return make_question(
                question,
                difficulty,
                "General"
            )

    # This should almost never be reached.
    # Return a unique question using the interview number.

    unique_question = (
        f"What is one new technical idea you would "
        f"like to discuss in question {question_number}?"
    )

    return make_question(
        unique_question,
        "medium",
        "General"
    )