from fastapi import APIRouter, UploadFile, File, Form

import cv2
import numpy as np

from backend.services.answer_analyzer import analyze_answer

from backend.services.session_manager import (
    create_session,
    get_session,
    add_interaction,
    add_face_event,
    end_session,
    get_conversation_memory
)

from backend.services.interview_report import (
    generate_interview_report
)

from backend.services.voice_analyzer import (
    analyze_voice
)

from backend.services.speech_service import (
    transcribe_audio
)

from backend.services.face_analyzer import (
    analyze_face
)

from backend.services.context_analyzer import (
    extract_answer_context
)

from backend.services.gemini_question_generator import (
    generate_gemini_question
)


# ============================================================
# INTERVIEW ROUTER
# ============================================================

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


# ============================================================
# INTERVIEW HOME
# ============================================================

@router.get("/")
def interview_home():

    return {
        "status": "success",
        "message": "EDITH Interview Engine is ready"
    }


# ============================================================
# START INTERVIEW
# ============================================================

@router.post("/start")
def start_interview():

    session = create_session()

    first_question = "Tell me about yourself."

    session["questions"].append(
        first_question
    )

    return {
        "status": "success",
        "message": "Interview started",
        "session_id": session["session_id"],
        "question_number": 1,
        "question": first_question
    }


# ============================================================
# SUBMIT TEXT ANSWER
# ============================================================

@router.post("/answer")
def submit_answer(data: dict):

    session_id = data.get("session_id")

    answer = data.get(
        "answer",
        ""
    )

    # --------------------------------------------------------
    # Get Session
    # --------------------------------------------------------

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID"
        }

    # --------------------------------------------------------
    # Get Current Question
    # --------------------------------------------------------

    question_number = session[
        "question_number"
    ]

    if question_number > len(
        session["questions"]
    ):

        question = session[
            "questions"
        ][-1]

    else:

        question = session[
            "questions"
        ][question_number - 1]

    # --------------------------------------------------------
    # Analyze Answer
    # --------------------------------------------------------

    analysis = analyze_answer(
        question,
        answer
    )

    # --------------------------------------------------------
    # Extract Context
    # --------------------------------------------------------

    context = extract_answer_context(
        answer
    )

    # --------------------------------------------------------
    # Store Interaction
    # --------------------------------------------------------

    add_interaction(
        session_id,
        question,
        answer,
        analysis
    )

    # --------------------------------------------------------
    # Get Conversation Memory
    # --------------------------------------------------------

    conversation_memory = (
        get_conversation_memory(
            session_id
        )
    )

    # --------------------------------------------------------
    # Generate Personalized Question
    # --------------------------------------------------------

    next_question = generate_gemini_question(

        previous_question=question,

        answer=answer,

        context=context,

        analysis=analysis,

        conversation_memory=conversation_memory
    )

    # --------------------------------------------------------
    # Store Generated Question
    # --------------------------------------------------------

    if next_question.get("question"):

        session[
            "questions"
        ].append(
            next_question["question"]
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "status": "success",

        "message": "Answer analyzed",

        "session_id": session_id,

        "question_number": question_number,

        "question": question,

        "answer": answer,

        "analysis": analysis,

        "context": context,

        "conversation_memory": conversation_memory,

        "next_question": next_question
    }


# ============================================================
# GET INTERVIEW SESSION
# ============================================================

@router.get("/session/{session_id}")
def get_interview_session(
    session_id: str
):

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Session not found"
        }

    return {
        "status": "success",
        "session": session
    }


# ============================================================
# END INTERVIEW
# ============================================================

@router.post("/end/{session_id}")
def finish_interview(
    session_id: str
):

    session = end_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Session not found"
        }

    report = generate_interview_report(
        session
    )

    return {

        "status": "success",

        "message": "Interview completed",

        "session": session,

        "report": report
    }


# ============================================================
# VOICE ANALYSIS
# ============================================================

@router.post("/voice")
def analyze_voice_answer(
    audio_file: UploadFile = File(...)
):

    result = analyze_voice(
        audio_file.file
    )

    return {

        "status": "success",

        "message": "Voice analyzed",

        "voice_analysis": result
    }


