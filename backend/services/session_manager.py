import uuid


# ============================================================
# ACTIVE INTERVIEW SESSIONS
# ============================================================

sessions = {}


# ============================================================
# CREATE SESSION
# ============================================================

def create_session():

    session_id = str(
        uuid.uuid4()
    )

    sessions[session_id] = {

        "session_id": session_id,

        "status": "active",

        "questions": [],

        "answers": [],

        "analyses": [],

        "evaluations": [],

        "face_events": [],

        "question_number": 1
    }

    return sessions[session_id]


# ============================================================
# GET SESSION
# ============================================================

def get_session(
    session_id: str
):

    return sessions.get(
        session_id
    )


# ============================================================
# ADD INTERVIEW INTERACTION
# ============================================================

def add_interaction(
    session_id: str,
    question: str,
    answer: str,
    analysis: dict,
    human_evaluation: dict = None
):

    session = sessions.get(
        session_id
    )

    if not session:

        return None

    session[
        "questions"
    ].append(
        question
    )

    session[
        "answers"
    ].append(
        answer
    )

    session[
        "analyses"
    ].append(
        analysis
    )

    session[
        "evaluations"
    ].append(
        human_evaluation or {}
    )

    session[
        "question_number"
    ] += 1

    return session


# ============================================================
# ADD FACE EVENT
# ============================================================

def add_face_event(
    session_id: str,
    face_detected: bool,
    face_count: int
):

    session = sessions.get(
        session_id
    )

    if not session:

        return None

    event = {

        "face_detected":
            face_detected,

        "face_count":
            face_count
    }

    session[
        "face_events"
    ].append(
        event
    )

    return event


# ============================================================
# GET CONVERSATION MEMORY
# ============================================================

def get_conversation_memory(
    session_id: str
):

    session = sessions.get(
        session_id
    )

    if not session:

        return []

    memory = []

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

    for index, question in enumerate(
        questions
    ):

        if index >= len(
            answers
        ):

            continue

        memory.append({

            "question":
                question,

            "answer":
                answers[index],

            "analysis":
                analyses[index]
                if index < len(analyses)
                else {},

            "evaluation":
                evaluations[index]
                if index < len(evaluations)
                else {}
        })

    return memory


# ============================================================
# END SESSION
# ============================================================

def end_session(
    session_id: str
):

    session = sessions.get(
        session_id
    )

    if not session:

        return None

    session[
        "status"
    ] = "completed"

    return session