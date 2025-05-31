import pygame
import sys
import random
import math

# --- Asset Paths ---
BG_IMAGE_PATH = r"C:\Users\sarah\Desktop\CryptographyProjectFINAL\cryptography-algorithms\20250531_0049_Binary Data Wave_remix_01jwhjnp11epgrkmnea8hnwpv2.png"
SURFER_IMAGE_PATH = r"C:\Users\sarah\Desktop\CryptographyProjectFINAL\cryptography-algorithms\20250531_0058_Surfer Above Water_remix_01jwhk65x6fkaa7va7bs0zcqn9.png"

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DES Educational Game")
clock = pygame.time.Clock()

# --- Load Assets ---
try:
    bg_image = pygame.image.load(BG_IMAGE_PATH)
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    surfer_img = pygame.image.load(SURFER_IMAGE_PATH)
    surfer_img = pygame.transform.scale(surfer_img, (150, 150))
except pygame.error:
    # Fallback if images don't load
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((0, 0, 50))  # Dark blue background
    surfer_img = pygame.Surface((100, 100))
    surfer_img.fill((255, 255, 255))  # White placeholder

# --- Fonts ---
FONT = pygame.font.SysFont('Consolas', 28)
BIG_FONT = pygame.font.SysFont('Consolas', 48)

# --- Game Variables ---
state = "main_menu"
mode = None
lives = 3
score = 0
current_question = 0
user_encrypt_input = ""
input_active = False
angle = 0

# For step-by-step explanation after each question
showing_step = False
step_to_show = 0
step_explanation_text = []
answered_correctly = False

game_over_message = ""

encrypt_game_entry_time = 0  # Debounce for answer clicks

def show_encryption_steps(text):
    steps = [
        "To perform DES on a string, we follow these steps:",
        f"1) Convert the string '{text}' to binary using ASCII codes.",
        "2) Rearrange the bits using the Initial Permutation (IP).",
        "3) Split the 64-bit binary block into two 32-bit halves.",
        "4) Run 16 rounds of operations: expand, XOR with key, substitute, permute.",
        "5) Swap the left and right halves after all rounds.",
        "6) Apply the Final Permutation (FP).",
        "7) Combine the final bits to get the encrypted result."
    ]
    return steps

# --- MCQ Questions for each DES step ---
MCQ_QUESTIONS = [
    {
        "question": "What is the first step in DES encryption?",
        "choices": [
            "Convert text to binary (ASCII)",
            "Final Permutation",
            "Key Mixing",
            "Apply S-box"
        ],
        "answer": 0,
        "explanation": "Step 1: Convert each character into binary (ASCII representation)."
    },
    {
        "question": "What is the Initial Permutation (IP)?",
        "choices": [
            "A step to convert binary to decimal",
            "A rearrangement of the key bits",
            "A rearrangement of the data bits before rounds",
            "A bitwise NOT operation"
        ],
        "answer": 2,
        "explanation": "Step 2: Apply Initial Permutation to reorder the input bits."
    },
    {
        "question": "What happens after the initial permutation?",
        "choices": [
            "Substitution using S-boxes",
            "Split into Left/Right halves",
            "Final Permutation",
            "XOR with the key"
        ],
        "answer": 1,
        "explanation": "Step 3: The permuted bits are divided into left and right halves."
    },
    {
        "question": "Which operations are involved in the 16 DES rounds?",
        "choices": [
            "Expansion, XOR, S-box, Permutation",
            "Permutation, NOT, AND, XOR",
            "Split, Merge, Sort, XOR",
            "IP, FP, IP, FP"
        ],
        "answer": 0,
        "explanation": "Step 4: Each of the 16 rounds uses Expansion, XOR, S-box, and Permutation."
    },
    {
        "question": "What happens after each DES round?",
        "choices": [
            "Apply Initial Permutation again",
            "Swap the key with data",
            "Swap Left and Right halves",
            "Do nothing"
        ],
        "answer": 2,
        "explanation": "Step 5: After each round, the left and right halves are swapped."
    },
    {
        "question": "What is the Final Permutation (FP)?",
        "choices": [
            "Swapping the final halves",
            "Reversing the entire process",
            "Permuting bits to finalize ciphertext",
            "Encrypting the key"
        ],
        "answer": 2,
        "explanation": "Step 6: Apply Final Permutation to produce the ciphertext."
    },
    {
        "question": "What is the last step in DES?",
        "choices": [
            "Convert bits back to text or binary output",
            "Apply Initial Permutation again",
            "Generate a new key",
            "Perform checksum"
        ],
        "answer": 0,
        "explanation": "Step 7: Combine final bits and convert back to readable format."
    }
]

