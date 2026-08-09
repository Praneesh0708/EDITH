import uuid

# Store active interview sessions
sessions = {}


# --------------------------------
# Create Session
# --------------------------------

def create_session():
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "session_id": session_id,
        "status": "active",

        "questions": [],
        "answers": [],
        "analyses": [],

        # Face monitoring data
        "face_events": [],

        "question_number": 1
    }

    return sessions[session_id]


# --------------------------------
# Get Session
# --------------------------------

def get_session(session_id: str):
    return sessions.get(session_id)


# --------------------------------
# Add Interview Interaction
# --------------------------------

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


# --------------------------------
# Add Face Monitoring Event
# --------------------------------

def add_face_event(
    session_id: str,
    face_detected: bool,
    face_count: int
):
    session = sessions.get(session_id)

    if not session:
        return None

    event = {
        "face_detected": face_detected,
        "face_count": face_count
    }

    session["face_events"].append(event)

    return event


# --------------------------------
# End Session
# --------------------------------

def end_session(session_id: str):
    session = sessions.get(session_id)

    if not session:
        return None

    session["status"] = "completed"

    return session