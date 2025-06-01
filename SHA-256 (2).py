import pygame
import sys
import numpy as np
import random
import struct
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='game.log',
    filemode='a'
)

try:
    pygame.init()
    pygame.mixer.init()
    logging.info("PyGame initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

WIDTH, HEIGHT = 1000, 600
try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SHA-256 Step-by-Step Hash Creation Game")
    logging.info("Display initialized successfully")
except Exception as e:
    logging.error(f"Failed to set display mode: {e}")
    sys.exit(1)

# --- Colors ---
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

# --- Fonts ---
title_font = pygame.font.SysFont("arial", 48, bold=True)
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 24)
hash_font = pygame.font.SysFont("arial", 18)
info_font = pygame.font.SysFont("arial", 20)
smaller_info_font = pygame.font.SysFont("arial", 16)
description_font = pygame.font.SysFont("arial", 22)
how_to_play_font = pygame.font.SysFont("arial", 18)

# --- Game States ---
START_SCREEN = 0
SHA_DESCRIPTION_SCREEN = 1
HOW_TO_PLAY_SCREEN = 2
GAME_SCREEN = 3
RESULT_SCREEN = 4
TRANSITION_SCREEN = 5
current_screen = START_SCREEN

# --- Game Variables ---
current_hash = ""
correct_text = ""
current_step = 0
user_input = ""
feedback = ""
feedback_timer = 0
feedback_duration = 2
game_result = ""
sha_step_answers = {}
padding_options = []
hex_options = {}
show_correct_answer = False
transition_timer = 0
transition_duration = 0.5
transition_x = WIDTH

# --- Steps Definition ---
steps = [
    {"prompt": "Convert the first character to binary (8-bit ASCII):", "type": "binary_char"},
    {"prompt": "Append a '1' bit to the binary message:", "type": "padding_one"},
    {"prompt": "Pad with zeros to 448 bits mod 512. Select number of zeros:", "type": "padding_zeros"},
    {"prompt": "Append 64-bit message length (in hex):", "type": "length"},
    {"prompt": "Type first 32-bit word of the block (hex):", "type": "word"},
    {"prompt": "Compute word w[16] (in hex) using word expansion:", "type": "word_expansion"},
    {"prompt": "Compute new 'a' value after first compression round (hex):", "type": "compression"},
    {"prompt": "Concatenate final hash values (full 64-char hash):", "type": "final_hash"}
]

# --- Hangman Parts Definition ---
hangman_parts = [
    ((700, 200), (700, 400)),
    ((700, 200), (800, 200)),
    ((800, 200), (800, 250)),
    ((800, 280), 30),
    ((800, 310), (800, 380)),
    ((800, 330), (770, 350)),
    ((800, 330), (830, 350)),
    ((800, 380), (770, 420)),
    ((800, 380), (830, 420)),
    ((790, 270), (790, 270)),
    ((810, 270), (810, 270))
]

wrong_guesses = 0
max_wrong_guesses = 11

# --- Particle Class ---
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

# --- Word Loading ---
def load_words():
    return ["date", "word", "bug", "cat", "dog", "hash"]

texts = load_words()

# --- SHA-256 Helper ---
def right_rotate(n, b):
    return ((n >> b) | (n << (32 - b))) & 0xFFFFFFFF

