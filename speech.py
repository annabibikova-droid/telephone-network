from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def transcribe_audio(filename):
    """Transcribe an audio recording and return cleaned text."""

    with open(filename, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file,
        )

    text = transcript.text.strip()

    if not text:
        raise ValueError("The recording did not contain recognizable speech.")

    return text
