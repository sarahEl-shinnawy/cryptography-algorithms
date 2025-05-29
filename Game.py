import pygame
import sys
import hashlib
import numpy as np
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHA-256 Hangman")

DARK_BLUE1 = (5, 10, 30)
DARK_BLUE2 = (15, 30, 80)
CYBER_BLUE = (0, 255, 255)
CYBER_BLUE_LIGHT = (50, 255, 255)
CYBER_BLUE_DARK = (0, 150, 150)
WHITE = (230, 240, 255)
PURE_WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 120, 150)
ACTIVE_BLUE = (0, 150, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
NEON_GREEN = (57, 255, 20)

title_font = pygame.font.SysFont("arial", 48, bold=True)
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 24)
hash_font = pygame.font.SysFont("arial", 18)
info_font = pygame.font.SysFont("arial", 20)

START_SCREEN = 0
SHA_DESCRIPTION_SCREEN = 1
HOW_TO_PLAY_SCREEN = 2
GAME_SCREEN = 3
RESULT_SCREEN = 4
current_screen = START_SCREEN

current_hash = ""
correct_text = ""
guessed_letters = []
wrong_guesses = 0
max_wrong_guesses = 10
game_result = ""
feedback = ""
feedback_timer = 0
feedback_duration = 2

hangman_parts = [
    ((700, 200), (700, 400)),
    ((700, 200), (800, 200)),
    ((800, 200), (800, 250)),
    ((800, 280), 30),
    ((800, 310), (800, 380)),
    ((800, 330), (770, 350)),
    ((800, 330), (830, 350)),
    ((800, 380), (770, 420)),
    ((800, 380), (830, 420))
]

class Particle:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.alpha = random.randint(50, 200)

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.alpha -= 1
        if self.alpha <= 0:
            self.__init__()
            self.alpha = random.randint(150, 255)
            self.x = random.randint(0, WIDTH)
            self.y = random.randint(0, HEIGHT)

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*CYBER_BLUE, self.alpha))
        surface.blit(s, (self.x, self.y))

particles = [Particle() for _ in range(50)]

def load_words(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        return ["apple", "banana", "cherry", "date", "elderberry", "quantum", "firewall", "encryption", "algorithm", "cyberspace"]

texts = load_words("words.txt")

def draw_gradient(surface, color1, color2):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def generate_question():
    global current_hash, correct_text, guessed_letters, wrong_guesses, feedback_timer
    correct_text = random.choice(texts)
    current_hash = hashlib.sha256(correct_text.encode('utf-8')).hexdigest()
    guessed_letters = []
    wrong_guesses = 0
    feedback_timer = 0
    return current_hash

def draw_cyber_button(rect, text, is_hovered=False):
    button_color = PURE_WHITE
    border_color = GRAY
    text_color = BLACK

    if is_hovered:
        button_color = ACTIVE_BLUE
        border_color = CYBER_BLUE
        text_color = WHITE

    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)
    
    text_surf = small_font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def draw_text_with_glow(surface, text, font, color, pos, glow_color, glow_radius=2):
    for x_offset in range(-glow_radius, glow_radius + 1):
        for y_offset in range(-glow_radius, glow_radius + 1):
            if x_offset == 0 and y_offset == 0:
                continue
            text_surf_glow = font.render(text, True, glow_color)
            surface.blit(text_surf_glow, (pos[0] + x_offset, pos[1] + y_offset))
    text_surf = font.render(text, True, color)
    surface.blit(text_surf, pos)

