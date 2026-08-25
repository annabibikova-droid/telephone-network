import os
import re
import time
import threading

import numpy as np
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_DURATION = 0.1


def play_beep(frequency=800, duration=0.6, volume=0.3):
    """Play a short tone indicating that recording is about to begin."""

    sample_count = int(SAMPLE_RATE * duration)
    times = np.arange(sample_count) / SAMPLE_RATE

    tone = volume * np.sin(2 * np.pi * frequency * times)

    fade_samples = min(int(SAMPLE_RATE * 0.01), sample_count // 2)

    if fade_samples > 0:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)

        tone[:fade_samples] *= fade_in
        tone[-fade_samples:] *= fade_out

    sd.play(tone.astype(np.float32), SAMPLE_RATE)
    sd.wait()


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


def record_audio(
    max_duration=20,
    progress_callback=None,
    stop_callback=None,
):
    """
    Record audio until either:

    - max_duration seconds pass, or
    - stop_callback returns True.

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

            if stop_callback is not None and stop_callback():
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


def play_audio_async(filename):
    """Play an audio file in the background."""

    thread = threading.Thread(
        target=play_audio,
        args=(filename,),
        daemon=True,
    )

    thread.start()

    return thread


def stop_audio():
    """Immediately stop any current sounddevice playback."""

    sd.stop()
