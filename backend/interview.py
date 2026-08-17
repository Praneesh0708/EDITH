
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
    get_conversation_memory,
)

from backend.services.interview_report import (
    generate_interview_report,
    format_interview_report,
)

from backend.services.voice_analyzer import analyze_voice

from backend.services.speech_service import transcribe_audio

from backend.services.face_analyzer import analyze_face

from backend.services.context_analyzer import extract_answer_context

from backend.services.gemini_question_generator import (
    generate_gemini_question,
)

from backend.services.human_answer_evaluator import (
    evaluate_answer_human_like,
)

from backend.services.dynamic_question_generator import (
    generate_dynamic_question,
)


# ============================================================
# INTERVIEW ROUTER
# ============================================================

router = APIRouter(
    prefix="/interview",
    tags=["Interview"],
)


# ============================================================
# HELPER - NORMALIZE QUESTION
# ============================================================

def normalize_question(question):
    if not isinstance(question, str):
        return ""

    return (
        question
        .strip()
        .lower()
        .replace("?", "")
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace(":", "")
        .replace(";", "")
    )


# ============================================================
# HELPER - CHECK DUPLICATE QUESTION
# ============================================================

def question_already_asked(
    session,
    question,
):
    new_question = normalize_question(question)

    if not new_question:
        return True

    for old_question in session.get(
        "questions",
        [],
    ):
        old_normalized = normalize_question(
            old_question
        )

        if old_normalized == new_question:
            return True

    return False


# ============================================================
# HELPER - GET UNIQUE QUESTION
# ============================================================

def get_unique_question(
    session,
    generated_question,
    previous_question,
    answer,
    context,
    analysis,
):
    """
    Prevent Gemini from returning a question
    that already exists in the interview.

    If Gemini repeats a question, use the
    dynamic question generator instead.
    """

    if isinstance(
        generated_question,
        dict,
    ):
        candidate = generated_question.get(
            "question",
            "",
        )
    else:
        candidate = str(
            generated_question or ""
        )

    candidate = candidate.strip()

    # --------------------------------------------------------
    # Gemini produced a new question
    # --------------------------------------------------------

    if (
        candidate
        and not question_already_asked(
            session,
            candidate,
        )
    ):
        if isinstance(
            generated_question,
            dict,
        ):
            return generated_question

        return {
            "status": "success",
            "question": candidate,
            "difficulty": "medium",
            "source": "gemini",
        }

    # --------------------------------------------------------
    # Gemini repeated a question
    # --------------------------------------------------------

    print(
        "⚠️ Gemini generated a repeated question."
    )

    print(
        "🔄 Switching to dynamic question generator."
    )

    # Build temporary list of previous questions
    asked_questions = session.get(
        "questions",
        [],
    )

    dynamic_result = generate_dynamic_question(
        previous_question=previous_question,
        answer=answer,
        context=context,
        analysis=analysis,
    )

    if isinstance(
        dynamic_result,
        dict,
    ):
        dynamic_question = dynamic_result.get(
            "question",
            "",
        )
    else:
        dynamic_question = str(
            dynamic_result or ""
        )

    # --------------------------------------------------------
    # Dynamic generator produced a unique question
    # --------------------------------------------------------

    if (
        dynamic_question
        and not question_already_asked(
            session,
            dynamic_question,
        )
    ):
        if isinstance(
            dynamic_result,
            dict,
        ):
            return dynamic_result

        return {
            "status": "fallback",
            "question": dynamic_question,
            "difficulty": "medium",
            "source": "dynamic",
        }

    # --------------------------------------------------------
    # Final guaranteed unique fallback
    # --------------------------------------------------------

    question_number = (
        len(asked_questions) + 1
    )

    fallback_question = (
        "Based on your previous answer, "
        "what is one technical decision you "
        f"would improve if you had another chance "
        f"in question {question_number}?"
    )

    # Make absolutely sure it is unique
    counter = 1

    while question_already_asked(
        session,
        fallback_question,
    ):
        counter += 1

        fallback_question = (
            "What is another technical lesson "
            f"you gained from your experience "
            f"that you have not discussed yet "
            f"({counter})?"
        )

    return {
        "status": "fallback",
        "question": fallback_question,
        "difficulty": "medium",
        "source": "unique_fallback",
    }


