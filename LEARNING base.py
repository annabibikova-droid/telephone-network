from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import os
import json

load_dotenv()

client = OpenAI()


def get_embedding(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding


def similarity(embedding1, embedding2):
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    return np.dot(embedding1, embedding2) / (
        np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )


def load_messages():
    folder = "messages"
    messages = []

    embeddings = load_embeddings()

    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)

        with open(filepath, "r") as file:
            text = file.read()

        if filename in embeddings:

            embedding = embeddings[filename]

        else:

            embedding = get_embedding(text)

            embeddings[filename] = embedding

        message = {
            "text": text,
            "filename": filename,
            "embedding": embedding,
        }

        messages.append(message)

    save_embeddings(embeddings)

    return messages


def load_embeddings():

    if not os.path.exists("embeddings.json"):
        return {}

    with open("embeddings.json", "r") as file:
        return json.load(file)


def save_embeddings(embeddings):

    with open("embeddings.json", "w") as file:
        json.dump(embeddings, file)


def find_best_match(user_message):
    messages = load_messages()
    user_embedding = get_embedding(user_message)
    best_message = None
    best_score = -1
    for message in messages:
        score = similarity(user_embedding, message["embedding"])
        if score > best_score:
            best_score = score
            best_message = message
    return best_message


def save_message(user_message):
    folder = "messages"

    files = os.listdir(folder)

    message_number = len(files) + 1

    filename = str(message_number) + ".txt"

    filepath = os.path.join(folder, filename)

    with open(filepath, "w") as file:
        file.write(user_message)

    embedding = get_embedding(user_message)

    embeddings = load_embeddings()

    embeddings[filename] = embedding

    save_embeddings(embeddings)


user_message = input("Leave a message: ")

result = find_best_match(user_message)

print()
print("☎ Someone answered:")
print()

print(result["text"])

save_message(user_message)