# --- SHA-256 Function ---
def sha256_full_process_and_capture(message_text):
    global sha_step_answers
    sha_step_answers = {}

    message = message_text.encode('utf-8')

    if len(message_text) > 0:
        sha_step_answers[0] = format(ord(message_text[0]), '08b')
    else:
        sha_step_answers[0] = ""

    h_initial = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    ]

    k = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ]

    original_length_bits = len(message) * 8
    padded_message = message + b'\x80'
    sha_step_answers[1] = ''.join(format(byte, '08b') for byte in message) + '1'
    current_length_bits = len(padded_message) * 8
    correct_zeros = (448 - (current_length_bits % 512)) % 512
    sha_step_answers[2] = correct_zeros

    while (len(padded_message) * 8) % 512 != 448:
        padded_message += b'\x00'

    padded_message += struct.pack('>Q', original_length_bits)
    sha_step_answers[3] = format(original_length_bits, '016x')

    h = h_initial.copy()
    final_hash_output = ""

    for chunk_start in range(0, len(padded_message), 64):
        chunk = padded_message[chunk_start:chunk_start + 64]
        w = list(struct.unpack('>16I', chunk)) + [0] * 48

        if chunk_start == 0:
            sha_step_answers[4] = format(w[0], '08x')

        for i in range(16, 64):
            s0 = (right_rotate(w[i-15], 7) ^ right_rotate(w[i-15], 18) ^ (w[i-15] >> 3))
            s1 = (right_rotate(w[i-2], 17) ^ right_rotate(w[i-2], 19) ^ (w[i-2] >> 10))
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xFFFFFFFF

            if i == 16 and chunk_start == 0:
                sha_step_answers[5] = format(w[16], '08x')

        a, b, c, d, e, f, g, hh = h[:]

        for i in range(64):
            S1 = (right_rotate(e, 6) ^ right_rotate(e, 11) ^ right_rotate(e, 25))
            ch = (e & f) ^ ((~e) & g)
            temp1 = (hh + S1 + ch + k[i] + w[i]) & 0xFFFFFFFF
            S0 = (right_rotate(a, 2) ^ right_rotate(a, 13) ^ right_rotate(a, 22))
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            hh = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

            if i == 0 and chunk_start == 0:
                sha_step_answers[6] = format(a, '08x')

        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + hh) & 0xFFFFFFFF

    final_hash_output = "".join(f'{x:08x}' for x in h)
    sha_step_answers[7] = final_hash_output
    return final_hash_output

def generate_question():
    global current_hash, correct_text, current_step, user_input, wrong_guesses, feedback_timer, show_correct_answer, padding_options, feedback, hex_options
    correct_text = random.choice(texts)
    current_hash = sha256_full_process_and_capture(correct_text)
    current_step = 0
    user_input = ""
    wrong_guesses = 0
    feedback_timer = 0
    feedback = ""
    show_correct_answer = False
    hex_options = {}

    # Generate padding options for step 2
    correct_zeros = sha_step_answers[2]
    padding_options = [correct_zeros]
    while len(padding_options) < 4:
        offset = random.randint(-64, 64)
        wrong_option = max(0, correct_zeros + offset)
        wrong_option = (wrong_option // 8) * 8
        if wrong_option not in padding_options:
            padding_options.append(wrong_option)
    random.shuffle(padding_options)

    # Generate hex options for steps 3, 4, 5, 6, 7
    for step in [3, 4, 5, 6, 7]:
        correct_answer = sha_step_answers[step]
        options = [correct_answer]
        required_length = len(correct_answer)  # 16 for step 3, 8 for 4-6, 64 for 7
        while len(options) < 4:
            wrong_option = format(random.randint(0, 16**required_length - 1), f'0{required_length}x')
            if wrong_option not in options:
                options.append(wrong_option)
        random.shuffle(options)
        hex_options[step] = options

    logging.info(f"Generated question with word: {correct_text}, hash: {current_hash}, padding options: {tuple(padding_options)}, hex_options: {hex_options}")
    logging.debug(f"SHA Step Answers: {sha_step_answers}")
    return current_hash

def get_correct_answer(step):
    return str(sha_step_answers.get(step, ""))

def validate_input(step, user_input_raw):
    correct_answer = get_correct_answer(step)
    user_input = str(user_input_raw).strip().lower()

    logging.debug(f"Validating Step {step}: Input: '{user_input}', Correct: '{correct_answer}'")

    if step in [0, 1]:
        return user_input == correct_answer
    elif step in [2, 3, 4, 5, 6, 7]:
        try:
            if step == 2:
                return int(user_input) == int(correct_answer)
            else:
                return user_input == correct_answer
        except Exception:
            return False
    return False

# --- Drawing Utilities ---
def draw_gradient(surface, color1, color2):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_cyber_button(screen, rect, text, is_hovered=False, font=None):
    button_color = PURE_WHITE
    border_color = CYBER_BLUE
    text_color = BLACK
    if is_hovered:
        button_color = ACTIVE_BLUE
        border_color = CYBER_BLUE
        text_color = WHITE
    pygame.draw.rect(screen, button_color, rect, border_radius=10)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)
    text_font = font if font else small_font
    text_surf = text_font.render(text, True, text_color)
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

