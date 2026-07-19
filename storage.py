import json
from datetime import datetime

ARCHIVE_FILE = "archive.json"


def load_archive():
    """Load the entire archive from archive.json."""

    with open(ARCHIVE_FILE, "r", encoding="utf-8") as file:
        archive = json.load(file)

    return archive


def save_archive(archive):
    """Save the archive back to archive.json."""

    with open(ARCHIVE_FILE, "w", encoding="utf-8") as file:
        json.dump(
            archive,
            file,
            indent=4,
            ensure_ascii=False,
        )


def get_next_message_id(archive):
    """Return the next available message ID."""

    messages = archive["messages"]

    if not messages:
        return 1

    return max(message["id"] for message in messages) + 1


def add_message(archive, text, embedding, audio):
    """Add a new message to the archive and return it."""

    message = {
        "id": get_next_message_id(archive),
        "text": text,
        "embedding": embedding,
        "audio": audio,
        "timestamp": datetime.now().isoformat(),
        "phone_id": "houston-01",
        "location": {
            "city": "Houston",
            "country": "USA",
        },
        "language": "en",
        "duration": None,
        "played_count": 0,
    }

    archive["messages"].append(message)

    save_archive(archive)

    return message


def increment_played_count(message_id):
    """Increase an archived message's played count."""

    archive = load_archive()

    for message in archive["messages"]:

        if message["id"] == message_id:
            message["played_count"] += 1
            save_archive(archive)
            return
