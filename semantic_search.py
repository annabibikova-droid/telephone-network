import numpy as np


def similarity(embedding1, embedding2):
    """Calculate cosine similarity between two embeddings."""

    embedding1 = np.asarray(embedding1, dtype=float)
    embedding2 = np.asarray(embedding2, dtype=float)

    denominator = np.linalg.norm(embedding1) * np.linalg.norm(embedding2)

    if denominator == 0:
        return 0.0

    return float(np.dot(embedding1, embedding2) / denominator)


def find_best_match(user_embedding, messages):
    """Return the archived message with the closest embedding."""

    best_message = None
    best_score = -1.0

    for message in messages:

        message_embedding = message.get("embedding")

        if not message_embedding:
            continue

        score = similarity(
            user_embedding,
            message_embedding,
        )

        if score > best_score:
            best_score = score
            best_message = message

    return best_message
