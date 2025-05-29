import pygame
import sys
import random
from sympy import isprime


pygame.init()


WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
SILVER = (192, 192, 192)
DARK_BLUE1 = (5, 10, 30)
DARK_BLUE2 = (15, 30, 80)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (0, 200, 0)
BLUE = (30, 144, 255)


screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RSA Cryptography")


font = pygame.font.SysFont("Arial", 28)
title_font = pygame.font.SysFont("Arial", 44, bold=True)


button_width, button_height = 250, 80
encryption_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 - button_height - 20, button_width, button_height)
decryption_button = pygame.Rect(WIDTH//2 - button_width//2, HEIGHT//2 + 20, button_width, button_height)
back_button = pygame.Rect(50, HEIGHT - 90, 140, 60)
next_button = pygame.Rect(WIDTH - 200, HEIGHT - 90, 140, 60)
submit_button = pygame.Rect(WIDTH - 400, HEIGHT - 90, 140, 60)
hint_button = pygame.Rect(WIDTH - 600, HEIGHT - 90, 140, 60)


state = "main"
current_mode = ""  
input_text = ""
message = ""
attempts = 3
user_p, user_q = 0, 0
n, phi, e, d = 0, 0, 0, 0
word_list = ["HI", "CAT", "DOG"]
current_word = ""
m_values = []
c_values = []
show_hint = False
game_result = None
cursor_visible = True
cursor_timer = 0
CURSOR_BLINK_INTERVAL = 500
input_active = True


char_map = {chr(i + 65): i for i in range(26)}
reverse_char_map = {v: k for k, v in char_map.items()}


class BinaryStream:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.speed = random.randint(2, 5)
        self.char = random.choice(['0', '1'])
        self.alpha = random.randint(100, 180)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = random.randint(-HEIGHT, 0)
            self.x = random.randint(0, WIDTH)
            self.char = random.choice(['0', '1'])
            self.alpha = random.randint(100, 180)

    def draw(self):
        glow = font.render(self.char, True, SILVER)
        glow.set_alpha(self.alpha)
        screen.blit(glow, (self.x, self.y))

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.radius = random.choice([1, 2])
        self.speed = random.uniform(0.2, 0.6)
        self.alpha = random.randint(120, 200)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self):
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, self.alpha), (self.radius, self.radius), self.radius)
        screen.blit(s, (self.x, self.y))

streams = [BinaryStream() for _ in range(80)]
stars = [Star() for _ in range(50)]


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def rsa_keygen(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)
    e = random.randrange(2, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)
    d = pow(e, -1, phi)
    return n, phi, e, d

def encrypt(m, e, n):
    return pow(m, e, n)

def decrypt(c, d, n):
    return pow(c, d, n)

def prepare_encryption_game():
    global current_word, m_values, c_values
    current_word = random.choice(word_list)
    m_values = [char_map[ch] for ch in current_word]
    c_values = [encrypt(m, e, n) for m in m_values]

def prepare_decryption_game():
    global current_word, m_values, c_values
    current_word = random.choice(word_list)
    m_values = [char_map[ch] for ch in current_word]
    c_values = [encrypt(m, e, n) for m in m_values]

def reset_all():
    global input_text, message, attempts, user_p, user_q, n, phi, e, d
    global current_word, m_values, c_values, show_hint, game_result, current_mode
    input_text = ""
    message = ""
    attempts = 3
    user_p, user_q = 0, 0
    n, phi, e, d = 0, 0, 0, 0
    current_word = ""
    m_values = []
    c_values = []
    show_hint = False
    game_result = None
    current_mode = ""


def draw_gradient_background():
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(DARK_BLUE1[0]*(1-ratio) + DARK_BLUE2[0]*ratio)
        g = int(DARK_BLUE1[1]*(1-ratio) + DARK_BLUE2[1]*ratio)
        b = int(DARK_BLUE1[2]*(1-ratio) + DARK_BLUE2[2]*ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_animated_background():
    draw_gradient_background()
    for star in stars:
        star.update()
        star.draw()
    for stream in streams:
        stream.update()
        stream.draw()

def draw_button(rect, text, hovered=False, color=WHITE, text_color=DARK_BLUE1):
    c = (230, 230, 230) if hovered else color
    pygame.draw.rect(screen, c, rect, border_radius=12)
    label = font.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))

def draw_input_box(prompt, user_text, active=True):
    box_width, box_height = 350, 50
    box_x, box_y = WIDTH//2 - box_width//2, HEIGHT//2 - box_height//2 + 30
    
    pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=10)
    pygame.draw.rect(screen, WHITE if active else (150,150,150), (box_x+2, box_y+2, box_width-4, box_height-4), border_radius=8)
    
    text_surface = font.render(user_text, True, BLACK)
    screen.blit(text_surface, (box_x + 10, box_y + 10))
    
    prompt_surf = font.render(prompt, True, WHITE)
    screen.blit(prompt_surf, (box_x, box_y - 40))
    
    if active and cursor_visible:
        cursor_x = box_x + 10 + text_surface.get_width()
        pygame.draw.line(screen, BLACK, (cursor_x, box_y+10), (cursor_x, box_y+40), 3)


