from gpiozero import Button
from signal import pause

hall = Button(27, pull_up=True, bounce_time=0.05)


def handset_down():
    print("HANDSET DOWN — on hook", flush=True)


def handset_lifted():
    print("HANDSET LIFTED — off hook", flush=True)


hall.when_pressed = handset_down
hall.when_released = handset_lifted

print("Hall sensor test running.", flush=True)
print("Move the handset/magnet toward and away from the sensor.", flush=True)
print("Press Ctrl+C to stop.", flush=True)
print()

if hall.is_pressed:
    print("Starting state: HANDSET DOWN — on hook", flush=True)
else:
    print("Starting state: HANDSET LIFTED — off hook", flush=True)

pause()
