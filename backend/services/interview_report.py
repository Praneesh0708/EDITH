def generate_interview_report(session: dict):
    """
    EDITH Step 32.5.4

    Generates a question-by-question interview report
    using the evaluations stored in the session.
    """

    questions = session.get(
        "questions",
        []
    )

    answers = session.get(
        "answers",
        []
    )

    analyses = session.get(
        "analyses",
        []
    )

    evaluations = session.get(
        "evaluations",
        []
    )

    question_reports = []

    # ========================================================
    # QUESTION-BY-QUESTION REPORT
    # ========================================================

    for index, answer in enumerate(answers):

        question = (
            questions[index]
            if index < len(questions)
            else ""
        )

        analysis = (
            analyses[index]
            if index < len(analyses)
            else {}
        )

        evaluation = (
            evaluations[index]
            if index < len(evaluations)
            else {}
        )

        question_report = {

            "question_number":
                index + 1,

            "question":
                question,

            "answer":
                answer,

            "answer_analysis":
                analysis,

            "human_evaluation":
                evaluation,

            "score":
                evaluation.get(
                    "overall_score",
                    analysis.get(
                        "overall_score",
                        0
                    )
                ),

            "correctness":
                evaluation.get(
                    "correctness",
                    0
                ),

            "relevance":
                evaluation.get(
                    "relevance",
                    0
                ),

            "technical_understanding":
                evaluation.get(
                    "technical_understanding",
                    0
                ),

            "completeness":
                evaluation.get(
                    "completeness",
                    0
                ),

            "reasoning":
                evaluation.get(
                    "reasoning",
                    0
                ),

            "strengths":
                evaluation.get(
                    "strengths",
                    []
                ),

            "missing_points":
                evaluation.get(
                    "missing_points",
                    []
                ),

            "misconceptions":
                evaluation.get(
                    "misconceptions",
                    []
                ),

            "feedback":
                evaluation.get(
                    "feedback",
                    ""
                )
        }

        question_reports.append(
            question_report
        )

    # ========================================================
    # CALCULATE OVERALL SCORE
    # ========================================================

    scores = []

    for report in question_reports:

        score = report.get(
            "score",
            0
        )

        if isinstance(
            score,
            (int, float)
        ):

            scores.append(
                score
            )

    if scores:

        overall_score = round(
            sum(scores) / len(scores),
            2
        )

    else:

        overall_score = 0

    # ========================================================
    # COLLECT STRENGTHS
    # ========================================================

    strengths = []

    for report in question_reports:

        for item in report.get(
            "strengths",
            []
        ):

            if item not in strengths:

                strengths.append(
                    item
                )

    # ========================================================
    # COLLECT MISSING POINTS
    # ========================================================

    missing_points = []

    for report in question_reports:

        for item in report.get(
            "missing_points",
            []
        ):

            if item not in missing_points:

                missing_points.append(
                    item
                )

    # ========================================================
    # COLLECT MISCONCEPTIONS
    # ========================================================

    misconceptions = []

    for report in question_reports:

        for item in report.get(
            "misconceptions",
            []
        ):

            if item not in misconceptions:

                misconceptions.append(
                    item
                )

    # ========================================================
    # PERFORMANCE LEVEL
    # ========================================================

    if overall_score >= 8:

        performance_level = "Excellent"

    elif overall_score >= 6:

        performance_level = "Good"

    elif overall_score >= 4:

        performance_level = "Needs Improvement"

    else:

        performance_level = "Weak"

    # ========================================================
    # FINAL REPORT
    # ========================================================

    return {

        "session_id":
            session.get(
                "session_id"
            ),

        "status":
            session.get(
                "status"
            ),

        "total_questions":
            len(question_reports),

        "overall_score":
            overall_score,

        "performance_level":
            performance_level,

        "strengths":
            strengths,

        "missing_points":
            missing_points,

        "misconceptions":
            misconceptions,

        "question_reports":
            question_reports
    }

