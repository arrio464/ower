import logging
from io import BytesIO
from tkinter import Button, Tk

import config
import pygame
from audio import WAVE_OUTPUT_FILENAME, Player, Recorder
from gtts import gTTS
from openai import OpenAI

logging.basicConfig(level=logging.INFO)


class Cli(Recorder, Player):
    def __init__(self):
        super().__init__()
        pygame.init()
        self.client = OpenAI(base_url=config.OPENAI_BASE_URL, api_key=config.OPENAI_KEY)
        # TODO: bind key

    def _play_stream(self, stream):
        stream.seek(0)
        pygame.mixer.music.load(stream)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(1)

    def say(self, text, chunk_size=100):
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            tts = gTTS(text=chunk, lang="zh")
            fp = BytesIO()
            tts.write_to_fp(fp)
            self._play_stream(fp)

    def listen(self):
        pass
        # TODO: streaming listen

    def _stt(self):
        audio_file = open(WAVE_OUTPUT_FILENAME, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
        logging.info(f"Transcription result: {transcription.text}")
        return transcription.text

    def talk(self, text):
        if not text:
            text = self._stt()
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个智能助手，你的任务是陪用户进行聊天",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
        )
        logging.info(f"LLM's response: {completion.choices[0].message}")
        return completion.choices[0].message.content


def test():
    cli = Cli()
    root = Tk()
    root.title("Recorder")
    root.geometry("200x200")
    root.attributes("-alpha", 0.5)

    record_button = Button(root, text="Press and hold to record")
    record_button.pack(expand=True)

    def on_press(event):
        cli.start_recording()

    def on_release(event):
        cli.stop_recording()
        # recorder._stt()
        cli.talk()

    record_button.bind("<ButtonPress-1>", on_press)
    record_button.bind("<ButtonRelease-1>", on_release)

    root.mainloop()


text = """计算机科学与技术主要涉及计算机系统的设计、开发、实现和应用。其主要内容包括计算机基础知识、算法与数据结构、程序设计与开发、计算机网络、数据库 系统、操作系统、人工智能、机器学习、软件工程、并行与分布式计算、计算机安全等领域。这些内容涵盖了计 算机科学与技术的基础理论、技术应用以及发展趋势等方面。计算机科学与技术是一个广泛且不断发展的领域，涉及到众多领域的知识和技术。"""


if __name__ == "__main__":
    # cli = Cli()
    # cli.say(text)
    test()
