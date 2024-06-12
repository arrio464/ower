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
import re
import sys

import cv2
import pygame


class Gui:
    def __init__(self):
        pygame.init()
        self.size = (480, 320)
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
        self.font = pygame.font.SysFont("SimHei", 20)
        self.text1 = ""
        self.text2 = ""
        self.max_width = self.size[0] - 20  # 最大宽度为窗口宽度减去左右边距

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

    def hide(self):
        pygame.display.iconify()

    def quit(self):
        self.running = False

    def run(self):
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
                    240 - frame_surface_ball.get_width() / 2,
                    0
                    - frame_surface_ball.get_height() / 2
                    + 80,  # 80 is a little offset
                ),
            )
            self.screen.blit(
                frame_surface_wave,
                (
                    240 - frame_surface_wave.get_width() / 2,
                    320 - frame_surface_wave.get_height(),
                ),
            )

            y_offset = 150
            for line in self.text1_lines:
                line_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(line_surface, (5, y_offset))
                y_offset += self.font.get_linesize()

            y_offset = 200
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
    gui = Gui()
    gui.set_topmost()
    gui.set_text1(
        "老子曰：「至治之極，鄰國相望，雞狗之聲相聞，民各甘其食，美其服，安其俗，樂其業，至老死，不相往來。」"
    )
    gui.set_text2(
        "太史公曰：夫神農以前，吾不知已。至若詩書所述虞夏以來，耳目欲極聲色之好，口欲窮芻豢之味，身安逸樂，而心誇矜輓能之榮使。"
    )
    gui.run()

# def main():
#     pygame.init()
#     size = (480, 320)
#     screen = pygame.display.set_mode(size, pygame.RESIZABLE)
#     pygame.display.set_caption("Pygame Video with Transparent Background")

#     cap_ball = cv2.VideoCapture("assets/idle_anim.mp4")
#     cap_wave = cv2.VideoCapture("assets/listening_anim.mp4")
#     clock = pygame.time.Clock()
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#         ret, frame_ball = cap_ball.read()
#         ret, frame_wave = cap_wave.read()
#         if not ret:
#             break
#         # 将视频帧从 BGR 转换为 RGB
#         frame_ball = cv2.cvtColor(frame_ball, cv2.COLOR_BGR2RGB)
#         frame_wave = cv2.cvtColor(frame_wave, cv2.COLOR_BGR2RGB)
#         # 将帧数据转换为 Pygame 表面
#         frame_surface = pygame.surfarray.make_surface(frame_ball)
#         frame_surface = pygame.transform.rotate(
#             frame_surface, -90
#         )  # 旋转 90 度适应窗口
#         # 创建半透明的背景
#         background = pygame.Surface(size)
#         background.set_alpha(128)  # 128 代表 50% 透明度
#         background.fill((0, 0, 0))  # 黑色背景
#         # 绘制背景和视频帧
#         screen.blit(background, (144, 0))
#         screen.blit(frame_surface, (0, 0))
#         pygame.display.flip()
#         clock.tick(30)  # 设置帧率
#     cap_ball.release()
#     pygame.quit()


# if __name__ == "__main__":
#     main()


# if __name__ == "__main__":
# app = VoiceAssistantApp()
# app.mainloop()
