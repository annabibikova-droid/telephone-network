import os
import re
import time

import keyboard
import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_DURATION = 0.1


def get_next_audio_filename():
    """Return the next available recording filename."""

    folder = "recordings"
    os.makedirs(folder, exist_ok=True)

    message_numbers = []

    for filename in os.listdir(folder):
        match = re.fullmatch(r"msg_(\d{6})\.wav", filename)

        if match:
            message_numbers.append(int(match.group(1)))

    if message_numbers:
        next_number = max(message_numbers) + 1
    else:
        next_number = 1

    filename = f"msg_{next_number:06d}.wav"

    return os.path.join(folder, filename)


def record_audio(max_duration=10, progress_callback=None):
    """
    Record audio until either:

    - max_duration seconds pass, or
    - the user presses R.

    Returns the saved audio filename.
    """

    filename = get_next_audio_filename()

    chunk_frames = int(CHUNK_DURATION * SAMPLE_RATE)
    recorded_chunks = []

    start_time = time.time()
    last_remaining = None

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    ) as stream:

        while True:
            elapsed = time.time() - start_time

            if elapsed >= max_duration:
                break

            # Stop recording early when the rotary is turned again.
            if keyboard.is_pressed("r"):

                while keyboard.is_pressed("r"):
                    time.sleep(0.01)

                break

            remaining = max_duration - int(elapsed)

            if remaining != last_remaining:
                last_remaining = remaining

                if progress_callback is not None:
                    progress_callback(remaining)

            audio_chunk, overflowed = stream.read(chunk_frames)

            if overflowed:
                print("Audio input overflow occurred.")

            recorded_chunks.append(audio_chunk.copy())

    if not recorded_chunks:
        raise RuntimeError("No audio was recorded.")

    recording = np.concatenate(recorded_chunks, axis=0)

    sf.write(filename, recording, SAMPLE_RATE)

    return filename


def play_audio(filename):
    """Play an audio file."""

    data, samplerate = sf.read(filename)

    sd.play(data, samplerate)
    sd.wait()
