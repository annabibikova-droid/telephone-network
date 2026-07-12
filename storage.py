import json
from datetime import datetime


def load_archive():
    """Load the entire archive from archive.json."""

    with open("archive.json", "r", encoding="utf-8") as file:
        archive = json.load(file)

    return archive


def save_archive(archive):
    """Save the archive back to archive.json."""

    with open("archive.json", "w", encoding="utf-8") as file:
        json.dump(archive, file, indent=4)


def add_message(archive, text, embedding, audio):
    """Add a new message to the archive."""

    message = {
        "id": len(archive["messages"]) + 1,
        "text": text,
        "embedding": embedding,
        "audio": audio,
        "timestamp": datetime.now().isoformat(),
        "phone_id": "houston-01",
        "location": {"city": "Houston", "country": "USA"},
        "language": "en",
        "duration": None,
        "played_count": 0,
    }

    archive["messages"].append(message)

    save_archive(archive)
