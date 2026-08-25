from state_machine import StateMachine, State, Event

import audio
import display
import embeddings
import hardware
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


def drain_rotary_events():
    """Discard rotary turns that no longer belong to an active call."""

    while hardware.get_rotary_event() is not None:
        pass


def reset_to_idle(phone):
    """Stop playback, clear the session, and return the phone to IDLE."""

    audio.stop_audio()

    reset_current_session(phone)

    drain_rotary_events()

    if phone.state != State.IDLE:
        phone.change_state(State.IDLE)


def handset_replaced():
    """Return True if the handset is physically on the hook."""

    return hardware.handset_is_down()


def interruptible_wait(seconds):
    """
    Wait for a period of time while continuing to watch the hook.

    Returns False if the handset was replaced.
    Returns True if the entire wait completed.
    """

    start = time.time()

    while time.time() - start < seconds:

        if handset_replaced():
            return False

        time.sleep(0.02)

    return True


def type_message_interruptibly(text):
    """
    Type the returned message while continuously checking the hook.

    Returns False if the handset is replaced while the message is typing.
    """

    display.clear()

    for character in text:

        if handset_replaced():
            return False

        print(character, end="", flush=True)
        time.sleep(display.MESSAGE_SPEED)

    return True


def recording_should_stop():
    """
    Stop recording if:

    - the handset is replaced, or
    - the rotary dial is turned again.
    """

    if handset_replaced():
        return True

    rotary_event = hardware.get_rotary_event()

    if rotary_event == "ROTARY_TURNED":
        return True

    return False


def handle_state(state, phone):

    if state is None:
        return

    # -----------------------------
    # RECORDING
    # -----------------------------

    if state == State.RECORDING:

        audio.play_beep()

        # If the user hung up during the beep,
        # immediately cancel this call.
        if handset_replaced():
            reset_to_idle(phone)
            return

        try:
            filename = audio.record_audio(
                max_duration=20,
                progress_callback=display.show_recording_progress,
                stop_callback=recording_should_stop,
            )

            phone.current_recording = filename

        except Exception as error:
            display.terminal_print(f"Recording failed.\n\n{error}")

            time.sleep(3)

            reset_to_idle(phone)
            return

        # If recording stopped because the handset
        # was replaced, do not process/save it.
        if handset_replaced():
            reset_to_idle(phone)
            return

        new_state = phone.handle_event(Event.RECORDING_FINISHED)

        handle_state(new_state, phone)

    # -----------------------------
    # PROCESSING
    # -----------------------------

    elif state == State.PROCESSING:

        if not interruptible_wait(0.75):
            reset_to_idle(phone)
            return

        try:
            phone.current_transcript = speech.transcribe_audio(phone.current_recording)

            if handset_replaced():
                reset_to_idle(phone)
                return

            new_embedding = embeddings.get_embedding(phone.current_transcript)

            if handset_replaced():
                reset_to_idle(phone)
                return

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

            reset_to_idle(phone)
            return

        if handset_replaced():
            reset_to_idle(phone)
            return

        display.searching(duration=2)

        if handset_replaced():
            reset_to_idle(phone)
            return

        if phone.matched_message is None:

            display.terminal_print(
                "Message saved.\n\n" "No earlier messages\n" "in the archive."
            )

            if not interruptible_wait(4):
                reset_to_idle(phone)
                return

            reset_to_idle(phone)
            return

        new_state = phone.handle_event(Event.SEARCH_COMPLETE)

        handle_state(new_state, phone)

    # -----------------------------
    # DISPLAYING MESSAGE
    # -----------------------------

    elif state == State.DISPLAYING_MESSAGE:

        message = phone.matched_message

        display.show_location(message)

        if handset_replaced():
            reset_to_idle(phone)
            return

        if not interruptible_wait(0.8):
            reset_to_idle(phone)
            return

        playback = None

        audio_filename = message.get("audio")

        if audio_filename:
            try:
                playback = audio.play_audio_async(audio_filename)

            except Exception as error:
                print(f"\nPlayback failed: {error}")

        # Type the message while also watching
        # for the handset being replaced.
        completed_typing = type_message_interruptibly(message["text"])

        if not completed_typing:
            reset_to_idle(phone)
            return

        # Wait for audio playback to finish,
        # but continue monitoring the hook.
        if playback is not None:

            while playback.is_alive():

                if handset_replaced():
                    reset_to_idle(phone)
                    return

                time.sleep(0.02)

            try:
                storage.increment_played_count(message["id"])

            except Exception:
                pass

        # Leave the message visible for 8 seconds,
        # unless the handset is replaced first.
        if not interruptible_wait(8):
            reset_to_idle(phone)
            return

        new_state = phone.handle_event(Event.PLAYBACK_COMPLETE)

        reset_current_session(phone)
        drain_rotary_events()

        handle_state(new_state, phone)


def main():

    phone = StateMachine()

    # If the program starts while the handset is
    # already lifted, synchronize the software
    # state with the physical phone.
    if hardware.handset_is_lifted():

        reset_current_session(phone)

        new_state = phone.handle_event(Event.HOOK_LIFTED)

        handle_state(new_state, phone)

    try:

        while True:

            display.update()

            # -----------------------------
            # HOOK EVENTS
            # -----------------------------

            hook_event = hardware.get_hook_event()

            if hook_event == "HOOK_REPLACED":

                if phone.state != State.IDLE:
                    reset_to_idle(phone)

                time.sleep(0.01)
                continue

            elif hook_event == "HOOK_LIFTED":

                if phone.state == State.IDLE:

                    reset_current_session(phone)

                    new_state = phone.handle_event(Event.HOOK_LIFTED)

                    handle_state(new_state, phone)

            # -----------------------------
            # ROTARY EVENTS
            # -----------------------------

            rotary_event = hardware.get_rotary_event()

            if rotary_event == "ROTARY_TURNED":

                new_state = phone.handle_event(Event.ROTARY_TURNED)

                handle_state(new_state, phone)

            time.sleep(0.01)

    except KeyboardInterrupt:

        print("\nTelephone Network stopped.")

    finally:

        audio.stop_audio()

        hardware.rotary.close()
        hardware.hook.close()


if __name__ == "__main__":
    main()
