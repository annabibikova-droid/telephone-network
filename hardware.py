from gpiozero import Button
from queue import SimpleQueue

# -----------------------------
# GPIO INPUTS
# -----------------------------

# Rotary dial off-normal contact
rotary = Button(
    17,
    pull_up=True,
    bounce_time=0.05,
)

# Hall sensor
# Magnet near = LOW = handset DOWN
# Magnet away = HIGH = handset LIFTED
hook = Button(
    22,
    pull_up=True,
    bounce_time=0.05,
)


# -----------------------------
# EVENT QUEUES
# -----------------------------

rotary_events = SimpleQueue()
hook_events = SimpleQueue()


def rotary_turned():
    rotary_events.put("ROTARY_TURNED")


def handset_down():
    hook_events.put("HOOK_REPLACED")


def handset_lifted():
    hook_events.put("HOOK_LIFTED")


rotary.when_pressed = rotary_turned

hook.when_pressed = handset_down
hook.when_released = handset_lifted


# -----------------------------
# FUNCTIONS USED BY MAIN.PY
# -----------------------------


def get_rotary_event():
    if rotary_events.empty():
        return None

    return rotary_events.get()


def get_hook_event():
    if hook_events.empty():
        return None

    return hook_events.get()


def handset_is_down():
    return hook.is_pressed


def handset_is_lifted():
    return not hook.is_pressed
