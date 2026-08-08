import uuid


sessions = {}


def create_session():
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "session_id": session_id,
        "status": "active",
        "question_number": 1,
        "questions": [],
        "answers": [],
        "analyses": []
    }

    return sessions[session_id]


def get_session(session_id: str):
    return sessions.get(session_id)


def add_interaction(
    session_id: str,
    question: str,
    answer: str,
    analysis: dict
):
    session = sessions.get(session_id)

    if not session:
        return None

    session["questions"].append(question)
    session["answers"].append(answer)
    session["analyses"].append(analysis)

    session["question_number"] += 1

    return session


def end_session(session_id: str):
    session = sessions.get(session_id)

    if not session:
        return None

    session["status"] = "completed"

    return session