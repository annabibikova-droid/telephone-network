from gpiozero import Button
from signal import pause

rotary = Button(17, pull_up=True, bounce_time=0.05)

rotary.when_pressed = lambda: print("CLOSED — rotary turned!", flush=True)
rotary.when_released = lambda: print("OPEN — rotary returned!", flush=True)

print("Rotary test running. Turn the dial. Press Ctrl+C to stop.", flush=True)

pause()