def format_interview_report(report: dict):
    """
    EDITH Step 32.6

    Converts the structured interview report into
    a human-readable interviewer-style report.
    """

    lines = []

    lines.append("========================================")
    lines.append("           EDITH INTERVIEW REPORT")
    lines.append("========================================")

    lines.append("")
    lines.append(
        f"Overall Score: "
        f"{report.get('overall_score', 0)}/10"
    )

    lines.append(
        f"Performance: "
        f"{report.get('performance_level', 'Unknown')}"
    )

    lines.append(
        f"Total Questions: "
        f"{report.get('total_questions', 0)}"
    )

    lines.append("")
    lines.append("----------------------------------------")
    lines.append("QUESTION-BY-QUESTION EVALUATION")
    lines.append("----------------------------------------")

    for item in report.get(
        "question_reports",
        []
    ):

        lines.append("")

        lines.append(
            f"Question {item.get('question_number')}"
        )

        lines.append(
            f"Q: {item.get('question', '')}"
        )

        lines.append(
            f"A: {item.get('answer', '')}"
        )

        lines.append(
            f"Score: {item.get('score', 0)}/10"
        )

        lines.append(
            f"Correctness: "
            f"{item.get('correctness', 0)}/10"
        )

        lines.append(
            f"Relevance: "
            f"{item.get('relevance', 0)}/10"
        )

        lines.append(
            f"Technical Understanding: "
            f"{item.get('technical_understanding', 0)}/10"
        )

        lines.append(
            f"Completeness: "
            f"{item.get('completeness', 0)}/10"
        )

        lines.append(
            f"Reasoning: "
            f"{item.get('reasoning', 0)}/10"
        )

        # ------------------------------------
        # Strengths
        # ------------------------------------

        lines.append("")
        lines.append("Strengths:")

        strengths = item.get(
            "strengths",
            []
        )

        if strengths:

            for strength in strengths:

                lines.append(
                    f"  ✓ {strength}"
                )

        else:

            lines.append(
                "  None identified."
            )

        # ------------------------------------
        # Missing Points
        # ------------------------------------

        lines.append("")
        lines.append("Missing Points:")

        missing = item.get(
            "missing_points",
            []
        )

        if missing:

            for point in missing:

                lines.append(
                    f"  • {point}"
                )

        else:

            lines.append(
                "  None identified."
            )

        # ------------------------------------
        # Misconceptions
        # ------------------------------------

        lines.append("")
        lines.append("Misconceptions:")

        misconceptions = item.get(
            "misconceptions",
            []
        )

        if misconceptions:

            for misconception in misconceptions:

                lines.append(
                    f"  ⚠ {misconception}"
                )

        else:

            lines.append(
                "  None identified."
            )

        # ------------------------------------
        # Feedback
        # ------------------------------------

        lines.append("")
        lines.append("Interviewer Feedback:")

        lines.append(
            f"  {item.get('feedback', '')}"
        )

        lines.append("")
        lines.append("----------------------------------------")

    # ========================================================
    # OVERALL STRENGTHS
    # ========================================================

    lines.append("")
    lines.append("OVERALL STRENGTHS")
    lines.append("----------------------------------------")

    strengths = report.get(
        "strengths",
        []
    )

    if strengths:

        for strength in strengths:

            lines.append(
                f"✓ {strength}"
            )

    else:

        lines.append(
            "No major strengths identified."
        )

    # ========================================================
    # OVERALL MISSING POINTS
    # ========================================================

    lines.append("")
    lines.append("AREAS TO IMPROVE")
    lines.append("----------------------------------------")

    missing_points = report.get(
        "missing_points",
        []
    )

    if missing_points:

        for point in missing_points:

            lines.append(
                f"• {point}"
            )

    else:

        lines.append(
            "No major missing points identified."
        )

    # ========================================================
    # MISCONCEPTIONS
    # ========================================================

    lines.append("")
    lines.append("TECHNICAL MISCONCEPTIONS")
    lines.append("----------------------------------------")

    misconceptions = report.get(
        "misconceptions",
        []
    )

    if misconceptions:

        for misconception in misconceptions:

            lines.append(
                f"⚠ {misconception}"
            )

    else:

        lines.append(
            "No technical misconceptions identified."
        )

    # ========================================================
    # FINAL ASSESSMENT
    # ========================================================

    lines.append("")
    lines.append("FINAL ASSESSMENT")
    lines.append("----------------------------------------")

    score = report.get(
        "overall_score",
        0
    )

    if score >= 8:

        feedback = (
            "The candidate demonstrated strong "
            "technical understanding and gave "
            "generally effective answers."
        )

    elif score >= 6:

        feedback = (
            "The candidate demonstrated a good "
            "technical foundation but could improve "
            "depth and completeness."
        )

    elif score >= 4:

        feedback = (
            "The candidate demonstrated partial "
            "understanding and should strengthen "
            "technical concepts and explanations."
        )

    else:

        feedback = (
            "The candidate needs significant "
            "improvement in technical understanding "
            "and answer quality."
        )

    lines.append(
        feedback
    )

    lines.append("")
    lines.append("========================================")
    lines.append("             END OF REPORT")
    lines.append("========================================")

    return "\n".join(lines)
# ============================================================
# TEST 32.5.4
# ============================================================

if __name__ == "__main__":

    print("\n📊 EDITH INTERVIEW REPORT TEST")
    print("================================")

    test_session = {

        "session_id":
            "test-session-123",

        "status":
            "completed",

        "questions": [

            "Why did you use PostgreSQL?",

            "How did you use FastAPI?"
        ],

        "answers": [

            (
                "I used PostgreSQL because EDITH "
                "needs structured data storage."
            ),

            (
                "I used FastAPI to create the backend "
                "APIs and handle requests."
            )
        ],

        "analyses": [

            {
                "overall_score": 8
            },

            {
                "overall_score": 9
            }
        ],

        "evaluations": [

            {
                "correctness": 9,
                "relevance": 9,
                "technical_understanding": 8,
                "completeness": 8,
                "reasoning": 9,
                "overall_score": 9,
                "strengths": [
                    "Clear explanation",
                    "Connected technology to project"
                ],
                "missing_points": [
                    "Could mention relational structure"
                ],
                "misconceptions": [],
                "feedback":
                    "Strong technical explanation."
            },

            {
                "correctness": 9,
                "relevance": 10,
                "technical_understanding": 9,
                "completeness": 8,
                "reasoning": 9,
                "overall_score": 9,
                "strengths": [
                    "Good understanding of FastAPI"
                ],
                "missing_points": [],
                "misconceptions": [],
                "feedback":
                    "Good explanation of backend usage."
            }
        ],

        "face_events": []
    }

    report = generate_interview_report(
        test_session
    )

    print("\nOverall Score:")
    print(
        report["overall_score"]
    )

    print("\nPerformance:")
    print(
        report["performance_level"]
    )

    print("\nTotal Questions:")
    print(
        report["total_questions"]
    )

    print("\nQuestion Reports:")

    for item in report[
        "question_reports"
    ]:

        print(
            f"\nQuestion {item['question_number']}:"
        )

        print(
            "Score:",
            item["score"]
        )

        print(
            "Feedback:",
            item["feedback"]
        )

    print("\nStrengths:")
    print(
        report["strengths"]
    )

    print("\nMissing Points:")
    print(
        report["missing_points"]
    )

    print("\nMisconceptions:")
    print(
        report["misconceptions"]
    )