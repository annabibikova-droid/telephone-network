from storage import load_archive, add_message
from embeddings import get_embedding
from semantic_search import find_best_match
from audio import record_audio, play_audio
from speech import transcribe_audio


def main():

    archive = load_archive()

    filename = record_audio()

    user_message = transcribe_audio(filename)

    print()
    print("Transcript:")
    print(user_message)
    print()

    user_embedding = get_embedding(user_message)

    best_match = find_best_match(user_embedding, archive["messages"])

    if best_match is not None:
        print()
        print("☎ Someone answered:")
        print()
        print(best_match["text"])
        print()

        print("Matching audio file:", best_match["audio"])

        if best_match["audio"] is not None:
            play_audio(best_match["audio"])
        else:
            print("⚠ This message doesn't have an audio recording.")

    else:
        print()
        print("☎ You're the first person to leave a message.")
        print("No previous recordings are available yet.")

    add_message(
        archive,
        user_message,
        user_embedding,
        filename,
    )


if __name__ == "__main__":
    main()