def draw_start_screen():
    title_text = "SHA-256 Hangman"
    title_surface = title_font.render(title_text, True, WHITE)
    draw_text_with_glow(screen, title_text, title_font, WHITE, (WIDTH//2 - title_surface.get_width()//2, 130), BLACK)
    
    subtitle = font.render("Guess the word from its SHA-256 hash", True, WHITE)
    screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 190))
    
    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(start_button, "START", start_button.collidepoint(mouse_pos))
    draw_cyber_button(exit_button, "EXIT", exit_button.collidepoint(mouse_pos))
    
    footer = small_font.render(f"Wrong guesses allowed: {max_wrong_guesses}", True, GRAY)
    screen.blit(footer, (WIDTH//2 - footer.get_width()//2, 460))

def draw_sha_description_screen():
    title_text = "What is SHA-256?"
    title_surface = title_font.render(title_text, True, WHITE)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 70)) # Adjusted Y position

    description_text_lines = [
        "SHA-256 stands for Secure Hash Algorithm 256-bit.",
        "It's a cryptographic hash function widely used for security.",
        "Think of it as a unique digital fingerprint for data.",
        "",
        "No matter the size of the input (a word, a file, etc.),",
        "SHA-256 always produces a fixed-size output:",
        "a 256-bit (64 character hexadecimal) hash value.",
        "",
        "Even a tiny change in the input will result in a completely",
        "different hash, making it extremely secure for verifying",
        "data integrity. It's almost impossible to reverse-engineer",
        "the original data from its hash alone.",
        "This is why guessing the word is a challenge!"
    ]
    
    y_offset = 140 # Adjusted Y position
    for line in description_text_lines:
        line_surf = small_font.render(line, True, WHITE)
        screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y_offset))
        y_offset += 25
    
    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(next_button_sha, "NEXT", next_button_sha.collidepoint(mouse_pos))
    draw_cyber_button(back_button_sha, "BACK", back_button_sha.collidepoint(mouse_pos))

def draw_how_to_play_screen():
    description_title = title_font.render("How to Play", True, WHITE)
    screen.blit(description_title, (WIDTH // 2 - description_title.get_width() // 2, 70)) # Adjusted Y position

    description_text_lines = [
        "Welcome to SHA-256 Hangman!",
        "",
        "In this game, your goal is to guess a hidden word.",
        "You'll be given its SHA-256 hash.",
        "",
        "Type letters to guess. Each incorrect guess will add a part",
        "to the hangman. You have a limited number of wrong guesses",
        "before the game is over. If you guess the word correctly,",
        "you win! Good luck!"
    ]
    
    y_offset = 180 # Adjusted Y position
    for line in description_text_lines:
        line_surf = small_font.render(line, True, WHITE)
        screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y_offset))
        y_offset += 30

    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(continue_button_how_to_play, "CONTINUE", continue_button_how_to_play.collidepoint(mouse_pos))
    draw_cyber_button(back_button_how_to_play, "BACK", back_button_how_to_play.collidepoint(mouse_pos))

