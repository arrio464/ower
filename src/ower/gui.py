# from tkinter import Button, Tk

# from audio import Player, Recorder


# class Gui:
#     def __init__(self):
#         self.recorder = Recorder()
#         self.player = Player()

#         self.root = Tk()
#         self.root.title("Recorder")
#         self.root.geometry("200x200")
#         self.root.attributes("-alpha", 0.5)

#         record_button = Button(self.root, text="Press and hold to record")
#         record_button.pack(expand=True)
#         record_button.bind("<ButtonPress-1>", self.on_press)
#         record_button.bind("<ButtonRelease-1>", self.on_release)

#     # def button_callback(channel):
#     #     if GPIO.input(12) == GPIO.LOW:
#     #         print("Pressed")
#     #     else:
#     #         print("Raised")

#     def run(self):
#         self.root.mainloop()

#     def on_press(self, event):
#         # self.recorder.start_recording()
#         print("Pressed")
#         self.root.attributes("-alpha", 0.8)

#     def on_release(self, event):
#         # self.recorder.stop_recording()
#         print("Released")
#         self.root.attributes("-alpha", 0.1)


# if __name__ == "__main__":
#     gui = Gui()
#     gui.run()


# import math
# import threading
# import time
# import tkinter as tk

# import cv2

# class VoiceAssistantApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("语音助手")
#         self.geometry("320x240")
#         self.configure(bg="")
#         # 创建悬浮的球
#         self.canvas = tk.Canvas(
#             self, width=320, height=120, bg="white", highlightthickness=0
#         )
#         self.canvas.pack()
#         self.ball = self.canvas.create_oval(140, 40, 180, 80, fill="black")
#         # 创建两个文字框
#         self.text_frame = tk.Frame(self, bg="white")
#         self.text_frame.pack(expand=True, fill=tk.BOTH)
#         self.text1 = tk.Label(
#             self.text_frame, text="语音助手", font=("Arial", 14), fg="black", bg="white"
#         )
#         self.text1.pack(pady=(10, 0))
#         self.text2 = tk.Label(
#             self.text_frame,
#             text="我能帮你什么？",
#             font=("Arial", 12),
#             fg="black",
#             bg="white",
#         )
#         self.text2.pack(pady=(5, 0))
#         # 创建波浪效果
#         self.wave_canvas = tk.Canvas(
#             self, width=320, height=60, bg="white", highlightthickness=0
#         )
#         self.wave_canvas.pack(side=tk.BOTTOM)
#         self.wave_points = [0] * 320
#         self.update_wave()
#     def update_wave(self):
#         self.wave_canvas.delete("wave")
#         for x in range(320):
#             y = 30 + 10 * math.sin((x + time.time() * 100) * 0.05)
#             self.wave_points[x] = y
#             self.wave_canvas.create_line(x, y, x, y + 1, fill="black", tag="wave")
#         self.after(50, self.update_wave)
import json
import logging
import queue
import re
import subprocess
import sys
import threading

import cv2
import pygame
import RPi.GPIO as GPIO
from cli import Cli
from enums import ClientEnum

logging.basicConfig(level=logging.INFO)


