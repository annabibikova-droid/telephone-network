import sounddevice as sd
import soundfile as sf
import os

SAMPLE_RATE = 44100
CHANNELS = 1
DURATION = 5


def get_next_audio_filename():
    """Return the next available recording filename."""

    folder = "recordings"

    files = os.listdir(folder)

    message_number = len(files) + 1

    filename = f"msg_{message_number:06d}.wav"

    return os.path.join(folder, filename)


def record_audio():
    """Record audio from the default microphone."""
    filename = get_next_audio_filename()

    print("🎤 Recording...")

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )

    sd.wait()

    sf.write(filename, recording, SAMPLE_RATE)

    print("✅ Recording saved!")
    return filename


def play_audio(filename):
    """Play an audio file."""

    print("🔊 Playing...")

    data, samplerate = sf.read(filename)

    sd.play(data, samplerate)

    sd.wait()

    print("Done.")