# --- UI Components ---
input_box_rect = pygame.Rect(WIDTH//2 - 200, 250, 400, 50)
gradient_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(HEIGHT):
    alpha = int(220 * (1 - y / HEIGHT))
    pygame.draw.line(gradient_overlay, (10, 10, 30, alpha), (0, y), (WIDTH, y))

class Button:
    def __init__(self, text, x, y, w, h, color, text_color, callback):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text_color = text_color
        self.callback = callback
        self.hovered = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3, border_radius=8)
        txt = FONT.render(self.text, True, self.text_color)
        surface.blit(txt, (self.rect.x + (self.rect.w - txt.get_width()) // 2, self.rect.y + (self.rect.h - txt.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

# --- State Management ---
def set_state(new_state):
    global state, input_active, showing_step, step_to_show, step_explanation_text, encrypt_game_entry_time
    state = new_state
    input_active = (state == "encrypt_input")
    if new_state == "step_explanation":
        pass
    elif new_state == "encrypt_game":
        global showing_step
        showing_step = False
        # If lives==0, go to game_over
        if lives <= 0:
            state = "game_over"
        # If all questions done, go to game_over
        elif current_question >= len(MCQ_QUESTIONS):
            state = "game_over"
        pygame.event.clear()
        encrypt_game_entry_time = pygame.time.get_ticks()

def start_encrypt():
    set_state("encrypt_input")

def start_decrypt():
    print("Decrypt mode coming soon!")

def next_to_explain():
    if user_encrypt_input:
        set_state("encrypt_explain")

def start_quiz():
    set_state("encrypt_game")

# --- Buttons ---
button_width, button_height = 260, 70
menu_buttons = [
    Button("Encrypt", WIDTH//2 - button_width//2, HEIGHT//2 - 80, button_width, button_height, (44, 125, 160), (255,255,255), start_encrypt),
    Button("Decrypt", WIDTH//2 - button_width//2, HEIGHT//2 + 20, button_width, button_height, (1, 79, 134), (255,255,255), start_decrypt)
]
next_btn = Button("Next", WIDTH//2 - 80, 340, 160, 50, (44, 125, 160), (255,255,255), next_to_explain)
continue_btn = Button("Continue", WIDTH//2 - 80, 500, 160, 50, (44, 125, 160), (255,255,255), start_quiz)

# Add a Back to Menu button for game over
back_to_menu_btn = Button("Back to Menu", WIDTH//2 - 100, 480, 200, 60, (44, 125, 160), (255,255,255), lambda: set_state("main_menu"))

# Add a Restart button for game over
restart_btn = Button("Restart", WIDTH//2 - 220, 400, 180, 60, (44, 160, 80), (255,255,255), lambda: (restart_game(), set_state("encrypt_input")))
# Add a Quit button for game over
quit_btn = Button("Quit", WIDTH//2 + 40, 400, 180, 60, (200, 60, 60), (255,255,255), lambda: (restart_game(), set_state("main_menu")))

# Add a Continue button for step explanation
continue_step_btn = Button("Continue", WIDTH//2 - 80, 480, 160, 50, (44, 125, 160), (255,255,255), lambda: set_state("encrypt_game"))

def get_step_explanation(step_idx, user_text):
    # Step 1: Convert to ASCII and binary
    if step_idx == 0:
        ascii_codes = [str(ord(c)) for c in user_text]
        binary_codes = [format(ord(c), '08b') for c in user_text]
        return [
            f"Original string: {user_text}",
            "ASCII codes: " + ' '.join(ascii_codes),
            "Binary: " + ' '.join(binary_codes)
        ]
    # Step 2: Initial Permutation (mock)
    elif step_idx == 1:
        binary_str = ''.join(format(ord(c), '08b') for c in user_text)
        # Mock permutation: reverse the string for illustration
        permuted = binary_str[::-1]
        return [
            "Initial Permutation (IP):",
            f"Input bits:   {binary_str}",
            f"Permuted bits: {permuted}",
            "(Real DES uses a fixed table, this is for illustration)"
        ]
    # Step 3: Split into halves
    elif step_idx == 2:
        binary_str = ''.join(format(ord(c), '08b') for c in user_text)
        padded = binary_str.ljust(64, '0')[:64]
        left = padded[:32]
        right = padded[32:]
        return [
            "Split into halves:",
            f"Full 64 bits: {padded}",
            f"Left 32:  {left}",
            f"Right 32: {right}"
        ]
    # Step 4: Feistel rounds (mock)
    elif step_idx == 3:
        return [
            "Feistel Rounds (16x):",
            "Each round: Expansion, XOR with key, S-box, Permutation",
            "(Not shown in detail here)",
            "After 16 rounds, halves are swapped."
        ]
    # Step 5: Swap halves (visual)
    elif step_idx == 4:
        binary_str = ''.join(format(ord(c), '08b') for c in user_text)
        padded = binary_str.ljust(64, '0')[:64]
        left = padded[:32]
        right = padded[32:]
        swapped = right + left
        return [
            "Swap Halves:",
            f"Before: {left} | {right}",
            f"After:  {right} | {left}",
            f"Swapped: {swapped}"
        ]
    # Step 6: Final Permutation (mock)
    elif step_idx == 5:
        binary_str = ''.join(format(ord(c), '08b') for c in user_text)
        padded = binary_str.ljust(64, '0')[:64]
        # Mock permutation: rotate left by 1
        permuted = padded[1:] + padded[0]
        return [
            "Final Permutation (FP):",
            f"Input bits:   {padded}",
            f"Permuted bits: {permuted}",
            "(Real DES uses a fixed table, this is for illustration)"
        ]
    # Step 7: Combine bits (mock output)
    elif step_idx == 6:
        binary_str = ''.join(format(ord(c), '08b') for c in user_text)
        padded = binary_str.ljust(64, '0')[:64]
        return [
            "Combine bits to get ciphertext:",
            f"Ciphertext (binary): {padded}",
            "(In real DES, this would be the encrypted output)"
        ]
    # Fallback
    return ["DES step complete!"]

def restart_game():
    global lives, score, current_question, user_encrypt_input, input_active, angle, showing_step, step_to_show, step_explanation_text, answered_correctly, game_over_message
    lives = 3
    score = 0
    current_question = 0
    user_encrypt_input = ""
    input_active = False
    angle = 0
    showing_step = False
    step_to_show = 0
    step_explanation_text = []
    answered_correctly = False
    game_over_message = ""
    set_state("encrypt_game")  
    pygame.event.clear()

def quit_game():
    pygame.quit()
    sys.exit()

# Helper to wrap long text lines
def draw_wrapped_text(surface, text, font, color, x, y, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    for i, line in enumerate(lines):
        txt = font.render(line, True, color)
        surface.blit(txt, (x, y + i * (font.get_height() + 4)))
    return len(lines)

# Helper to count wrapped lines
def count_wrapped_lines(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return len(lines)

# Helper to detect code/monospaced lines in step explanations
CODE_KEYWORDS = [
    "input bits:", "permuted bits:", "ciphertext", "ascii codes:", "binary:",
    "left", "right", "full 64 bits:", "before:", "after:", "swapped:",
    "output bits:", "permuted:", "padded:", "split:", "combined:", "ip:", "fp:",
    "s-box:", "expansion:", "key:", "round:", "block:", "original string:",
    "feistel", "swap halves:", "split into halves:", "initial permutation (ip):",
    "final permutation (fp):"
]
def is_code_line(line):
    l = line.strip().lower()
    return any(l.startswith(k) for k in CODE_KEYWORDS)

def render_code_line(surface, line, font, color, x, y, max_width):
    display_line = line
    txt = font.render(display_line, True, color)
    # Truncate with ellipsis if too wide
    if txt.get_width() > max_width:
        while len(display_line) > 3 and font.size(display_line + "...")[0] > max_width:
            display_line = display_line[:-1]
        display_line += "..."
        txt = font.render(display_line, True, color)
    surface.blit(txt, (x, y))
    return font.get_height() + 4

angle = 0
# --- Main Loop ---
running = True
while running:
    screen.blit(bg_image, (0, 0))
    screen.blit(gradient_overlay, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if state == "main_menu":
            for btn in menu_buttons:
                btn.handle_event(event)

        elif state == "encrypt_input":
            if event.type == pygame.MOUSEBUTTONDOWN:
                input_active = input_box_rect.collidepoint(event.pos)
                next_btn.handle_event(event)
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    user_encrypt_input = user_encrypt_input[:-1]
                elif event.key == pygame.K_RETURN:
                    next_to_explain()
                elif len(user_encrypt_input) < 24 and event.unicode.isprintable():
                    user_encrypt_input += event.unicode

        elif state == "encrypt_explain":
            continue_btn.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                set_state("encrypt_game")

        # --- Handle answer button clicks ---
        if state == "encrypt_game":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Debounce: ignore clicks for 200 ms after entering encrypt_game
                if pygame.time.get_ticks() - encrypt_game_entry_time < 200:
                    continue
                if current_question < len(MCQ_QUESTIONS):
                    q = MCQ_QUESTIONS[current_question]
                    choice_w = 420
                    choice_x = WIDTH - choice_w - 100
                    spacing = 24
                    y_offset = 100
                    # Account for wrapped question text
                    lines_used = count_wrapped_lines(q["question"], FONT, WIDTH - 160)
                    y_offset += lines_used * (FONT.get_height() + 4) + 20
                    for i, choice in enumerate(q["choices"]):
                        lines = count_wrapped_lines(choice, FONT, choice_w - 20)
                        choice_h = lines * (FONT.get_height() + 4) + 20
                        btn_rect = pygame.Rect(choice_x, y_offset, choice_w, choice_h)
                        if btn_rect.collidepoint(event.pos):
                            if i == q["answer"]:
                                showing_step = True
                                step_to_show = current_question
                                step_explanation_text = get_step_explanation(step_to_show, user_encrypt_input)
                                answered_correctly = True
                                set_state("step_explanation")
                                pygame.event.clear()
                            else:
                                lives -= 1
                                answered_correctly = False
                                if lives <= 0:
                                    set_state("game_over")
                                    game_over_message = f"Game Over! Final Score: {score}/{len(MCQ_QUESTIONS)}"
                            break
                        y_offset += choice_h + spacing

        if state == "game_over":
            if event.type == pygame.MOUSEBUTTONDOWN:
                restart_btn.handle_event(event)
                quit_btn.handle_event(event)
                break

        elif state == "step_explanation":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                # After pressing space/enter, update question/score only if correct
                if answered_correctly:
                    current_question += 1
                    score += 1
                set_state("encrypt_game")

    # --- Drawing section ---
    if state == "main_menu":
        title = BIG_FONT.render("Welcome to DES", True, (204, 51, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for btn in menu_buttons:
            btn.draw(screen)

    elif state == "encrypt_input":
        title = BIG_FONT.render("DES Encryption", True, (204, 51, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        prompt = FONT.render("Enter a string to encrypt using DES:", True, (255,255,255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 180))
        pygame.draw.rect(screen, (30,30,30), input_box_rect, border_radius=8)
        border_col = (44, 125, 160) if input_active else (100,100,100)
        pygame.draw.rect(screen, border_col, input_box_rect, 3, border_radius=8)
        input_surf = FONT.render(user_encrypt_input or "Type your text...", True, (173,216,230) if user_encrypt_input else (120,120,120))
        screen.blit(input_surf, (input_box_rect.x+15, input_box_rect.y+10))
        if user_encrypt_input:
            next_btn.draw(screen)

    elif state == "encrypt_explain":
        title = BIG_FONT.render("DES Encryption Steps", True, (204, 51, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        steps = show_encryption_steps(user_encrypt_input)
        y_offset = 130
        for i, step in enumerate(steps):
            # Use wrapped text to prevent horizontal overflow
            lines_used = draw_wrapped_text(screen, step, FONT, (255,255,255), 80, y_offset, WIDTH - 160)
            y_offset += lines_used * (FONT.get_height() + 4)
        continue_btn.draw(screen)

    elif state == "encrypt_game":
        angle += 0.05            
        dx = math.sin(angle) * 30
        SURFER_BASE_X = WIDTH//2 - 160 
        # Rotate the surfer image based on the angle
        rotated_surfer = pygame.transform.rotate(surfer_img, math.sin(angle) * 15)
        # Adjust the position to account for rotation
        surfer_rect = rotated_surfer.get_rect(center=(SURFER_BASE_X + dx, 300 + surfer_img.get_height()//2))
        screen.blit(rotated_surfer, surfer_rect)
        title = BIG_FONT.render(f"Lives: {lives}  Score: {score}", True, (255, 255, 255))
        screen.blit(title, (30, 30))
        if current_question < len(MCQ_QUESTIONS):
            q = MCQ_QUESTIONS[current_question]
            y_offset = 100
            # Wrap the question text
            lines_used = draw_wrapped_text(screen, q["question"], FONT, (255,255,255), 80, y_offset, WIDTH - 160)
            y_offset += lines_used * (FONT.get_height() + 4) + 20
            choice_w = 420
            choice_x = WIDTH - choice_w - 100
            spacing = 24
            mouse_pos = pygame.mouse.get_pos()
            btn_rects = []
            for i, choice in enumerate(q["choices"]):
                # Calculate wrapped lines for this choice
                lines = count_wrapped_lines(choice, FONT, choice_w - 20)
                choice_h = lines * (FONT.get_height() + 4) + 20
                btn_rect = pygame.Rect(choice_x, y_offset, choice_w, choice_h)
                btn_rects.append(btn_rect)
                btn_color = (44, 125, 160) if i%2==0 else (1, 79, 134)
                border_col = (0,0,0)
                hovered = btn_rect.collidepoint(mouse_pos)
                if hovered:
                    btn_color = (min(btn_color[0]+30, 255), min(btn_color[1]+30, 255), min(btn_color[2]+30, 255))
                    pygame.draw.rect(screen, (255,255,255), btn_rect, 2, border_radius=8)
                pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
                pygame.draw.rect(screen, border_col, btn_rect, 3, border_radius=8)
                # Wrap the choice text as well
                draw_wrapped_text(screen, choice, FONT, (255,255,255), btn_rect.x + 10, btn_rect.y + 10, choice_w - 20)
                y_offset += choice_h + spacing
        else:
            done_surf = FONT.render("No more questions!", True, (255,255,255))
            screen.blit(done_surf, (WIDTH//2 - done_surf.get_width()//2, 300))

    elif state == "step_explanation":
        # Show what happened to the string at this step
        title = BIG_FONT.render(f"Step {step_to_show + 1} Explanation", True, (204, 51, 255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        y_offset = 180
        LEFT_MARGIN = 80
        MAX_WIDTH = WIDTH - 160
        for line in step_explanation_text:
            if is_code_line(line):
                y_offset += render_code_line(screen, line, FONT, (173,216,230), LEFT_MARGIN, y_offset, MAX_WIDTH)
            else:
                lines_used = draw_wrapped_text(screen, line, FONT, (173,216,230), LEFT_MARGIN, y_offset, MAX_WIDTH)
                y_offset += lines_used * (FONT.get_height() + 4)
        # Show instruction to press space
        instr = FONT.render("Press SPACE to continue", True, (200, 200, 255))
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 520))

    elif state == "game_over":
        # Only show 'Game Over' if user lost (lives == 0)
        if lives == 0:
            title = BIG_FONT.render("Game Over", True, (204, 51, 255))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        # Show 'You Won!' if all answers were correct
        if score == len(MCQ_QUESTIONS):
            win_msg = BIG_FONT.render("You Won!", True, (80, 255, 80))
            screen.blit(win_msg, (WIDTH//2 - win_msg.get_width()//2, 180))
        elif game_over_message:
            msg = FONT.render(game_over_message, True, (255, 255, 255))
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 200))
        summary = FONT.render(f"Your text was: {user_encrypt_input}", True, (173, 216, 230))
        screen.blit(summary, (WIDTH//2 - summary.get_width()//2, 300))
        restart_btn.draw(screen)
        quit_btn.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()