def draw_game_screen():
    hash_title = small_font.render("SHA-256 Hash:", True, WHITE)
    screen.blit(hash_title, (50, 100))
    
    y_offset = 130
    chunk_size = 32
    for i in range(0, len(current_hash), chunk_size):
        chunk = current_hash[i:i+chunk_size]
        hash_surf = hash_font.render(chunk, True, WHITE)
        screen.blit(hash_surf, (50, y_offset))
        y_offset += 25
    
    display_word = ""
    for letter in correct_text:
        if letter in guessed_letters:
            display_word += letter.upper() + " "
        else:
            display_word += "_ "
    
    word_surf = font.render(display_word, True, WHITE)
    screen.blit(word_surf, (50, 300))
    
    for i in range(wrong_guesses):
        if i < len(hangman_parts):
            part = hangman_parts[i]
            if isinstance(part[0], tuple) and isinstance(part[1], tuple):
                pygame.draw.line(screen, WHITE, part[0], part[1], 3)
            else:
                pygame.draw.circle(screen, WHITE, part[0], part[1], 3)
    
    keyboard_layout = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    y_pos = 400
    mouse_pos = pygame.mouse.get_pos()
    for row in keyboard_layout:
        x_pos = 50
        for letter in row:
            rect = pygame.Rect(x_pos, y_pos, 40, 40)
            
            bg_color = PURE_WHITE
            text_color = BLACK

            if letter in guessed_letters:
                if letter in correct_text:
                    bg_color = GREEN
                    text_color = WHITE
                else:
                    bg_color = RED
                    text_color = WHITE
            elif rect.collidepoint(mouse_pos):
                bg_color = ACTIVE_BLUE
                text_color = WHITE
            
            pygame.draw.rect(screen, bg_color, rect, border_radius=5)
            pygame.draw.rect(screen, GRAY, rect, 2, border_radius=5)

            letter_surf = small_font.render(letter.upper(), True, text_color)
            letter_rect = letter_surf.get_rect(center=rect.center)
            screen.blit(letter_surf, letter_rect)

            x_pos += 50
        y_pos += 50
    
    attempts_text = small_font.render(f"Wrong guesses: {wrong_guesses}/{max_wrong_guesses}", True, WHITE)
    screen.blit(attempts_text, (700, 460))

    bar_width = 200
    bar_height = 20
    bar_x = 700
    bar_y = 490
    pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_width, bar_height), 2)
    fill_width = (wrong_guesses / max_wrong_guesses) * bar_width
    pygame.draw.rect(screen, RED, (bar_x, bar_y, fill_width, bar_height))

    if feedback and feedback_timer < feedback_duration:
        alpha = int(255 * (1 - (feedback_timer / feedback_duration)))
        feedback_color_base = GREEN if feedback.startswith("Correct") else RED
        feedback_color = (*feedback_color_base, alpha)
        feedback_surf = small_font.render(feedback, True, feedback_color)
        screen.blit(feedback_surf, (50, 550))

