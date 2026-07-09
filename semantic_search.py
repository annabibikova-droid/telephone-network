import numpy as np


def similarity(embedding1, embedding2):
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)

    return np.dot(embedding1, embedding2) / (
        np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
    )


def find_best_match(user_embedding, messages):

    best_message = None
    best_score = -1

    for message in messages:

        score = similarity(user_embedding, message["embedding"])

        if score > best_score:
            best_score = score
            best_message = message

    return best_message
