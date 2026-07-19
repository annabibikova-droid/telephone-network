from enum import Enum, auto
import display


class State(Enum):
    IDLE = auto()
    WAITING_FOR_DIAL = auto()
    RECORDING = auto()
    PROCESSING = auto()
    DISPLAYING_MESSAGE = auto()
    PLAYING = auto()


class Event(Enum):
    HOOK_LIFTED = auto()
    HOOK_REPLACED = auto()
    ROTARY_TURNED = auto()
    RECORDING_FINISHED = auto()
    SEARCH_COMPLETE = auto()
    PLAYBACK_COMPLETE = auto()


class StateMachine:

    def __init__(self):
        self.state = State.IDLE

        self.current_recording = None
        self.current_transcript = None
        self.matched_message = None

        display.show(self.state)

    def change_state(self, new_state):
        self.state = new_state
        display.show(self.state)
        return self.state

    def handle_event(self, event):

        match self.state:

            case State.IDLE:
                if event == Event.HOOK_LIFTED:
                    return self.change_state(State.WAITING_FOR_DIAL)

            case State.WAITING_FOR_DIAL:
                if event == Event.ROTARY_TURNED:
                    return self.change_state(State.RECORDING)

            case State.RECORDING:
                if event == Event.RECORDING_FINISHED:
                    return self.change_state(State.PROCESSING)

            case State.PROCESSING:
                if event == Event.SEARCH_COMPLETE:
                    return self.change_state(State.DISPLAYING_MESSAGE)

            case State.DISPLAYING_MESSAGE:
                if event == Event.PLAYBACK_COMPLETE:
                    return self.change_state(State.IDLE)

        return None
