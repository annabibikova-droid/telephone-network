from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def get_embedding(text):
    """Generate an embedding for a piece of text."""

    cleaned_text = text.strip()

    if not cleaned_text:
        raise ValueError("Cannot generate an embedding for empty text.")

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=cleaned_text,
    )

    return response.data[0].embedding
