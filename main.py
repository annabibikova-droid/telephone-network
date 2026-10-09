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
        completed_typing = type_message_interruptibly(message["text"], header=message_header)

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

                display.update()
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