import json
import os

print(os.getcwd())
print("Writing to:", os.path.abspath("archive.json"))

# Load existing embeddings
with open("embeddings.json", "r", encoding="utf-8") as file:
    embeddings = json.load(file)

archive = {"version": 1, "messages": []}

folder = "messages"

# Process each message file
for filename in sorted(os.listdir(folder)):
    filepath = os.path.join(folder, filename)

    with open(filepath, "r", encoding="utf-8") as file:
        text = file.read().strip()

    message = {
        "id": len(archive["messages"]) + 1,
        "text": text,
        "embedding": embeddings.get(filename, []),
        "audio": None,
        "timestamp": None,
        "phone_id": "houston-01",
        "location": {"city": "Houston", "country": "USA"},
        "language": "en",
        "duration": None,
        "played_count": 0,
    }
    print(filename)
    print(text)
    print(len(embeddings.get(filename, [])))
    print("----------------")
    archive["messages"].append(message)

# Save the new archive
with open("archive.json", "w", encoding="utf-8") as file:
    json.dump(archive, file, indent=4)

print(archive["messages"][0]["embedding"][:5])
print(len(archive["messages"][0]["embedding"]))