# --- Screen Drawing Functions ---
def draw_start_screen():
    title_text = "SHA-256 Step-by-Step Hash Creation Game"
    title_surface = title_font.render(title_text, True, WHITE)
    draw_text_with_glow(screen, title_text, title_font, WHITE, (WIDTH // 2 - title_surface.get_width() // 2, 100), BLACK)
    subtitle = font.render("Create the SHA-256 hash step by step", True, WHITE)
    screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 190))
    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(screen, start_button, "START", start_button.collidepoint(mouse_pos))
    draw_cyber_button(screen, exit_button, "EXIT", exit_button.collidepoint(mouse_pos))
    footer = small_font.render(f"Wrong guesses allowed: {max_wrong_guesses}", True, GRAY)
    screen.blit(footer, (WIDTH // 2 - footer.get_width() // 2, 460))

def draw_sha_description_screen():
    title_text = "What is SHA-256?"
    title_surface = title_font.render(title_text, True, WHITE)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 50))
    description_pages = [
        [
            "How to create the SHA-256 hash step-by-step:",
            "",
            "1. Convert the original message into binary:",
            "Each character is represented by 8 bits using ASCII encoding.",
            "For example, 'abc' becomes:",
            "",
            "'a' → 01100001",
            "'b' → 01100010",
            "'c' → 01100011",
            "",
            "The message becomes a string of binary digits.",
            "",
            "2. Append a single '1' bit:",
            "Add one '1' bit after the binary message to mark its end."
        ],
        [
            "3. Add '0' bits until length is 448 bits modulo 512:",
            "Add enough '0' bits after the '1' bit to reach 448 bits.",
            "This prepares the message for 512-bit blocks.",
            "",
            "4. Append 64-bit message length:",
            "Add the original message length (in bits) as a 64-bit number.",
            "The total length becomes a multiple of 512 bits.",
            "",
            "5. Split into 512-bit blocks:",
            "Divide the padded message into 512-bit (64-byte) chunks.",
            "Each block has 16 32-bit words.",
            "",
            "6. Extend 16 words to 64 words:",
            "Use rotations, shifts, and XOR to expand 16 words to 64."
        ],
        [
            "7. Initialize eight hash values (a to h):",
            "Start with 8 predefined 32-bit constants.",
            "",
            "8. Perform 64 rounds of compression:",
            "Update a, b, c, d, e, f, g, h with modular addition, XOR, etc.",
            "Each round uses the words and constants.",
            "",
            "9. Add results to initial hash values:",
            "Add the new a-h values to the initial ones.",
            "",
            "10. Concatenate to form the 256-bit hash:",
            "Combine the 8 32-bit values into a 64-char hex hash."
        ]
    ]
    global sha_page_num
    y_offset = 100
    for line in description_pages[sha_page_num]:
        line_surf = description_font.render(line, True, WHITE)
        screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y_offset))
        y_offset += 30
    mouse_pos = pygame.mouse.get_pos()
    if sha_page_num < len(description_pages) - 1:
        draw_cyber_button(screen, continue_button_sha, "NEXT", continue_button_sha.collidepoint(mouse_pos))
    else:
        draw_cyber_button(screen, continue_button_sha, "CONTINUE", continue_button_sha.collidepoint(mouse_pos))
    draw_cyber_button(screen, back_button_sha, "BACK", back_button_sha.collidepoint(mouse_pos))

