import os
import time

TYPE_SPEED = 0.04
MESSAGE_SPEED = 0.035


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def update():
    # Nothing to update anymore.
    pass


def terminal_print(text, speed=TYPE_SPEED):

    clear()

    for character in text:
        print(character, end="", flush=True)
        time.sleep(speed)


def show(state):

    match state.name:

        case "IDLE":
            show_idle()

        case "WAITING_FOR_DIAL":
            show_waiting()

        case "RECORDING":
            show_recording()

        case "PROCESSING":
            show_processing()

        case "DISPLAYING_MESSAGE":
            pass


def show_idle():

    terminal_print("Leave a message\n\n" "Hear another")


def show_waiting():

    terminal_print("Turn dial\n" "to begin recording.\n\n" "Turn again\n" "to finish.")


def show_recording():

    clear()
    print("Recording", flush=True)


def show_processing():

    terminal_print("Message received.")


def show_recording_progress(remaining):

    clear()

    print("Recording")
    print()
    print("█" * remaining, flush=True)


def searching(duration=2):

    frames = [
        "Searching archive",
        "Searching archive.",
        "Searching archive..",
        "Searching archive...",
    ]

    start = time.time()
    index = 0

    while time.time() - start < duration:

        clear()

        print("Message received.")
        print()
        print(frames[index], flush=True)

        index = (index + 1) % len(frames)

        time.sleep(0.35)


def show_location(message):

    location = message.get("location", {})

    city = location.get("city", "Unknown")
    country = location.get("country", "")

    timestamp = message.get("timestamp", "")

    try:
        date = time.strftime(
            "%B %d, %Y",
            time.strptime(timestamp[:10], "%Y-%m-%d"),
        )

        # Remove a leading zero from dates such as "July 05".
        date = date.replace(" 0", " ")

    except (ValueError, TypeError):
        date = "Unknown date"

    if country:
        location_text = f"{city}, {country}"
    else:
        location_text = city

    terminal_print(f"{location_text}\n\n{date}")


def type_message(text):

    terminal_print(text, speed=MESSAGE_SPEED)
