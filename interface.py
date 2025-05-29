import cv2
import pygame
import sys
import numpy as np
import time
import math
import random
from pygame import gfxdraw
import os
import subprocess

pygame.init()
pygame.mixer.init()

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Get the Python executable path
python_exe = sys.executable

window_width, window_height = 1000, 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Cryptography Game")

# Use os.path.join to create the correct path to the audio file
audio_path = os.path.join(script_dir, "mixkit-futuristic-sci-fi-computer-ambience-2507.wav")
pygame.mixer.music.load(audio_path)
pygame.mixer.music.play(-1)

# Update the video path as well
video_path = os.path.join(script_dir, "6915809_Motion Graphics_Motion Graphic_3840x2160.mov.crdownload")
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Cannot open video file.")
    sys.exit()

fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
clock = pygame.time.Clock()

# Update the image path
key_img_path = os.path.join(script_dir, "lock.png")
key_img = pygame.image.load(key_img_path).convert_alpha()
key_img = pygame.transform.scale(key_img, (200, 180))
key_rect = key_img.get_rect(center=(window_width // 2, window_height // 2))


def tint_image(image, tint_color):
    tinted = image.copy()
    tint_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
    tint_surface.fill(tint_color)
    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


key_img_tinted = tint_image(key_img, (0, 255, 0, 120))

title_font = pygame.font.SysFont("consolas", 64, bold=True)
quote_font = pygame.font.SysFont("segoeuiitalic", 26, bold=False)

WHITE = (255, 255, 255)
CYBER_BLUE = (0, 255, 255)
SOFT_CYAN = (100, 255, 255)
DARK_TRANSPARENT = (0, 0, 0, 180)
SOFT_GREEN = (100, 255, 180)
IVORY = (245, 235, 220)

full_quote = " Click the lock to begin your magical journey...."
typed_quote = ""
quote_start_time = time.time()
letter_delay = 0.05


def draw_soft_glow_text(text, font, x, y, glow_color, main_color, surface):
    for offset in range(1, 4):
        glow = font.render(text, True, glow_color)
        glow.set_alpha(30)
        surface.blit(glow, (x - offset, y - offset))
        surface.blit(glow, (x + offset, y - offset))
        surface.blit(glow, (x - offset, y + offset))
        surface.blit(glow, (x + offset, y + offset))
    main = font.render(text, True, main_color)
    surface.blit(main, (x, y))


def main_menu():
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BRONZE = (205, 127, 50)
    DARK_BLUE = (5, 10, 20)
    LOCK_COLOR = (50, 150, 255)
    GLOW_COLOR = (100, 200, 255)

    title_font = pygame.font.Font(None, 80)
    button_font = pygame.font.Font(None, 28)
    small_font = pygame.font.Font(None, 24)
    matrix_font = pygame.font.Font(None, 20)

    clock = pygame.time.Clock()
    FPS = 60

    algorithms = [
        {"name": "Hill Cipher"},
        {"name": "Feistel Cipher"},
        {"name": "RSA Algorithm"},
        {"name": "Elliptic-Curve"},
        {"name": "Rail Fence Cipher"},
        {"name": "SHA-256"},
    ]

    class MatrixStream:
        def __init__(self, x, window_height, font, char_set, color_start, color_end):
            self.x = x
            self.y = random.randint(-window_height, 0)
            self.length = random.randint(5, 15)
            self.speed = random.uniform(2, 6)
            self.font = font
            self.char_set = char_set
            self.characters = [random.choice(self.char_set) for _ in range(self.length)]
            self.color_start = color_start
            self.color_end = color_end
            self.char_height = self.font.get_height()

        def update(self):
            self.y += self.speed
            if self.y > window_height + self.length * self.char_height:
                self.y = random.randint(-window_height, 0)
                self.speed = random.uniform(2, 6)
                self.characters = [random.choice(self.char_set) for _ in range(self.length)]

        def draw(self, surface):
            for i, char in enumerate(self.characters):
                alpha = int(255 * (1 - i / self.length))
                alpha = max(0, alpha)
                color = (
                    int(self.color_start[0] + (self.color_end[0] - self.color_start[0]) * (i / self.length)),
                    int(self.color_start[1] + (self.color_end[1] - self.color_start[1]) * (i / self.length)),
                    int(self.color_start[2] + (self.color_end[2] - self.color_start[2]) * (i / self.length)),
                )
                char_surface = self.font.render(char, True, (*color, alpha))
                surface.blit(char_surface, (self.x, self.y - i * self.char_height))

    matrix_streams = []
    matrix_char_set = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()-_+="
    char_spacing = matrix_font.size("W")[0] + 2

    for x in range(0, window_width, char_spacing):
        matrix_streams.append(MatrixStream(x, window_height, matrix_font, matrix_char_set, GLOW_COLOR, DARK_BLUE))

    global_time = 0

    def draw_cyber_background():
        nonlocal global_time
        screen.fill(DARK_BLUE)
        global_time += 0.02

        for stream in matrix_streams:
            stream.update()
            stream.draw(screen)

        center_x, center_y = window_width // 2, window_height // 2
        max_radius = min(window_width, window_height) // 4
        pulse_ratio = 0.8 + 0.2 * math.sin(global_time * 0.8)
        current_radius = int(max_radius * pulse_ratio)

        for i in range(5):
            alpha_val = max(0, int(20 - i * 4))
            current_layer_radius = int(current_radius * (1 + i * 0.1))
            s = pygame.Surface((current_layer_radius * 2, current_layer_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*GLOW_COLOR, alpha_val), (current_layer_radius, current_layer_radius),
                               current_layer_radius)
            screen.blit(s, (center_x - current_layer_radius, center_y - current_layer_radius))

        for i in range(15):
            angle = global_time * 0.5 + i * (2 * math.pi / 15)
            radius_offset = 100 + 50 * math.sin(global_time * 0.3 + i)
            text_x = center_x + current_radius * 1.5 * math.cos(angle) + radius_offset * math.cos(angle)
            text_y = center_y + current_radius * 1.5 * math.sin(angle) + radius_offset * math.sin(angle)

            binary_text = "".join(random.choice("01") for _ in range(random.randint(5, 10)))
            alpha_text = max(0, int(100 + 50 * math.sin(global_time * 1.5 + i * 0.5)))
            text_surface = small_font.render(binary_text, True, (*GLOW_COLOR, alpha_text))
            text_surface.set_alpha(alpha_text)
            screen.blit(text_surface, (text_x - text_surface.get_width() // 2, text_y - text_surface.get_height() // 2))

    def draw_button(x, y, width, height, text, hover=False):
        glow_strength = 80 if hover else 30
        glow_size = 10 if hover else 5
        s = pygame.Surface((width + glow_size * 2, height + glow_size * 2), pygame.SRCALPHA)
        pygame.draw.rect(s, (*GLOW_COLOR, glow_strength), (0, 0, width + glow_size * 2, height + glow_size * 2),
                         border_radius=15)
        screen.blit(s, (x - glow_size, y - glow_size))

        s = pygame.Surface((width, height), pygame.SRCALPHA)
        s.fill((*DARK_BLUE, 200))
        pygame.draw.rect(s, GLOW_COLOR, (0, 0, width, height), 2, border_radius=12)
        screen.blit(s, (x, y))

        text_surface = button_font.render(text, True, (255, 255, 255))
        screen.blit(text_surface, (x + (width - text_surface.get_width()) // 2,
                                   y + (height - text_surface.get_height()) // 2))

    def launch_algorithm(name):
        if name == "RSA Algorithm":
            # Close pygame window
            pygame.quit()
            # Launch python project.py
            script_path = os.path.join(script_dir, "python project.py")
            subprocess.Popen([python_exe, script_path])
            sys.exit()
        elif name == "SHA-256":
            # Close pygame window
            pygame.quit()
            # Launch Game.py
            script_path = os.path.join(script_dir, "Game.py")
            subprocess.Popen([python_exe, script_path])
            sys.exit()
        elif name == "Hill Cipher":
            # Close pygame window
            pygame.quit()
            # Launch hillciphertest.py
            script_path = os.path.join(script_dir, "hillciphertest.py")
            subprocess.Popen([python_exe, script_path])
            sys.exit()
        else:
            # For other algorithms, show the loading animation
            for i in range(0, 100, 2):
                screen.fill(DARK_BLUE)
                draw_cyber_background()

                size = 50
                font = pygame.font.Font(None, size)
                text = font.render(f"Launching {name}...", True, (255, 255, 255))
                text_x = (window_width - text.get_width()) // 2
                text_y = (window_height - text.get_height()) // 2 - 20
                screen.blit(text, (text_x, text_y))

                loading_font = pygame.font.Font(None, 24)
                loading_text = loading_font.render("Loading...", True, (200, 200, 200))
                loading_x = (window_width - loading_text.get_width()) // 2
                loading_y = text_y + text.get_height() + 10
                screen.blit(loading_text, (loading_x, loading_y))

                pygame.draw.rect(screen, (20, 50, 80),
                                 (window_width // 4, window_height // 2 + 70, window_width // 2, 20),
                                 border_radius=10)
                pygame.draw.rect(screen, GLOW_COLOR,
                                 (window_width // 4, window_height // 2 + 70, window_width // 2 * i / 100, 20),
                                 border_radius=10)

                pygame.display.flip()
                pygame.time.delay(20)

    running = True
    while running:
        draw_cyber_background()

        title_text = "Choose an Algorithm"
        title_surface = title_font.render(title_text, True, WHITE)
        screen.blit(title_surface, ((window_width - title_surface.get_width()) // 2, 40))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_clicked = True

        button_width, button_height = 230, 45
        margin = 25
        start_y = 150
        for idx, algo in enumerate(algorithms):
            x = (window_width - button_width) // 2
            y = start_y + idx * (button_height + margin)
            hover = pygame.Rect(x, y, button_width, button_height).collidepoint(mouse_pos)

            draw_button(x, y, button_width, button_height, algo["name"], hover)

            if hover and mouse_clicked:
                launch_algorithm(algo["name"])

        pygame.display.update()
        clock.tick(FPS)


def launch_game():
    main_menu()


clicked = False
while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame = cv2.resize(frame, (window_width, window_height))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = np.rot90(frame)
    frame_surface = pygame.surfarray.make_surface(frame)
    screen.blit(frame_surface, (0, 0))

    overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay.fill(DARK_TRANSPARENT)
    screen.blit(overlay, (0, 0))

    draw_soft_glow_text("Cryptonia", title_font, (window_width - 400) // 2, 50, SOFT_CYAN, WHITE, screen)

    if clicked:
        screen.blit(key_img_tinted, key_rect)
    else:
        screen.blit(key_img, key_rect)

    elapsed = time.time() - quote_start_time
    num_chars = min(len(full_quote), int(elapsed / letter_delay))
    typed_quote = full_quote[:num_chars]

    quote_surface = quote_font.render(typed_quote, True, WHITE)
    quote_x = (window_width - quote_surface.get_width()) // 2
    quote_y = key_rect.bottom + 20
    draw_soft_glow_text(typed_quote, quote_font, quote_x, quote_y, SOFT_GREEN, IVORY, screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            cap.release()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if key_rect.collidepoint(pygame.mouse.get_pos()) and not clicked:
                clicked = True
                pygame.display.update()
                pygame.time.wait(500)
                launch_game()

    pygame.display.update()
    clock.tick(fps)