import speech_recognition as sr


FILLER_WORDS = [
    "um",
    "uh",
    "like",
    "actually",
    "basically",
    "you know",
    "so"
]


def analyze_voice(audio_file):
    """
    Convert speech audio into text and calculate
    basic voice communication metrics.
    """

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)

        words = transcript.split()
        word_count = len(words)

        transcript_lower = transcript.lower()

        filler_count = 0

        for filler in FILLER_WORDS:
            filler_count += transcript_lower.count(filler)

        if word_count > 0:
            filler_rate = round(
                (filler_count / word_count) * 100,
                2
            )
        else:
            filler_rate = 0

        return {
            "status": "success",
            "transcript": transcript,
            "word_count": word_count,
            "filler_words": filler_count,
            "filler_rate": filler_rate
        }

    except sr.UnknownValueError:

        return {
            "status": "error",
            "message": "Speech could not be understood.",
            "transcript": "",
            "word_count": 0,
            "filler_words": 0,
            "filler_rate": 0
        }

    except sr.RequestError as error:

        return {
            "status": "error",
            "message": f"Speech recognition service error: {error}",
            "transcript": "",
            "word_count": 0,
            "filler_words": 0,
            "filler_rate": 0
        }

    except Exception as error:

        return {
            "status": "error",
            "message": str(error),
            "transcript": "",
            "word_count": 0,
            "filler_words": 0,
            "filler_rate": 0
        }