# ============================================================
# VOICE ANSWER + WHISPER TRANSCRIPTION
# ============================================================

@router.post("/voice-answer")
async def voice_answer(

    session_id: str = Form(...),

    audio_file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Get Session
    # --------------------------------------------------------

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID"
        }

    # --------------------------------------------------------
    # Save Uploaded Audio
    # --------------------------------------------------------

    filename = (
        f"backend/test_voice_"
        f"{session_id}.webm"
    )

    with open(
        filename,
        "wb"
    ) as f:

        f.write(
            await audio_file.read()
        )

    # --------------------------------------------------------
    # Whisper Transcription
    # --------------------------------------------------------

    answer = transcribe_audio(
        filename
    )

    # --------------------------------------------------------
    # Convert Whisper Result To Text
    # --------------------------------------------------------

    if isinstance(
        answer,
        dict
    ):

        answer = answer.get(
            "text",
            ""
        )

    if not isinstance(
        answer,
        str
    ):

        answer = str(answer)

    answer = answer.strip()

    # --------------------------------------------------------
    # Get Current Question
    # --------------------------------------------------------

    question_number = session[
        "question_number"
    ]

    if question_number > len(
        session["questions"]
    ):

        question = session[
            "questions"
        ][-1]

    else:

        question = session[
            "questions"
        ][question_number - 1]

    # --------------------------------------------------------
    # Analyze Answer
    # --------------------------------------------------------

    analysis = analyze_answer(
        question,
        answer
    )

    # --------------------------------------------------------
    # Extract Context
    # --------------------------------------------------------

    context = extract_answer_context(
        answer
    )

    # --------------------------------------------------------
    # Store Interaction
    # --------------------------------------------------------

    add_interaction(
        session_id,
        question,
        answer,
        analysis
    )

    # --------------------------------------------------------
    # Get Conversation Memory
    # --------------------------------------------------------

    conversation_memory = (
        get_conversation_memory(
            session_id
        )
    )

    # --------------------------------------------------------
    # Generate Gemini Question
    # --------------------------------------------------------

    next_question = generate_gemini_question(

        previous_question=question,

        answer=answer,

        context=context,

        analysis=analysis,

        conversation_memory=conversation_memory
    )

    # --------------------------------------------------------
    # Store Next Question
    # --------------------------------------------------------

    if next_question.get("question"):

        session[
            "questions"
        ].append(
            next_question["question"]
        )

    # --------------------------------------------------------
    # Return Result
    # --------------------------------------------------------

    return {

        "status": "success",

        "message": "Voice answer processed",

        "session_id": session_id,

        "question": question,

        "transcribed_answer": answer,

        "analysis": analysis,

        "context": context,

        "conversation_memory": conversation_memory,

        "next_question": next_question
    }


# ============================================================
# FACE ANALYSIS
# ============================================================

@router.post("/face")
async def analyze_face_frame(

    session_id: str,

    image_file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Get Interview Session
    # --------------------------------------------------------

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID"
        }

    # --------------------------------------------------------
    # Read Uploaded Image
    # --------------------------------------------------------

    image_bytes = await image_file.read()

    # --------------------------------------------------------
    # Convert Image Bytes To NumPy Array
    # --------------------------------------------------------

    image_array = np.frombuffer(
        image_bytes,
        np.uint8
    )

    # --------------------------------------------------------
    # Decode Image
    # --------------------------------------------------------

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )

    if image is None:

        return {
            "status": "error",
            "message": "Invalid image file"
        }

    # --------------------------------------------------------
    # Analyze Face
    # --------------------------------------------------------

    result = analyze_face(
        image
    )

    # --------------------------------------------------------
    # Store Face Event
    # --------------------------------------------------------

    add_face_event(

        session_id,

        result.get(
            "face_detected",
            False
        ),

        result.get(
            "face_count",
            0
        )
    )

    # --------------------------------------------------------
    # Return Result
    # --------------------------------------------------------

    return {

        "status": "success",

        "message": (
            "Face analyzed and stored"
        ),

        "session_id": session_id,

        "face_analysis": result
    }