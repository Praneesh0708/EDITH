import whisper


def transcribe_audio(filename="speech/test.wav"):
    print("Loading Whisper model...")

    model = whisper.load_model("base")

    print("Transcribing audio...")

    result = model.transcribe(filename)

    print("\nEDITH heard:")
    print(result["text"])


if __name__ == "__main__":
    transcribe_audio()