def generate_interview_report(session: dict):
    analyses = session.get("analyses", [])

    if not analyses:
        return {
            "overall_score": 0,
            "average_relevance": 0,
            "average_clarity": 0,
            "average_completeness": 0,
            "questions_answered": 0,
            "strengths": [],
            "improvement_areas": [],
            "recommendation": "Not enough data to evaluate the interview."
        }

    relevance_scores = [
        analysis.get("relevance", 0)
        for analysis in analyses
    ]

    clarity_scores = [
        analysis.get("clarity", 0)
        for analysis in analyses
    ]

    completeness_scores = [
        analysis.get("completeness", 0)
        for analysis in analyses
    ]

    overall_scores = [
        analysis.get("overall_score", 0)
        for analysis in analyses
    ]

    average_relevance = round(
        sum(relevance_scores) / len(relevance_scores),
        1
    )

    average_clarity = round(
        sum(clarity_scores) / len(clarity_scores),
        1
    )

    average_completeness = round(
        sum(completeness_scores) / len(completeness_scores),
        1
    )

    overall_score = round(
        sum(overall_scores) / len(overall_scores),
        1
    )

    strengths = []
    improvement_areas = []

    # Strength detection
    if average_relevance >= 8:
        strengths.append("Strong relevance to interview questions.")

    if average_clarity >= 8:
        strengths.append("Clear and understandable communication.")

    if average_completeness >= 8:
        strengths.append("Good level of detail in answers.")

    # Improvement detection
    if average_relevance < 7:
        improvement_areas.append(
            "Improve how directly answers address the question."
        )

    if average_clarity < 7:
        improvement_areas.append(
            "Improve answer structure and clarity."
        )

    if average_completeness < 7:
        improvement_areas.append(
            "Provide more details and concrete examples."
        )

    # Recommendation
    if overall_score >= 8:
        recommendation = "Excellent interview performance."
    elif overall_score >= 7:
        recommendation = "Good interview performance with minor improvements needed."
    elif overall_score >= 5:
        recommendation = "Average performance. Further practice is recommended."
    else:
        recommendation = "Needs significant improvement and additional practice."

    return {
        "overall_score": overall_score,
        "average_relevance": average_relevance,
        "average_clarity": average_clarity,
        "average_completeness": average_completeness,
        "questions_answered": len(analyses),
        "strengths": strengths,
        "improvement_areas": improvement_areas,
        "recommendation": recommendation
    }