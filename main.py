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

        display.update()
        time.sleep(0.02)

    return True


def type_message_interruptibly(text, header=""):
    """Type on the LCD and terminal, retaining the location/date header."""

    prefix = f"{header}\n\n" if header else ""
    display.draw_text(prefix, show_cursor=True, blink_cursor=False)

    # Batch characters at the LCD refresh rate instead of rendering one
    # expensive CRT frame per character on the Pi Zero.
    start = time.monotonic()
    visible_count = 0
    character_delay = max(display.MESSAGE_SPEED, 0.011)

    while visible_count < len(text):
        if handset_replaced():
            return False

        next_count = min(
            len(text),
            max(1, int((time.monotonic() - start) / character_delay) + 1),
        )
        if next_count > visible_count:
            print(text[visible_count:next_count], end="", flush=True)
            visible_count = next_count
            display.draw_text(
                prefix + text[:visible_count],
                show_cursor=True,
                blink_cursor=False,
            )

        time.sleep(1 / display.MAX_REFRESH_RATE)

    print(flush=True)
    display.draw_text(prefix + text, show_cursor=True)
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
