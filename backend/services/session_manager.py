import uuid


# ============================================================
# Store Active Interview Sessions
# ============================================================

sessions = {}


# ============================================================
# Create Session
# ============================================================

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

        # Current question number
        "question_number": 1
    }

    return sessions[session_id]


# ============================================================
# Get Session
# ============================================================

def get_session(session_id: str):
    return sessions.get(session_id)


# ============================================================
# Add Interview Interaction
# ============================================================

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


# ============================================================
# Get Conversation Memory
# ============================================================

def get_conversation_memory(session_id: str):
    """
    Build a compact memory of the interview
    for EDITH's adaptive question engine.
    """

    session = sessions.get(session_id)

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

    # --------------------------------------------------------
    # Make sure only complete interactions are included
    # --------------------------------------------------------

    count = min(
        len(questions),
        len(answers),
        len(analyses)
    )

    # --------------------------------------------------------
    # Build Memory
    # --------------------------------------------------------

    for i in range(count):

        analysis = analyses[i]

        if not isinstance(analysis, dict):
            analysis = {}

        memory.append({

            "question_number": i + 1,

            "question": questions[i],

            "answer": answers[i],

            "analysis": {

                "overall_score": analysis.get(
                    "overall_score",
                    0
                ),

                "keywords": analysis.get(
                    "keywords",
                    []
                )
            }
        })

    return memory


# ============================================================
# Add Face Monitoring Event
# ============================================================

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


# ============================================================
# End Session
# ============================================================

def end_session(session_id: str):

    session = sessions.get(session_id)

    if not session:
        return None

    session["status"] = "completed"

    return session


# ============================================================
# TEST CONVERSATION MEMORY
# ============================================================

if __name__ == "__main__":

    session = create_session()

    session_id = session["session_id"]

    # --------------------------------------------------------
    # Test Interaction 1
    # --------------------------------------------------------

    add_interaction(
        session_id,

        "Tell me about yourself.",

        "I am a Python developer.",

        {
            "overall_score": 8,
            "keywords": [
                "python"
            ]
        }
    )

    # --------------------------------------------------------
    # Test Interaction 2
    # --------------------------------------------------------

    add_interaction(
        session_id,

        "How did you use Python?",

        "I used Python with FastAPI.",

        {
            "overall_score": 9,
            "keywords": [
                "python",
                "fastapi"
            ]
        }
    )

    # --------------------------------------------------------
    # Get Memory
    # --------------------------------------------------------

    memory = get_conversation_memory(
        session_id
    )

    # --------------------------------------------------------
    # Display Memory
    # --------------------------------------------------------

    print()
    print("🧠 EDITH CONVERSATION MEMORY")
    print("============================")

    for item in memory:

        print()
        print(
            "Question:",
            item["question"]
        )

        print(
            "Answer:",
            item["answer"]
        )

        print(
            "Analysis:",
            item["analysis"]
        )