def draw_how_to_play_screen():
    description_title = title_font.render("How to Play", True, WHITE)
    screen.blit(description_title, (WIDTH // 2 - description_title.get_width() // 2, 70))
    description_text_lines = [
        "Welcome to the SHA-256 Hash Creation Game!",
        "",
        "Your goal is to create the SHA-256 hash for a given word.",
        "The word will be shown, and you compute its hash step by step.",
        "",
        "Follow these steps:",
        "- Convert the message to binary.",
        "- Add padding and length.",
        "- Process blocks and compression rounds.",
        "- Form the final hash.",
        "",
        "Type your answer for binary steps or select an option for others.",
        
    ]
    y_offset = 140
    for line in description_text_lines:
        line_surf = how_to_play_font.render(line, True, WHITE)
        screen.blit(line_surf, (WIDTH // 2 - line_surf.get_width() // 2, y_offset))
        y_offset += 24
    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(screen, continue_button_how_to_play, "START GAME", continue_button_how_to_play.collidepoint(mouse_pos))
    draw_cyber_button(screen, back_button_how_to_play, "BACK", back_button_how_to_play.collidepoint(mouse_pos))

def draw_game_screen():
    word_title = small_font.render(f"Word to hash: {correct_text.upper()}", True, WHITE)
    screen.blit(word_title, (50, 100))

    # Draw hangman parts
    try:
        for i in range(min(wrong_guesses, len(hangman_parts))):
            part = hangman_parts[i]
            if isinstance(part[0], tuple) and isinstance(part[1], tuple):
                if part[0] == part[1]:  # Dots (eyes)
                    pygame.draw.circle(screen, WHITE, part[0], 3)
                else:  # Lines
                    pygame.draw.line(screen, WHITE, part[0], part[1], 3)
            else:  # Circle (head)
                pygame.draw.circle(screen, WHITE, part[0], part[1], 3)
            logging.debug(f"Drew hangman part {i+1}/{len(hangman_parts)}")
    except Exception as e:
        logging.error(f"Error drawing hangman part {i+1}: {e}")

    prompt_text = small_font.render(steps[current_step]["prompt"], True, WHITE)
    screen.blit(prompt_text, (50, 300))

    mouse_pos = pygame.mouse.get_pos()

    if show_correct_answer:
        correct_ans_text = info_font.render(f"The correct answer was: {get_correct_answer(current_step)}", True, NEON_GREEN)
        if current_step in [2, 3, 4, 5, 6, 7]:
            screen.blit(correct_ans_text, (50, 500))
        else:
            screen.blit(correct_ans_text, (50, 340))
    elif current_step in [0, 1]:
        input_box_rect = pygame.Rect(50, 340, 400, 50)
        pygame.draw.rect(screen, PURE_WHITE, input_box_rect, border_radius=5)
        pygame.draw.rect(screen, GRAY, input_box_rect, 2, border_radius=5)

        input_surf = small_font.render(user_input, True, BLACK)
        screen.blit(input_surf, (input_box_rect.x + 5, input_box_rect.y + 5))

        draw_cyber_button(screen, submit_button, "SUBMIT", submit_button.collidepoint(mouse_pos))
    elif current_step in [2, 3, 4, 5, 6, 7]:
        y_pos_start = 340
        x_pos_start = 50
        button_width = 600 if current_step == 7 else 250 if current_step == 3 else 150
        button_height = 40
        padding = 10
        options = padding_options if current_step == 2 else hex_options.get(current_step, [])
        columns = 1 if current_step == 7 else 2
        for idx, option in enumerate(options):
            if current_step == 7:
                x_pos = x_pos_start
                y_pos = y_pos_start + idx * (button_height + padding)
            else:
                x_pos = x_pos_start + (idx % columns) * (button_width + padding)
                y_pos = y_pos_start + (idx // columns) * (button_height + padding)
            rect = pygame.Rect(x_pos, y_pos, button_width, button_height)
            font = hash_font if current_step == 7 else small_font
            draw_cyber_button(screen, rect, str(option), rect.collidepoint(mouse_pos), font=font)

    if feedback:
        feedback_color = GREEN if "Correct" in feedback else RED
        feedback_surf = info_font.render(feedback, True, feedback_color)
        screen.blit(feedback_surf, (50, 500))

def draw_result_screen():
    result_text = title_font.render(game_result, True, WHITE)
    screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 80))

    if game_result == "Game Over":
        original_word_label = info_font.render(f"The word was: {correct_text.upper()}", True, PURE_WHITE)
        screen.blit(original_word_label, (WIDTH // 2 - original_word_label.get_width() // 2, HEIGHT // 2 - 20))
        correct_hash_label = info_font.render("The correct SHA-256 hash was:", True, PURE_WHITE)
        screen.blit(correct_hash_label, (WIDTH // 2 - correct_hash_label.get_width() // 2, HEIGHT // 2 + 10))
        correct_hash_value = hash_font.render(current_hash, True, NEON_GREEN)
        screen.blit(correct_hash_value, (WIDTH // 2 - correct_hash_value.get_width() // 2, HEIGHT // 2 + 40))
    elif game_result == "You Win!":
        final_hash_label = info_font.render(f"Original Word: {correct_text.upper()}", True, PURE_WHITE)
        screen.blit(final_hash_label, (WIDTH // 2 - final_hash_label.get_width() // 2, HEIGHT // 2 + 20))
        final_hash_value = hash_font.render(f"Your SHA-256 Hash: {current_hash}", True, NEON_GREEN)
        screen.blit(final_hash_value, (WIDTH // 2 - final_hash_value.get_width() // 2, HEIGHT // 2 + 60))

    mouse_pos = pygame.mouse.get_pos()
    draw_cyber_button(screen, play_again_button, "TRY AGAIN", play_again_button.collidepoint(mouse_pos))
    draw_cyber_button(screen, exit_button_result, "EXIT", exit_button_result.collidepoint(mouse_pos))

def draw_transition_screen():
    global transition_x
    transition_surface = pygame.Surface((WIDTH, HEIGHT))
    draw_gradient(transition_surface, DARK_BLUE1, DARK_BLUE2)
    draw_result_screen()
    screen.blit(transition_surface, (transition_x, 0))

# --- Button Definitions ---
start_button = pygame.Rect(WIDTH // 2 - 75, 270, 150, 50)
exit_button = pygame.Rect(WIDTH // 2 - 75, 340, 150, 50)
continue_button_sha = pygame.Rect(WIDTH // 2 + 10, HEIGHT - 70, 150, 40)
back_button_sha = pygame.Rect(WIDTH // 2 - 160, HEIGHT - 70, 150, 40)
continue_button_how_to_play = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)
back_button_how_to_play = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 90, 200, 50)
submit_button = pygame.Rect(460, 340, 100, 40)
play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)
exit_button_result = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 180, 200, 50)

# Initialize sha_page_num
sha_page_num = 0

# Generate first question
generate_question()

# --- Game Loop ---
clock = pygame.time.Clock()
running = True
time = 0.0

while running:
    dt = clock.tick(60) / 1000
    time += dt * 5

    if current_screen == TRANSITION_SCREEN:
        transition_timer += dt
        transition_x = WIDTH - (WIDTH * (transition_timer / transition_duration))
        if transition_timer >= transition_duration:
            current_screen = RESULT_SCREEN
            transition_timer = 0
            transition_x = WIDTH
            logging.info("Transition to RESULT_SCREEN completed")
    elif feedback_timer < feedback_duration:
        feedback_timer += dt
    else:
        feedback = ""
        if show_correct_answer and game_result == "Game Over":
            current_screen = TRANSITION_SCREEN
            transition_timer = 0
            transition_x = WIDTH
            show_correct_answer = False
            logging.info("Initiated transition to RESULT_SCREEN after Game Over")

    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Quit event received")
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if current_screen == START_SCREEN:
                    if start_button.collidepoint(mouse_pos):
                        current_screen = SHA_DESCRIPTION_SCREEN
                        sha_page_num = 0
                        logging.info("Start button clicked")
                    elif exit_button.collidepoint(mouse_pos):
                        running = False
                        logging.info("Exit button clicked")

                elif current_screen == SHA_DESCRIPTION_SCREEN:
                    if continue_button_sha.collidepoint(mouse_pos):
                        if sha_page_num < 2:
                            sha_page_num += 1
                        else:
                            current_screen = HOW_TO_PLAY_SCREEN
                        logging.info(f"Continue button clicked, sha_page_num: {sha_page_num}")
                    elif back_button_sha.collidepoint(mouse_pos):
                        if sha_page_num > 0:
                            sha_page_num -= 1
                        else:
                            current_screen = START_SCREEN
                        logging.info(f"Back button clicked, sha_page_num: {sha_page_num}")

                elif current_screen == HOW_TO_PLAY_SCREEN:
                    if continue_button_how_to_play.collidepoint(mouse_pos):
                        generate_question()
                        current_screen = GAME_SCREEN
                        logging.info("Start game button clicked")
                    elif back_button_how_to_play.collidepoint(mouse_pos):
                        current_screen = SHA_DESCRIPTION_SCREEN
                        logging.info("Back to SHA description")

                elif current_screen == GAME_SCREEN and not show_correct_answer:
                    try:
                        if current_step in [0, 1] and submit_button.collidepoint(mouse_pos) and user_input:
                            if validate_input(current_step, user_input):
                                feedback = "Correct! Moving to next step."
                                current_step += 1
                                user_input = ""
                                if current_step >= len(steps):
                                    game_result = "You Win!"
                                    current_screen = TRANSITION_SCREEN
                                    transition_timer = 0
                                    transition_x = WIDTH
                                    logging.info(f"Correct input for step {current_step - 1}. Transition to RESULT_SCREEN (Win)")
                                else:
                                    logging.info(f"Correct input for step {current_step - 1}. New step: {current_step}")
                            else:
                                wrong_guesses += 1
                                logging.info(f"Wrong input for step {current_step}, wrong_guesses: {wrong_guesses}")
                                if wrong_guesses >= max_wrong_guesses:
                                    game_result = "Game Over"
                                    feedback = f"Game Over! The correct answer was: {get_correct_answer(current_step)}"
                                    show_correct_answer = True
                                    feedback_timer = 0
                                    logging.info(f"Max wrong guesses ({max_wrong_guesses}) reached at step {current_step}. Setting game_result: {game_result}")
                                else:
                                    feedback = f"Wrong! Try again. ({max_wrong_guesses - wrong_guesses} guesses left)"
                            feedback_timer = 0
                        elif current_step in [2, 3, 4, 5, 6, 7]:
                            y_pos_start = 340
                            x_pos_start = 50
                            button_width = 600 if current_step == 7 else 250 if current_step == 3 else 150
                            button_height = 40
                            padding = 10
                            columns = 1 if current_step == 7 else 2
                            options = padding_options if current_step == 2 else hex_options.get(current_step, [])
                            for idx, option in enumerate(options):
                                if current_step == 7:
                                    x_pos = x_pos_start
                                    y_pos = y_pos_start + idx * (button_height + padding)
                                else:
                                    x_pos = x_pos_start + (idx % columns) * (button_width + padding)
                                    y_pos = y_pos_start + (idx // columns) * (button_height + padding)
                                rect = pygame.Rect(x_pos, y_pos, button_width, button_height)
                                if rect.collidepoint(mouse_pos):
                                    if validate_input(current_step, str(option)):
                                        feedback = "Correct! Moving to next step."
                                        current_step += 1
                                        user_input = ""
                                        if current_step >= len(steps):
                                            game_result = "You Win!"
                                            current_screen = TRANSITION_SCREEN
                                            transition_timer = 0
                                            transition_x = WIDTH
                                            logging.info(f"Correct option {option} for step {current_step - 1}. Transition to RESULT_SCREEN (Win)")
                                        else:
                                            logging.info(f"Correct option {option} for step {current_step - 1}. New step: {current_step}")
                                    else:
                                        wrong_guesses += 1
                                        logging.info(f"Wrong option {option} for step {current_step}, wrong_guesses: {wrong_guesses}")
                                        if wrong_guesses >= max_wrong_guesses:
                                            game_result = "Game Over"
                                            feedback = f"Game Over! The correct answer was: {get_correct_answer(current_step)}"
                                            show_correct_answer = True
                                            feedback_timer = 0
                                            logging.info(f"Max wrong guesses ({max_wrong_guesses}) reached at step {current_step}. Setting game_result: {game_result}")
                                        else:
                                            feedback = f"Wrong! Try again. ({max_wrong_guesses - wrong_guesses} guesses left)"
                                    feedback_timer = 0
                                    break

                    except Exception as e:
                        logging.error(f"Error processing mouse input in GAME_SCREEN: {e}")

                elif current_screen == RESULT_SCREEN:
                    if play_again_button.collidepoint(mouse_pos):
                        generate_question()
                        current_screen = GAME_SCREEN
                        feedback = ""
                        logging.info("Play again clicked")
                    elif exit_button_result.collidepoint(mouse_pos):
                        running = False
                        logging.info("Exit from result screen")

            elif event.type == pygame.KEYDOWN and current_screen == GAME_SCREEN and current_step in [0, 1] and not show_correct_answer:
                try:
                    if event.key == pygame.K_RETURN and user_input:
                        if validate_input(current_step, user_input):
                            feedback = "Correct! Moving to next step."
                            current_step += 1
                            user_input = ""
                            if current_step >= len(steps):
                                game_result = "You Win!"
                                current_screen = TRANSITION_SCREEN
                                transition_timer = 0
                                transition_x = WIDTH
                                logging.info(f"Correct input for step {current_step - 1} via Enter. Transition to RESULT_SCREEN (Win)")
                            else:
                                logging.info(f"Correct input for step {current_step - 1} via Enter. New step: {current_step}")
                        else:
                            wrong_guesses += 1
                            logging.info(f"Wrong input for step {current_step}, wrong_guesses: {wrong_guesses}")
                            if wrong_guesses >= max_wrong_guesses:
                                game_result = "Game Over"
                                feedback = f"Game Over! The correct answer was: {get_correct_answer(current_step)}"
                                show_correct_answer = True
                                feedback_timer = 0
                                logging.info(f"Max wrong guesses ({max_wrong_guesses}) reached at step {current_step}. Setting game_result: {game_result}")
                            else:
                                feedback = f"Wrong! Try again. ({max_wrong_guesses - wrong_guesses} guesses left)"
                        feedback_timer = 0
                    elif event.key == pygame.K_BACKSPACE:
                        user_input = user_input[:-1]
                        logging.debug(f"Backspace pressed, user_input: {user_input}")
                    elif event.unicode.isprintable():
                        user_input += event.unicode
                        logging.debug(f"Key pressed, user_input: {user_input}")
                except Exception as e:
                    logging.error(f"Error processing keyboard input in GAME_SCREEN: {e}")

        # --- Drawing ---
        draw_gradient(screen, DARK_BLUE1, DARK_BLUE2)

        grid_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for x in range(0, WIDTH, 40):
            alpha = int(50 + 50 * np.sin(time + x / 100))
            pygame.draw.line(grid_surf, (*CYBER_BLUE[:3], alpha), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
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
        elif current_screen == TRANSITION_SCREEN:
            draw_transition_screen()

        try:
            pygame.display.flip()
        except pygame.error as e:
            logging.error(f"Failed to update display: {e}")
            running = False

    except Exception as e:
        logging.error(f"Error in main game loop: {e}")
        running = False

pygame.quit()
sys.exit()