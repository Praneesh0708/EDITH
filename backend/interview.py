from fastapi import APIRouter, UploadFile, File

from services.answer_analyzer import analyze_answer
from services.question_engine import generate_next_question
from services.session_manager import (
    create_session,
    get_session,
    add_interaction,
    end_session
)
from services.interview_report import generate_interview_report
from services.voice_analyzer import analyze_voice

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


# --------------------------------
# Interview Home
# --------------------------------

@router.get("/")
def interview_home():
    return {
        "status": "success",
        "message": "EDITH Interview Engine is ready"
    }


# --------------------------------
# Start Interview
# --------------------------------

@router.post("/start")
def start_interview():

    session = create_session()

    first_question = "Tell me about yourself."

    session["questions"].append(first_question)

    return {
        "status": "success",
        "message": "Interview started",
        "session_id": session["session_id"],
        "question_number": 1,
        "question": first_question
    }


# --------------------------------
# Submit Answer
# --------------------------------

@router.post("/answer")
def submit_answer(data: dict):

    session_id = data.get("session_id")
    answer = data.get("answer", "")

    session = get_session(session_id)

    if not session:
        return {
            "status": "error",
            "message": "Invalid session ID"
        }

    question_number = session["question_number"]

    if question_number > len(session["questions"]):
        question = session["questions"][-1]
    else:
        question = session["questions"][question_number - 1]

    # Analyze answer
    analysis = analyze_answer(
        question,
        answer
    )

    # Store interaction
    add_interaction(
        session_id,
        question,
        answer,
        analysis
    )

    # Generate next question
    next_question = generate_next_question(
        question,
        answer,
        analysis
    )

    # Store next question
    session["questions"].append(
        next_question["question"]
    )

    return {
        "status": "success",
        "message": "Answer analyzed",
        "session_id": session_id,
        "question_number": question_number,
        "question": question,
        "answer": answer,
        "analysis": analysis,
        "next_question": next_question
    }


# --------------------------------
# Get Session
# --------------------------------

@router.get("/session/{session_id}")
def get_interview_session(session_id: str):

    session = get_session(session_id)

    if not session:
        return {
            "status": "error",
            "message": "Session not found"
        }

    return {
        "status": "success",
        "session": session
    }


# --------------------------------
# End Interview
# --------------------------------

@router.post("/end/{session_id}")
def finish_interview(session_id: str):

    session = end_session(session_id)

    if not session:
        return {
            "status": "error",
            "message": "Session not found"
        }

    report = generate_interview_report(session)

    return {
        "status": "success",
        "message": "Interview completed",
        "session": session,
        "report": report
    }
@router.post("/voice")
def analyze_voice_answer(audio_file: UploadFile = File(...)):

    result = analyze_voice(
        audio_file.file
    )

    return {
        "status": "success",
        "message": "Voice analyzed",
        "voice_analysis": result
    }