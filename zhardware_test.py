import hardware
import time

print("Telephone hardware test running.")
print()
print("Lift/replace the handset and turn the rotary dial.")
print("Press Ctrl+C to stop.")
print()

if hardware.handset_is_down():
    print("Starting state: HANDSET DOWN")
else:
    print("Starting state: HANDSET LIFTED")


while True:

    hook_event = hardware.get_hook_event()

    if hook_event == "HOOK_LIFTED":
        print("HANDSET LIFTED")

    elif hook_event == "HOOK_REPLACED":
        print("HANDSET DOWN")

    rotary_event = hardware.get_rotary_event()

    if rotary_event == "ROTARY_TURNED":
        print("ROTARY TURNED")

    time.sleep(0.01)