class Gui(Cli):
    def __init__(self):
        super().__init__()
        GPIO.setmode(GPIO.BCM)  # 设置GPIO 12为输入，并启用内部上拉电阻
        GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            12, GPIO.BOTH, callback=self.button_callback, bouncetime=50
        )
        pygame.init()
        self.size = (900, 610)
        self.screen = pygame.display.set_mode(
            self.size, pygame.RESIZABLE | pygame.NOFRAME
        )
        self.running = True
        self.clock = pygame.time.Clock()

        self.cap_ball = cv2.VideoCapture("assets/idle_anim.mp4")
        self.cap_wave = cv2.VideoCapture("assets/listening_anim.mp4")

        pygame.font.init()
        # self.font = pygame.font.Font(None, 36)
        # self.font = pygame.font.Font("C:\Windows\Fonts\Arial.ttf", 24)
        self.font = pygame.font.SysFont("wenquanyimicrohei", 36)
        self.max_width = self.size[0] - 20  # 最大宽度为窗口宽度减去左右边距

    def pause_music(self):
        fuo_msg = {
            "type": None,
            "name": None,
            "state": "0",
        }
        self.queues[ClientEnum.FUO].put(fuo_msg)
        logging.info("Pausing music...")

    def resume_music(self):
        fuo_msg = {
            "type": None,
            "name": None,
            "state": "1",
        }
        self.queues[ClientEnum.FUO].put(fuo_msg)
        logging.info("Resuming music...")

    def button_callback(self, channel):
        if GPIO.input(12) == GPIO.LOW:
            logging.info("Key pressed")
            self.pause_music()

            super().start_recording()
            self.set_text1("        我能帮你什么？        ")
            self.set_text2("")
            self.set_topmost()
        else:
            logging.info("Key raised")
            super().stop_recording()
            user = super()._stt()
            self.set_text1(user)
            llm = super().talk(user)
            self.set_text2(llm)
            super().say(llm)
            self.hide()
            self.resume_music()

    def split_text(self, text, font, max_width):
        words = re.split("([ ,.，。：；*])", text)
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            if word == "":
                continue
            word_width, word_height = font.size(word)

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append("".join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append("".join(current_line))

        return lines

    def set_text1(self, text):
        self.text1 = text
        self.text1_lines = self.split_text(text, self.font, self.max_width)

    def set_text2(self, text):
        self.text2 = text
        self.text2_lines = self.split_text(text, self.font, self.max_width)

    def set_topmost(self):
        if sys.platform == "win32":
            hwnd = pygame.display.get_wm_info()["window"]
            import ctypes

            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        elif sys.platform == "linux":
            window_id = pygame.display.get_wm_info()["window"]
            subprocess.run(["xdotool", "windowraise", str(window_id)])
            subprocess.run(["xdotool", "windowactivate", str(window_id)])

    def hide(self):
        pygame.display.iconify()

    def quit(self):
        self.running = False

    def run(self, queue, event):
        self.queues = queue
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            ret_ball, frame_ball = self.cap_ball.read()
            ret_wave, frame_wave = self.cap_wave.read()

            if not ret_ball:
                self.cap_ball.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_ball, frame_ball = self.cap_ball.read()

            if not ret_wave:
                self.cap_wave.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret_wave, frame_wave = self.cap_wave.read()

            frame_ball = cv2.cvtColor(frame_ball, cv2.COLOR_BGR2RGB)
            frame_wave = cv2.cvtColor(frame_wave, cv2.COLOR_BGR2RGB)

            frame_surface_ball = pygame.surfarray.make_surface(frame_ball)
            frame_surface_ball = pygame.transform.rotate(frame_surface_ball, -90)
            frame_surface_wave = pygame.surfarray.make_surface(frame_wave)
            frame_surface_wave = pygame.transform.rotate(frame_surface_wave, -90)

            background = pygame.Surface(self.size)
            background.set_alpha(128)
            background.fill((0, 0, 0))

            self.screen.blit(background, (0, 0))
            self.screen.blit(
                frame_surface_ball,
                (
                    450 - frame_surface_ball.get_width() / 2,
                    0
                    - frame_surface_ball.get_height() / 2
                    + 80,  # 80 is a little offset
                ),
            )
            self.screen.blit(
                frame_surface_wave,
                (
                    450 - frame_surface_wave.get_width() / 2,
                    610 - frame_surface_wave.get_height(),
                ),
            )

            y_offset = 150
            for line in self.text1_lines:
                line_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(line_surface, (5, y_offset))
                y_offset += self.font.get_linesize()

            y_offset = 350
            for line in self.text2_lines:
                line_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(line_surface, (5, y_offset))
                y_offset += self.font.get_linesize()

            pygame.display.flip()
            self.clock.tick(30)

        self.cap_ball.release()
        self.cap_wave.release()
        pygame.quit()


if __name__ == "__main__":
    queues = [queue.Queue() for _ in range(ClientEnum.__len__())]
    events = [threading.Event() for _ in range(ClientEnum.__len__())]
    gui = Gui()

    gui.set_text1(
        "老子曰：「至治之極，鄰國相望，雞狗之聲相聞，民各甘其食，美其服，安其俗，樂其業，至老死，不相往來。」"
    )
    gui.set_text2(
        "太史公曰：夫神農以前，吾不知已。至若詩書所述虞夏以來，耳目欲極聲色之好，口欲窮芻豢之味，身安逸樂，而心誇矜輓能之榮使。"
    )
    gui.run(queues, events)
    gui.set_topmost()