# ============================================================
# INTERVIEW HOME
# ============================================================

@router.get("/")
def interview_home():

    return {
        "status": "success",
        "message": "EDITH Interview Engine is ready",
    }


# ============================================================
# START INTERVIEW
# ============================================================

@router.post("/start")
def start_interview():

    session = create_session()

    first_question = (
        "Tell me about yourself."
    )

    session["questions"].append(
        first_question
    )

    return {
        "status": "success",
        "message": "Interview started",
        "session_id": session["session_id"],
        "question_number": 1,
        "question": first_question,
    }


# ============================================================
# SUBMIT TEXT ANSWER
# ============================================================

@router.post("/answer")
def submit_answer(data: dict):

    session_id = data.get(
        "session_id"
    )

    answer = data.get(
        "answer",
        "",
    )

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID",
        }

    # --------------------------------------------------------
    # Current question
    # --------------------------------------------------------

    question_number = session.get(
        "question_number",
        1,
    )

    questions = session.get(
        "questions",
        [],
    )

    if not questions:

        question = (
            "Tell me about yourself."
        )

    elif question_number > len(
        questions
    ):

        question = questions[-1]

    else:

        question = questions[
            question_number - 1
        ]

    # --------------------------------------------------------
    # Analyze answer
    # --------------------------------------------------------

    analysis = analyze_answer(
        question,
        answer,
    )

    context = extract_answer_context(
        answer
    )

    # --------------------------------------------------------
    # Human evaluation
    # --------------------------------------------------------

    human_evaluation = (
        evaluate_answer_human_like(
            question=question,
            answer=answer,
            context=context,
            analysis=analysis,
        )
    )

    # --------------------------------------------------------
    # Store interaction
    # --------------------------------------------------------

    add_interaction(
        session_id,
        question,
        answer,
        analysis,
        human_evaluation,
    )

    # --------------------------------------------------------
    # Conversation memory
    # --------------------------------------------------------

    conversation_memory = (
        get_conversation_memory(
            session_id
        )
    )

    # --------------------------------------------------------
    # Generate Gemini question
    # --------------------------------------------------------

    generated_question = (
        generate_gemini_question(
            previous_question=question,
            answer=answer,
            context=context,
            analysis=analysis,
            conversation_memory=conversation_memory,
        )
    )

    # --------------------------------------------------------
    # GUARANTEE UNIQUE QUESTION
    # --------------------------------------------------------

    next_question = get_unique_question(
        session=session,
        generated_question=generated_question,
        previous_question=question,
        answer=answer,
        context=context,
        analysis=analysis,
    )

    # --------------------------------------------------------
    # Store next question
    # --------------------------------------------------------

    if next_question.get(
        "question"
    ):

        new_question = next_question[
            "question"
        ]

        if not question_already_asked(
            session,
            new_question,
        ):

            session[
                "questions"
            ].append(
                new_question
            )

            # Move session to next question
            session[
                "question_number"
            ] = len(
                session["questions"]
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

        "human_evaluation": human_evaluation,

        "context": context,

        "conversation_memory": conversation_memory,

        "next_question": next_question,
    }


# ============================================================
# GET INTERVIEW SESSION
# ============================================================

@router.get("/session/{session_id}")
def get_interview_session(
    session_id: str,
):

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Session not found",
        }

    return {
        "status": "success",
        "session": session,
    }


# ============================================================
# END INTERVIEW
# ============================================================

@router.post("/end/{session_id}")
def finish_interview(
    session_id: str,
):

    session = end_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Session not found",
        }

    report = generate_interview_report(
        session
    )

    formatted_report = (
        format_interview_report(
            report
        )
    )

    return {

        "status": "success",

        "message": "Interview completed",

        "session": session,

        "report": report,

        "formatted_report": formatted_report,
    }


# ============================================================
# VOICE ANALYSIS
# ============================================================

@router.post("/voice")
def analyze_voice_answer(
    audio_file: UploadFile = File(...),
):

    result = analyze_voice(
        audio_file.file
    )

    return {

        "status": "success",

        "message": "Voice analyzed",

        "voice_analysis": result,
    }


# ============================================================
# VOICE ANSWER
# ============================================================

