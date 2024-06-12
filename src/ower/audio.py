import logging
import threading
import wave
from tkinter import Button, Tk

import config
import pyaudio
import requests

# import RPi.GPIO as GPIO
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "record.wav"


class Recorder:
    def __init__(self):
        self.frames = []
        self.is_recording = False

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        threading.Thread(target=self.record).start()

    def stop_recording(self):
        self.is_recording = False

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        logging.info("Recording started")
        while self.is_recording:
            data = stream.read(CHUNK)
            self.frames.append(data)
        logging.info("Recording stopped")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()


class Player:
    def __init__(self):
        pass


def create_gui():
    recorder = Recorder()
    root = Tk()
    root.title("Recorder")
    root.geometry("200x200")
    root.attributes("-alpha", 0.5)

    record_button = Button(root, text="Press and hold to record")
    record_button.pack(expand=True)

    def on_press(event):
        recorder.start_recording()

    def on_release(event):
        recorder.stop_recording()

    record_button.bind("<ButtonPress-1>", on_press)
    record_button.bind("<ButtonRelease-1>", on_release)

    root.mainloop()


if __name__ == "__main__":
    create_gui()

# def main():
#     audio = pyaudio.PyAudio()
#     stream = audio.open(
#         format=pyaudio.paInt16,
#         channels=1,
#         rate=16000,
#         input=True,
#         frames_per_buffer=1024,
#     )
#     frames = []
#     while True:
#         data = stream.read(1024)
#         frames.append(data)
#         if len(frames) >= 10:
#             break

#     stream.stop_stream()
#     stream.close()
#     with open("audio.wav", "wb") as f:
#         f.write(b"".join(frames))

#     # files = {"file": open("audio.wav", "rb")}
#     # response = requests.post(
#     #     "https://api.openai.com/v1/audio/transcriptions",
#     #     headers={"Authorization": f"Bearer {config.OPENAI_KEY}"},
#     #     files=files,
#     # )
#     # print(response.json()["text"])


# if __name__ == "__main__":
#     main()
