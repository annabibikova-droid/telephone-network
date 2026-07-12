from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def transcribe_audio(filename):
    """Transcribe an audio file into text."""

    with open(filename, "rb") as audio_file:

        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file,
        )

    return transcript.text
