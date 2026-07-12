from speech import transcribe_audio

text = transcribe_audio("audio/test.wav")

print()
print("Transcript:")
print(text)
