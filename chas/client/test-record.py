# A Simple script that will record and play back sound, while saving it to a wav file

import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
FILENAME = 'output.wav'

p = pyaudio.PyAudio()

print("Sound devices:")

for i in range(p.get_device_count()):

    print(f"[{i}] {p.get_device_info_by_index(i)}")

print(f"Default Output device: {p.get_default_output_device_info()}")
print(f"Default Input device: {p.get_default_input_device_info()}")

out = int(input("Choose a Output Device:"))
inp = int(input("Choose a Input device:"))

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input_device_index=inp,
                output_device_index=out,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

print("Recording...")

frames = []

for i in range(0, int(RATE/CHUNK * RECORD_SECONDS)):

    # Recording audio data to buffer

    data = stream.read(CHUNK)
    frames.append(data)

print("Done recording!")

print("Replaying audio...")

pos = 0

while pos <= len(frames):

    # Writing audio to stream

    data = frames[pos:pos+CHUNK]
    stream.write(b''.join(data))

    pos = pos+CHUNK

stream.stop_stream()
stream.close()

print(f"Saving wave file '{FILENAME}' ...")

wf = wave.open(FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()

print("Wave file saved!")
