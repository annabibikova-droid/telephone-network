from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding