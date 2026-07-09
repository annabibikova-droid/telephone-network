from storage import load_archive, add_message
from embeddings import get_embedding
from semantic_search import find_best_match


def main():

    archive = load_archive()

    user_message = input("Leave a message: ")

    user_embedding = get_embedding(user_message)

    best_match = find_best_match(user_embedding, archive["messages"])

    print()
    print("☎ Someone answered:")
    print()
    print(best_match["text"])

    add_message(archive, user_message)


if __name__ == "__main__":
    main()