def draw_main_menu():
    draw_animated_background()
    title = title_font.render("RSA Cryptography Algorithm", True, SILVER)
    screen.blit(title, title.get_rect(center=(WIDTH//2, 100)))
    
    mouse_pos = pygame.mouse.get_pos()
    draw_button(encryption_button, "Encryption", encryption_button.collidepoint(mouse_pos))
    draw_button(decryption_button, "Decryption", decryption_button.collidepoint(mouse_pos))

def draw_encryption_instructions():
    draw_animated_background()
    title = title_font.render("Encryption Instructions", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    instructions = [
        "1. Select two large prime numbers: p and q.",
        "2. Compute n = p * q and φ(n) = (p - 1) * (q - 1).",
        "3. Choose e such that 1 < e < φ(n) and gcd(e, φ(n)) = 1.",
        "4. Compute d such that (d * e) % φ(n) = 1.",
        "5. Public key is (e, n).",
        "6. Encrypt the message M: C = (M^e) % n.",
    ]

    for i, line in enumerate(instructions):
        rendered = font.render(line, True, WHITE)
        screen.blit(rendered, (60, 140 + i * 50))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(back_button, "Back", back_button.collidepoint(mouse_pos))
    draw_button(next_button, "Next", next_button.collidepoint(mouse_pos))

def draw_decryption_instructions():
    draw_animated_background()
    title = title_font.render("Decryption Instructions", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    instructions = [
        "1. Use the private key (d, n) to decrypt.",
        "2. For each encrypted number C, compute M = (C^d) % n.",
        "3. Convert the decrypted numbers back to letters.",
        "4. Combine the letters to form the original message.",
        "5. The private key (d) is kept secret for security.",
    ]

    for i, line in enumerate(instructions):
        rendered = font.render(line, True, WHITE)
        screen.blit(rendered, (60, 140 + i * 50))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(back_button, "Back", back_button.collidepoint(mouse_pos))
    draw_button(next_button, "Next", next_button.collidepoint(mouse_pos))

def draw_prime_input_screen(prime_name):
    draw_animated_background()
    title = title_font.render(f"Enter prime number {prime_name}", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    draw_input_box(f"Enter prime {prime_name} (integer):", input_text, active=input_active)

    if message:
        msg_surf = font.render(message, True, RED)
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2 + 100))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(back_button, "Back", back_button.collidepoint(mouse_pos))
    draw_button(next_button, "Next", next_button.collidepoint(mouse_pos))

def draw_encryption_game():
    draw_animated_background()
    title = title_font.render("Encryption Game", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    info = font.render(f"Encrypt the word '{current_word}'", True, WHITE)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 100))

    prompt = font.render("Enter the encrypted numbers separated by commas:", True, WHITE)
    screen.blit(prompt, (50, 180))

    draw_input_box("", input_text, active=input_active)

    attempts_surf = font.render(f"Attempts left: {attempts}", True, GREEN if attempts > 1 else RED)
    screen.blit(attempts_surf, (50, HEIGHT - 140))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(submit_button, "Submit", submit_button.collidepoint(mouse_pos))
    draw_button(back_button, "Back", back_button.collidepoint(mouse_pos))
    draw_button(hint_button, "Hint", hint_button.collidepoint(mouse_pos))

    if message:
        msg_color = GREEN if game_result == "win" else RED
        msg_surf = font.render(message, True, msg_color)
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT - 220))

    if show_hint:
        hint_text = f"Public Key (e,n): ({e}, {n})"
        hint2 = f"Plaintext ASCII Codes: {', '.join(str(m) for m in m_values)}"
        hint_surf = font.render(hint_text, True, WHITE)
        hint_surf2 = font.render(hint2, True, WHITE)
        screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, HEIGHT - 180))
        screen.blit(hint_surf2, (WIDTH//2 - hint_surf2.get_width()//2, HEIGHT - 150))

def draw_decryption_game():
    draw_animated_background()
    title = title_font.render("Decryption Challenge", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))

    cipher_text = f"Ciphertext: {', '.join(str(c) for c in c_values)}"
    cipher_surf = font.render(cipher_text, True, WHITE)
    screen.blit(cipher_surf, (WIDTH//2 - cipher_surf.get_width()//2, 120))

    prompt = font.render("Decrypt to find the original word:", True, WHITE)
    screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 180))

    draw_input_box("Enter decrypted word:", input_text, active=input_active)

    attempts_surf = font.render(f"Attempts left: {attempts}", True, GREEN if attempts > 1 else RED)
    screen.blit(attempts_surf, (50, HEIGHT - 140))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(submit_button, "Submit", submit_button.collidepoint(mouse_pos))
    draw_button(back_button, "Back", back_button.collidepoint(mouse_pos))
    draw_button(hint_button, "Hint", hint_button.collidepoint(mouse_pos))

    if message:
        msg_color = GREEN if game_result == "win" else RED
        msg_surf = font.render(message, True, msg_color)
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT - 220))

    if show_hint:
        hint_text = f"Private Key (d,n): ({d}, {n})"
        hint2 = f"Decrypted Numbers: {', '.join(str(m) for m in m_values)}"
        hint_surf = font.render(hint_text, True, WHITE)
        hint_surf2 = font.render(hint2, True, WHITE)
        screen.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, HEIGHT - 180))
        screen.blit(hint_surf2, (WIDTH//2 - hint_surf2.get_width()//2, HEIGHT - 150))

def draw_result_screen():
    draw_animated_background()
    title = title_font.render("Result", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))

    if game_result == "win":
        result_msg = "Correct! You decrypted the message!" if current_mode == "decryption" else "Correct! You encrypted the message!"
        color = GREEN
    else:
        result_msg = f"Game Over! The word was: {current_word}"
        color = RED

    msg_surf = font.render(result_msg, True, color)
    screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 160))

    y_start = 220
    line_spacing = 40

    word_label = font.render("Original Word:", True, WHITE)
    screen.blit(word_label, (100, y_start))
    word_value = font.render(current_word, True, SILVER)
    screen.blit(word_value, (300, y_start))

    y_start += line_spacing
    m_label = font.render("Plaintext Numbers (m):", True, WHITE)
    screen.blit(m_label, (100, y_start))
    m_str = ", ".join(str(m) for m in m_values)
    m_value = font.render(m_str, True, SILVER)
    screen.blit(m_value, (400, y_start))

    y_start += line_spacing
    c_label = font.render("Encrypted Numbers (c):", True, WHITE)
    screen.blit(c_label, (100, y_start))
    c_str = ", ".join(str(c) for c in c_values)
    c_value = font.render(c_str, True, SILVER)
    screen.blit(c_value, (400, y_start))

    mouse_pos = pygame.mouse.get_pos()
    draw_button(back_button, "Back to Menu", back_button.collidepoint(mouse_pos))

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    cursor_timer += clock.get_time()
    if cursor_timer >= CURSOR_BLINK_INTERVAL:
        cursor_visible = not cursor_visible
        cursor_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if state in ["prime_input_p", "prime_input_q", "encryption_game", "decryption_game"]:
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_RETURN:
                    if state in ["prime_input_p", "prime_input_q"]:
                        if not input_text.isdigit():
                            message = "Please enter a valid integer."
                        else:
                            val = int(input_text)
                            if not isprime(val):
                                message = "Number is not prime."
                            else:
                                if state == "prime_input_p":
                                    user_p = val
                                    input_text = ""
                                    message = ""
                                    state = "prime_input_q"
                                elif state == "prime_input_q":
                                    user_q = val
                                    input_text = ""
                                    message = ""
                                    n, phi, e, d = rsa_keygen(user_p, user_q)
                                    if current_mode == "decryption":
                                        prepare_decryption_game()
                                        state = "decryption_game"
                                    else:
                                        prepare_encryption_game()
                                        state = "encryption_game"
                    elif state == "encryption_game":
                        if attempts > 0:
                            try:
                                user_input_nums = [int(x.strip()) for x in input_text.split(",")]
                            except ValueError:
                                message = "Please enter valid integers separated by commas."
                                continue
                            if user_input_nums == c_values:
                                game_result = "win"
                                message = "Correct! You win!"
                                state = "result"
                            else:
                                attempts -= 1
                                if attempts <= 0:
                                    game_result = "lose"
                                    message = "No attempts left. Game Over."
                                    state = "result"
                                else:
                                    message = f"Incorrect. Attempts left: {attempts}"
                            input_text = ""
                    elif state == "decryption_game":
                        if attempts > 0:
                            user_input = input_text.strip().upper()
                            if user_input == current_word:
                                game_result = "win"
                                message = "Correct! You decrypted the message!"
                                state = "result"
                            else:
                                attempts -= 1
                                if attempts <= 0:
                                    game_result = "lose"
                                    message = f"No attempts left. The word was: {current_word}"
                                    state = "result"
                                else:
                                    message = f"Incorrect. Attempts left: {attempts}"
                            input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    reset_all()
                    state = "main"
                else:
                    if state in ["prime_input_p", "prime_input_q"]:
                        if len(input_text) < 20 and event.unicode.isdigit():
                            input_text += event.unicode
                    elif state == "encryption_game":
                        if len(input_text) < 20 and (event.unicode.isdigit() or event.unicode == ',' or event.unicode.isspace()):
                            input_text += event.unicode.upper()
                    elif state == "decryption_game":
                        if len(input_text) < 20 and event.unicode.isalpha():
                            input_text += event.unicode.upper()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            if state == "main":
                if encryption_button.collidepoint((mx, my)):
                    current_mode = "encryption"
                    state = "encryption_instructions"
                elif decryption_button.collidepoint((mx, my)):
                    current_mode = "decryption"
                    state = "decryption_instructions"

            elif state == "encryption_instructions":
                if back_button.collidepoint((mx, my)):
                    state = "main"
                elif next_button.collidepoint((mx, my)):
                    state = "prime_input_p"
                    input_text = ""
                    message = ""
                    input_active = True

            elif state == "decryption_instructions":
                if back_button.collidepoint((mx, my)):
                    state = "main"
                elif next_button.collidepoint((mx, my)):
                    state = "prime_input_p"
                    input_text = ""
                    message = ""
                    input_active = True

            elif state in ["prime_input_p", "prime_input_q"]:
                if back_button.collidepoint((mx, my)):
                    if state == "prime_input_p":
                        state = "decryption_instructions" if current_mode == "decryption" else "encryption_instructions"
                    elif state == "prime_input_q":
                        state = "prime_input_p"
                        input_text = ""
                        message = ""
                elif next_button.collidepoint((mx, my)):
                    if not input_text.isdigit():
                        message = "Please enter a valid integer."
                    else:
                        val = int(input_text)
                        if not isprime(val):
                            message = "Number is not prime."
                        else:
                            if state == "prime_input_p":
                                user_p = val
                                input_text = ""
                                message = ""
                                state = "prime_input_q"
                            elif state == "prime_input_q":
                                user_q = val
                                input_text = ""
                                message = ""
                                n, phi, e, d = rsa_keygen(user_p, user_q)
                                if current_mode == "decryption":
                                    prepare_decryption_game()
                                    state = "decryption_game"
                                else:
                                    prepare_encryption_game()
                                    state = "encryption_game"
                                attempts = 3
                                message = ""
                                show_hint = False

            elif state == "encryption_game":
                if back_button.collidepoint((mx, my)):
                    state = "prime_input_q"
                    input_text = ""
                    message = ""
                    attempts = 3
                    show_hint = False
                    game_result = None
                elif submit_button.collidepoint((mx, my)):
                    if attempts > 0:
                        try:
                            user_input_nums = [int(x.strip()) for x in input_text.split(",")]
                        except ValueError:
                            message = "Please enter valid integers separated by commas."
                            continue
                        if user_input_nums == c_values:
                            game_result = "win"
                            message = "Correct! You win!"
                            state = "result"
                        else:
                            attempts -= 1
                            if attempts <= 0:
                                game_result = "lose"
                                message = "No attempts left. Game Over."
                                state = "result"
                            else:
                                message = f"Incorrect. Attempts left: {attempts}"
                        input_text = ""
                elif hint_button.collidepoint((mx, my)):
                    show_hint = not show_hint

            elif state == "decryption_game":
                if back_button.collidepoint((mx, my)):
                    state = "prime_input_q"
                    input_text = ""
                    message = ""
                    attempts = 3
                    show_hint = False
                    game_result = None
                elif submit_button.collidepoint((mx, my)):
                    if attempts > 0:
                        user_input = input_text.strip().upper()
                        if user_input == current_word:
                            game_result = "win"
                            message = "Correct! You decrypted the message!"
                            state = "result"
                        else:
                            attempts -= 1
                            if attempts <= 0:
                                game_result = "lose"
                                message = f"No attempts left. The word was: {current_word}"
                                state = "result"
                            else:
                                message = f"Incorrect. Attempts left: {attempts}"
                        input_text = ""
                elif hint_button.collidepoint((mx, my)):
                    show_hint = not show_hint

            elif state == "result":
                if back_button.collidepoint((mx, my)):
                    reset_all()
                    state = "main"

    # Drawing
    if state == "main":
        draw_main_menu()
    elif state == "encryption_instructions":
        draw_encryption_instructions()
    elif state == "decryption_instructions":
        draw_decryption_instructions()
    elif state == "prime_input_p":
        draw_prime_input_screen("p")
    elif state == "prime_input_q":
        draw_prime_input_screen("q")
    elif state == "encryption_game":
        draw_encryption_game()
    elif state == "decryption_game":
        draw_decryption_game()
    elif state == "result":
        draw_result_screen()

    pygame.display.flip()

pygame.quit()
sys.exit()
