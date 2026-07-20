from state_machine import StateMachine, State, Event

import audio
import display
import embeddings
import keyboard
import semantic_search
import speech
import storage
import time


def reset_current_session(phone):
    """Clear temporary data from the previous phone call."""

    phone.current_recording = None
    phone.current_transcript = None
    phone.current_embedding = None
    phone.matched_message = None
    phone.match_score = None


def handle_state(state, phone):

    if state is None:
        return

    # -----------------------------
    # RECORDING
    # -----------------------------

    if state == State.RECORDING:

        audio.play_beep()

        try:
            filename = audio.record_audio(
                max_duration=20,
                progress_callback=display.show_recording_progress,
            )

            phone.current_recording = filename

        except Exception as error:
            display.terminal_print(f"Recording failed.\n\n{error}")
            time.sleep(3)

            reset_current_session(phone)
            phone.change_state(State.IDLE)
            return

        new_state = phone.handle_event(Event.RECORDING_FINISHED)
        handle_state(new_state, phone)

    # -----------------------------
    # PROCESSING
    # -----------------------------
    elif state == State.PROCESSING:

        time.sleep(0.75)

        try:
            phone.current_transcript = speech.transcribe_audio(phone.current_recording)

            new_embedding = embeddings.get_embedding(phone.current_transcript)

            archive = storage.load_archive()

            existing_messages = archive["messages"]

            phone.matched_message = semantic_search.find_best_match(
                new_embedding,
                existing_messages,
            )

            storage.add_message(
                archive,
                phone.current_transcript,
                new_embedding,
                phone.current_recording,
            )

        except Exception as error:
            display.terminal_print(f"Processing failed.\n\n{error}")

            time.sleep(4)

            reset_current_session(phone)
            phone.change_state(State.IDLE)
            return

        display.searching(duration=2)

        if phone.matched_message is None:
            display.terminal_print(
                "Message saved.\n\n" "No earlier messages\n" "in the archive."
            )

            time.sleep(4)

            reset_current_session(phone)
            phone.change_state(State.IDLE)
            return

        new_state = phone.handle_event(Event.SEARCH_COMPLETE)

        handle_state(new_state, phone)

    # -----------------------------
    # DISPLAYING MESSAGE
    # -----------------------------

    elif state == State.DISPLAYING_MESSAGE:

        message = phone.matched_message

        display.show_location(message)

        time.sleep(0.8)

        playback = None

        audio_filename = message.get("audio")

        if audio_filename:
            try:
                playback = audio.play_audio_async(audio_filename)
            except Exception as error:
                print(f"\nPlayback failed: {error}")

        display.type_message(message["text"])

        if playback is not None:
            playback.join()

            try:
                storage.increment_played_count(message["id"])
            except Exception:
                pass

        start = time.time()

        while time.time() - start < 8:

            display.update()

            if keyboard.is_pressed("h"):

                while keyboard.is_pressed("h"):
                    time.sleep(0.01)

                reset_current_session(phone)
                phone.change_state(State.IDLE)
                return

            time.sleep(0.05)

        new_state = phone.handle_event(Event.PLAYBACK_COMPLETE)

        reset_current_session(phone)

        handle_state(new_state, phone)


def main():

    phone = StateMachine()

    while True:

        display.update()

        if keyboard.is_pressed("q"):
            break

        elif keyboard.is_pressed("h"):

            while keyboard.is_pressed("h"):
                time.sleep(0.01)

            if phone.state == State.IDLE:
                reset_current_session(phone)

                new_state = phone.handle_event(Event.HOOK_LIFTED)

                handle_state(new_state, phone)

            else:
                reset_current_session(phone)
                phone.change_state(State.IDLE)

            time.sleep(0.15)

        elif keyboard.is_pressed("r"):

            while keyboard.is_pressed("r"):
                time.sleep(0.01)

            new_state = phone.handle_event(Event.ROTARY_TURNED)

            handle_state(new_state, phone)

            time.sleep(0.15)

        time.sleep(0.01)


if __name__ == "__main__":
    main()
