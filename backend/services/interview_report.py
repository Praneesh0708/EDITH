def generate_interview_report(session: dict):

    analyses = session.get("analyses", [])
    face_events = session.get("face_events", [])

    # ============================================================
    # FACE MONITORING ANALYSIS
    # ============================================================

    total_face_checks = len(face_events)

    if total_face_checks > 0:

        face_present_events = [
            event for event in face_events
            if event.get("face_detected", False)
        ]

        no_face_events = [
            event for event in face_events
            if not event.get("face_detected", False)
        ]

        multiple_face_events = [
            event for event in face_events
            if event.get("face_count", 0) > 1
        ]

        average_face_count = round(
            sum(
                event.get("face_count", 0)
                for event in face_events
            ) / total_face_checks,
            2
        )

        presence_rate = round(
            (len(face_present_events) / total_face_checks) * 100,
            1
        )

    else:

        no_face_events = []
        multiple_face_events = []

        average_face_count = 0
        presence_rate = 0

    face_monitoring = {
        "total_checks": total_face_checks,
        "presence_rate": presence_rate,
        "average_face_count": average_face_count,
        "no_face_events": len(no_face_events),
        "multiple_face_events": len(multiple_face_events)
    }

    # ============================================================
    # ANSWER ANALYSIS
    # ============================================================

    if not analyses:

        return {
            "overall_score": 0,
            "average_relevance": 0,
            "average_clarity": 0,
            "average_completeness": 0,
            "questions_answered": 0,

            "strengths": [],
            "improvement_areas": [],

            "face_monitoring": face_monitoring,

            "recommendation": (
                "Not enough answer data to evaluate the interview."
            )
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

    # ============================================================
    # STRENGTHS
    # ============================================================

    strengths = []
    improvement_areas = []

    if average_relevance >= 8:
        strengths.append(
            "Strong relevance to interview questions."
        )

    if average_clarity >= 8:
        strengths.append(
            "Clear and understandable communication."
        )

    if average_completeness >= 8:
        strengths.append(
            "Good level of detail in answers."
        )

    # ============================================================
    # FACE-BASED OBSERVATIONS
    # ============================================================

    if total_face_checks > 0:

        if presence_rate >= 90:
            strengths.append(
                "Consistent face presence during the interview."
            )

        if multiple_face_events == 0:
            strengths.append(
                "No multiple-face events detected."
            )

        if presence_rate < 80:
            improvement_areas.append(
                "Maintain consistent presence in front of the camera."
            )

        if len(multiple_face_events) > 0:
            improvement_areas.append(
                "Multiple faces were detected during some monitoring checks."
            )

    # ============================================================
    # ANSWER IMPROVEMENTS
    # ============================================================

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

    # ============================================================
    # RECOMMENDATION
    # ============================================================

    if overall_score >= 8:
        recommendation = (
            "Excellent interview performance."
        )

    elif overall_score >= 7:
        recommendation = (
            "Good interview performance with minor improvements needed."
        )

    elif overall_score >= 5:
        recommendation = (
            "Average performance. Further practice is recommended."
        )

    else:
        recommendation = (
            "Needs significant improvement and additional practice."
        )

    # ============================================================
    # FINAL REPORT
    # ============================================================

    return {
        "overall_score": overall_score,

        "average_relevance": average_relevance,
        "average_clarity": average_clarity,
        "average_completeness": average_completeness,

        "questions_answered": len(analyses),

        "strengths": strengths,
        "improvement_areas": improvement_areas,

        "face_monitoring": face_monitoring,

        "recommendation": recommendation
    }