def draw_result_screen():
    title_text = "ACCESS GRANTED!" if game_result == "You Win!" else "SYSTEM BREACHED!"
    title_color = NEON_GREEN if game_result == "You Win!" else RED
    
    title_surface = title_font.render(title_text, True, WHITE)
    draw_text_with_glow(screen, title_text, title_font, WHITE, (WIDTH//2 - title_surface.get_width()//2, 130), title_color)
    
    result_text = font.render(f"The word was: {correct_text.upper()}", True, WHITE)
    screen.blit(result_text, (WIDTH//2 - result_text.get_rect().width//2, 190))
    
    hash_text = small_font.render(f"SHA-256: {current_hash[:20]}...", True, GRAY)
    screen.blit(hash_text, (WIDTH//2 - hash_text.get_rect().width//2, 250))
    
    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(play_again_button, "PLAY AGAIN", play_again_button.collidepoint(mouse_pos))
    
    global exit_button_result
    exit_button_result = pygame.Rect(WIDTH//2 - 100, play_again_button.bottom + 20, 200, 50)
    draw_cyber_button(exit_button_result, "EXIT", exit_button_result.collidepoint(mouse_pos))

# Button definitions
start_button = pygame.Rect(WIDTH//2 - 100, 320, 200, 50)
exit_button = pygame.Rect(WIDTH//2 - 100, 390, 200, 50)

# SHA Description Screen buttons
next_button_sha = pygame.Rect(WIDTH//2 - 100, HEIGHT - 120, 200, 50) # Adjusted Y position
back_button_sha = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)  # Adjusted Y position

# How to Play Screen buttons
continue_button_how_to_play = pygame.Rect(WIDTH//2 - 100, HEIGHT - 120, 200, 50) # Adjusted Y position
back_button_how_to_play = pygame.Rect(WIDTH//2 - 100, HEIGHT - 60, 200, 50)  # Adjusted Y position

play_again_button = pygame.Rect(WIDTH//2 - 100, 370, 200, 50)

generate_question()

clock = pygame.time.Clock()
running = True
time = 0

while running:
    dt = clock.tick(60) / 1000
    time += dt * 5
    
    if feedback_timer < feedback_duration:
        feedback_timer += dt
    else:
        feedback = ""

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_screen == START_SCREEN:
                if start_button.collidepoint(event.pos):
                    current_screen = SHA_DESCRIPTION_SCREEN
                    feedback = ""
                elif exit_button.collidepoint(event.pos):
                    running = False
            
            elif current_screen == SHA_DESCRIPTION_SCREEN:
                if next_button_sha.collidepoint(event.pos):
                    current_screen = HOW_TO_PLAY_SCREEN
                elif back_button_sha.collidepoint(event.pos):
                    current_screen = START_SCREEN

            elif current_screen == HOW_TO_PLAY_SCREEN:
                if continue_button_how_to_play.collidepoint(event.pos):
                    generate_question() 
                    current_screen = GAME_SCREEN
                    feedback = ""
                elif back_button_how_to_play.collidepoint(event.pos):
                    current_screen = SHA_DESCRIPTION_SCREEN

            elif current_screen == GAME_SCREEN:
                mouse_pos = pygame.mouse.get_pos()
                y_pos = 400
                letter_clicked = None
                
                for row_str in ["qwertyuiop", "asdfghjkl", "zxcvbnm"]:
                    x_pos = 50
                    for letter in row_str:
                        rect = pygame.Rect(x_pos, y_pos, 40, 40)
                        if rect.collidepoint(mouse_pos) and letter not in guessed_letters:
                            letter_clicked = letter
                            break
                        x_pos += 50
                    if letter_clicked:
                        break
                    y_pos += 50
                
                if letter_clicked:
                    guessed_letters.append(letter_clicked)
                    feedback_timer = 0
                    if letter_clicked in correct_text:
                        feedback = f"Correct! '{letter_clicked.upper()}' is in the word."
                        if all(char in guessed_letters for char in correct_text):
                            game_result = "You Win!"
                            current_screen = RESULT_SCREEN
                    else:
                        wrong_guesses += 1
                        feedback = f"Wrong! '{letter_clicked.upper()}' is not in the word."
                        if wrong_guesses >= max_wrong_guesses:
                            game_result = "Game Over"
                            current_screen = RESULT_SCREEN
            
            elif current_screen == RESULT_SCREEN:
                if play_again_button.collidepoint(event.pos):
                    generate_question()
                    current_screen = GAME_SCREEN
                    feedback = ""
                elif exit_button_result.collidepoint(event.pos):
                    running = False
        
        elif event.type == pygame.KEYDOWN and current_screen == GAME_SCREEN:
            if event.unicode.isalpha() and event.unicode.lower() not in guessed_letters:
                letter = event.unicode.lower()
                guessed_letters.append(letter)
                feedback_timer = 0
                if letter in correct_text:
                    feedback = f"Correct! '{letter.upper()}' is in the word."
                    if all(char in guessed_letters for char in correct_text):
                        game_result = "You Win!"
                        current_screen = RESULT_SCREEN
                else:
                    wrong_guesses += 1
                    feedback = f"Wrong! '{letter.upper()}' is not in the word."
                    if wrong_guesses >= max_wrong_guesses:
                        game_result = "Game Over"
                        current_screen = RESULT_SCREEN

    draw_gradient(screen, DARK_BLUE1, DARK_BLUE2)
    
    grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(0, WIDTH, 40):
        alpha = int(50 + 50 * np.sin(time + x / 100))
        pygame.draw.line(grid_surf, (*CYBER_BLUE[:3], alpha), (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        alpha = int(50 + 50 * np.sin(time + y / 100))
        pygame.draw.line(grid_surf, (*CYBER_BLUE[:3], alpha), (0, y), (WIDTH, y))
    screen.blit(grid_surf, (0, 0))

    for particle in particles:
        particle.move()
        particle.draw(screen)

    if current_screen == START_SCREEN:
        draw_start_screen()
    elif current_screen == SHA_DESCRIPTION_SCREEN:
        draw_sha_description_screen()
    elif current_screen == HOW_TO_PLAY_SCREEN:
        draw_how_to_play_screen()
    elif current_screen == GAME_SCREEN:
        draw_game_screen()
    elif current_screen == RESULT_SCREEN:
        draw_result_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()