@router.post("/voice-answer")
async def voice_answer(

    session_id: str = Form(...),

    audio_file: UploadFile = File(...),
):

    # --------------------------------------------------------
    # Get session
    # --------------------------------------------------------

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID",
        }

    # --------------------------------------------------------
    # Save audio
    # --------------------------------------------------------

    filename = (
        f"backend/test_voice_"
        f"{session_id}.webm"
    )

    with open(
        filename,
        "wb",
    ) as f:

        f.write(
            await audio_file.read()
        )

    # --------------------------------------------------------
    # Whisper
    # --------------------------------------------------------

    answer = transcribe_audio(
        filename
    )

    if isinstance(
        answer,
        dict,
    ):

        answer = answer.get(
            "text",
            "",
        )

    if not isinstance(
        answer,
        str,
    ):

        answer = str(
            answer
        )

    answer = answer.strip()

    # --------------------------------------------------------
    # Current question
    # --------------------------------------------------------

    question_number = session.get(
        "question_number",
        1,
    )

    questions = session.get(
        "questions",
        [],
    )

    if not questions:

        question = (
            "Tell me about yourself."
        )

    elif question_number > len(
        questions
    ):

        question = questions[-1]

    else:

        question = questions[
            question_number - 1
        ]

    # --------------------------------------------------------
    # Analyze answer
    # --------------------------------------------------------

    analysis = analyze_answer(
        question,
        answer,
    )

    context = extract_answer_context(
        answer
    )

    # --------------------------------------------------------
    # Human evaluation
    # --------------------------------------------------------

    human_evaluation = (
        evaluate_answer_human_like(
            question=question,
            answer=answer,
            context=context,
            analysis=analysis,
        )
    )

    # --------------------------------------------------------
    # Store interaction
    # --------------------------------------------------------

    add_interaction(
        session_id,
        question,
        answer,
        analysis,
        human_evaluation,
    )

    # --------------------------------------------------------
    # Conversation memory
    # --------------------------------------------------------

    conversation_memory = (
        get_conversation_memory(
            session_id
        )
    )

    # --------------------------------------------------------
    # Generate Gemini question
    # --------------------------------------------------------

    generated_question = (
        generate_gemini_question(
            previous_question=question,
            answer=answer,
            context=context,
            analysis=analysis,
            conversation_memory=conversation_memory,
        )
    )

    # --------------------------------------------------------
    # GUARANTEE UNIQUE QUESTION
    # --------------------------------------------------------

    next_question = get_unique_question(
        session=session,
        generated_question=generated_question,
        previous_question=question,
        answer=answer,
        context=context,
        analysis=analysis,
    )

    # --------------------------------------------------------
    # Store next question
    # --------------------------------------------------------

    if next_question.get(
        "question"
    ):

        new_question = next_question[
            "question"
        ]

        if not question_already_asked(
            session,
            new_question,
        ):

            session[
                "questions"
            ].append(
                new_question
            )

            session[
                "question_number"
            ] = len(
                session["questions"]
            )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "status": "success",

        "message": "Voice answer processed",

        "session_id": session_id,

        "question": question,

        "transcribed_answer": answer,

        "analysis": analysis,

        "human_evaluation": human_evaluation,

        "context": context,

        "conversation_memory": conversation_memory,

        "next_question": next_question,
    }


# ============================================================
# FACE ANALYSIS
# ============================================================

@router.post("/face")
async def analyze_face_frame(

    session_id: str,

    image_file: UploadFile = File(...),
):

    session = get_session(
        session_id
    )

    if not session:

        return {
            "status": "error",
            "message": "Invalid session ID",
        }

    image_bytes = (
        await image_file.read()
    )

    image_array = np.frombuffer(
        image_bytes,
        np.uint8,
    )

    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR,
    )

    if image is None:

        return {
            "status": "error",
            "message": "Invalid image file",
        }

    result = analyze_face(
        image
    )

    add_face_event(

        session_id,

        result.get(
            "face_detected",
            False,
        ),

        result.get(
            "face_count",
            0,
        ),
    )

    return {

        "status": "success",

        "message": (
            "Face analyzed and stored"
        ),

        "session_id": session_id,

        "face_analysis": result,
    }