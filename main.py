import os


def load_messages():

    folder = "messages"

    messages = []

    for filename in os.listdir(folder):

        filepath = os.path.join(folder, filename)

        with open(filepath, "r") as file:

            message = {"text": file.read(), "filename": filename}

            messages.append(message)

    return messages


messages = load_messages()

for message in messages:

    print(message["text"])
