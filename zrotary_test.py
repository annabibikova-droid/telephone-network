from gpiozero import Button
from signal import pause

rotary = Button(17, pull_up=True)

rotary.when_pressed = lambda: print("Rotary turned!")

pause()
