import whisper
import os

_model = None


def get_whisper_model():
    global _model

    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model("base")

    return _model


def transcribe_audio(filename):
    if not os.path.exists(filename):
        return {
            "status": "error",
            "message": "Audio file not found"
        }

    model = get_whisper_model()

    print("Transcribing audio...")

    result = model.transcribe(filename)

    text = result.get("text", "").strip()

    return {
        "status": "success",
        "text": text
    }