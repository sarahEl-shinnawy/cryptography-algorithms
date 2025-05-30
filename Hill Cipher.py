import pygame
import sys
import random
import numpy as np
import cv2

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hill Cipher Challenge")

# Add image background setup
bg_image_path = r"C:\Users\sarah\Desktop\CryptographyProjectFINAL\cryptography-algorithms\3139256.jpg"
bg_image = pygame.image.load(bg_image_path)
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Fonts
try:
    FONT = pygame.font.SysFont('Consolas', 26)
    BIG_FONT = pygame.font.SysFont('Consolas', 36)
    SMALL_FONT = pygame.font.SysFont('Consolas', 16)
    STEP_FONT = pygame.font.SysFont('Consolas', 18)
    MATRIX_FONT = pygame.font.SysFont('Consolas', 20)
except:
    # Fallback to default font if Consolas is not available
    FONT = pygame.font.Font(None, 26)
    BIG_FONT = pygame.font.Font(None, 36)
    SMALL_FONT = pygame.font.Font(None, 16)
    STEP_FONT = pygame.font.Font(None, 18)
    MATRIX_FONT = pygame.font.Font(None, 20)

# Colors
WHITE = (255, 255, 255)
BLACK = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
BUTTON_HOVER = (180, 180, 180)
BUTTON_ACTIVE = (150, 150, 150)

# Hill cipher key matrix
KEY_MATRIX = np.array([[3, 3], [2, 5]])

def get_video_frame():
    return None

def text_to_numbers(text):
    return [ord(c.lower()) - ord('a') for c in text if c.isalpha()]

def numbers_to_text(numbers):
    return ''.join([chr(n % 26 + ord('a')) for n in numbers])

def draw_matrix(matrix, x, y, surface=None, cell_size=50, highlight_cells=None):
    if surface is None:
        surface = screen
        
    rows, cols = matrix.shape
    if highlight_cells is None:
        highlight_cells = []
    
    for i in range(rows):
        for j in range(cols):
            rect = pygame.Rect(x + j * cell_size, y + i * cell_size, cell_size, cell_size)
            
            if (i, j) in highlight_cells:
                pygame.draw.rect(surface, LIGHT_BLUE, rect)
            
            pygame.draw.rect(surface, WHITE, rect, 1)
            num = MATRIX_FONT.render(str(matrix[i, j]), True, WHITE)
            surface.blit(num, (x + j * cell_size + (cell_size - num.get_width()) // 2, 
                             y + i * cell_size + (cell_size - num.get_height()) // 2))

def encrypt_hill(text):
    text = ''.join([c for c in text if c.isalpha()])
    if len(text) % 2 != 0:
        text += 'x'
    
    result = []
    steps = []
    steps.append(("Key Matrix:", "This is our encryption key"))
    steps.append(("matrix", KEY_MATRIX))
    
    for i in range(0, len(text), 2):
        pair = text[i:i+2]
        vec = np.array([[ord(pair[0]) - ord('a')], [ord(pair[1]) - ord('a')]])
        
        steps.append((f"Convert '{pair.upper()}' to numbers:", 
                     f"A=0, B=1, ..., Z=25 → [{vec[0][0]}, {vec[1][0]}]"))
        
        steps.append(("Matrix multiplication:", 
             f"{KEY_MATRIX[0][0]}×{vec[0][0]} + {KEY_MATRIX[0][1]}×{vec[1][0]} = ?"))
        steps.append(("Matrix multiplication:", 
             f"{KEY_MATRIX[1][0]}×{vec[0][0]} + {KEY_MATRIX[1][1]}×{vec[1][0]} = ?"))
        
        enc = np.dot(KEY_MATRIX, vec)
        
        steps.append(("Calculation results:", 
             f"First element: {enc[0][0]}, Second element: {enc[1][0]}"))
        
        # Detailed modulo steps
        steps.append(("Modulo 26 operation:", 
                    f"First element: {enc[0][0]} mod 26 = {enc[0][0] % 26}"))
        steps.append(("", 
                    f"Second element: {enc[1][0]} mod 26 = {enc[1][0] % 26}"))
        
        enc_mod = enc % 26
        steps.append(("Final encrypted numbers:", 
                     f"[{enc_mod[0][0]}, {enc_mod[1][0]}]"))
        
        result.extend(enc_mod.flatten())
    
    encrypted = numbers_to_text(result)
    return encrypted, steps

def decrypt_hill(encrypted_numbers):
    """Decrypt numbers using Hill cipher and return detailed steps"""
    steps = []
    result = []
    
    # Calculate inverse matrix
    det = int(np.linalg.det(KEY_MATRIX))
    det_inv = pow(det, -1, 26)  # Modular multiplicative inverse
    adj_matrix = np.array([[KEY_MATRIX[1,1], -KEY_MATRIX[0,1]], 
                          [-KEY_MATRIX[1,0], KEY_MATRIX[0,0]]]) % 26
    inv_matrix = (det_inv * adj_matrix) % 26
    
    steps.append(("Key Matrix:", "This is our decryption key (inverse of encryption key)"))
    steps.append(("matrix", inv_matrix))
    
    for i in range(0, len(encrypted_numbers), 2):
        pair = encrypted_numbers[i:i+2]
        vec = np.array([[pair[0]], [pair[1]]])
        
        steps.append((f"Convert encrypted pair to vector:", 
                     f"[{vec[0][0]}, {vec[1][0]}]"))
        
        steps.append(("Matrix multiplication:", 
             f"{inv_matrix[0][0]}×{vec[0][0]} + {inv_matrix[0][1]}×{vec[1][0]} = ?"))
        steps.append(("Matrix multiplication:", 
             f"{inv_matrix[1][0]}×{vec[0][0]} + {inv_matrix[1][1]}×{vec[1][0]} = ?"))
        
        dec = np.dot(inv_matrix, vec)
        
        steps.append(("Calculation results:", 
             f"First element: {dec[0][0]}, Second element: {dec[1][0]}"))
        
        # Detailed modulo steps
        steps.append(("Modulo 26 operation:", 
                     f"First element: {dec[0][0]} mod 26 = {dec[0][0] % 26}"))
        steps.append(("", 
                     f"Second element: {dec[1][0]} mod 26 = {dec[1][0] % 26}"))
        
        dec_mod = dec % 26
        steps.append(("Final decrypted numbers:", 
                     f"[{dec_mod[0][0]}, {dec_mod[1][0]}]"))
        
        result.extend(dec_mod.flatten())
    
    return numbers_to_text(result), steps

def generate_choices(encrypted_word):
    encrypted = encrypted_word.lower()
    choices = []
    
    for i in range(3):
        pos = random.randint(0, len(encrypted)-1)
        delta = random.choice([1, -1, 2, -2])
        new_char = chr((ord(encrypted[pos]) - ord('a') + delta) % 26 + ord('a'))
        wrong = encrypted[:pos] + new_char + encrypted[pos+1:]
        choices.append(wrong)
    
    choices.append(encrypted)
    random.shuffle(choices)
    return choices

class Button:
    def __init__(self, text, x, y, w, h, callback, color=GRAY, text_color=WHITE, border_color=WHITE):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback
        self.is_hovered = False
        self.is_active = False
        self.color = color
        self.text_color = text_color
        self.border_color = border_color

    def draw(self, screen):
        color = BUTTON_ACTIVE if self.is_active else BUTTON_HOVER if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=5)
        txt = FONT.render(self.text, True, self.text_color)
        screen.blit(txt, (self.rect.x + (self.rect.w - txt.get_width()) // 2, 
                         self.rect.y + (self.rect.h - txt.get_height()) // 2))

    def handle_event(self, event):
        self.is_hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered:
            self.is_active = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_active and self.is_hovered:
                self.callback()
            self.is_active = False

# Game states
state = "main_menu"
user_input = ""
encrypted_word = ""
encryption_steps = []
decryption_steps = []
choices = []
choice_buttons = []
result_message = ""
original_word = ""
scroll_offset = 0
max_scroll = 0
target_scroll_offset = 0
scroll_speed = 0.2
main_menu_buttons = []
current_mode = ""

def init_main_menu_buttons():
    global main_menu_buttons
    button_width = 200  # smaller
    button_height = 60  # smaller
    button_spacing = 22 # slightly smaller spacing
    start_y = HEIGHT//2 + 30 # shift down
    
    # Create encryption button (color: #1a759f)
    encryption_btn = Button("Encryption", WIDTH//2 - button_width//2, start_y, 
                          button_width, button_height, start_encryption, (26, 117, 159), WHITE, (26, 117, 159))
    
    # Create decryption button (color: #52b69a)
    decryption_btn = Button("Decryption", WIDTH//2 - button_width//2, start_y + button_height + button_spacing,
                          button_width, button_height, start_decryption, (82, 182, 154), WHITE, (82, 182, 154))
    
    # Create quit button (color: #b5179e)
    quit_btn = Button("Quit", WIDTH//2 - button_width//2, start_y + 2*(button_height + button_spacing),
                     button_width, button_height, quit_game, (181, 23, 158), WHITE, (181, 23, 158))
    
    main_menu_buttons = [encryption_btn, decryption_btn, quit_btn]

def show_result(is_correct):
    global state, result_message
    result_message = "CORRECT!" if is_correct else "INCORRECT"
    state = "result"

def start_encryption():
    global state, user_input, encrypted_word, encryption_steps, choices, original_word, scroll_offset, current_mode
    user_input = ""
    encrypted_word = ""
    encryption_steps = []
    choices = []
    original_word = ""
    scroll_offset = 0
    current_mode = "encryption"
    state = "input"

def start_decryption():
    global state, encrypted_word, encryption_steps, decryption_steps, choices, original_word, scroll_offset, choice_buttons, current_mode
    current_mode = "decryption"
    # Generate a random word
    original_word = generate_random_word(4)  # 4-letter word
    # Encrypt it to get the encrypted text
    encrypted_word, _ = encrypt_hill(original_word)
    # Get decryption steps
    _, decryption_steps = decrypt_hill(text_to_numbers(encrypted_word))
    # Generate wrong choices
    choices = []
    for _ in range(3):
        wrong = generate_random_word(len(original_word))
        while wrong == original_word or wrong in choices:
            wrong = generate_random_word(len(original_word))
        choices.append(wrong)
    choices.append(original_word)
    random.shuffle(choices)
    # Reset scroll and set state
    scroll_offset = 0
    target_scroll_offset = 0
    # Create choice buttons
    choice_buttons = []
    for i, choice in enumerate(choices):
        # Alternate button colors
        if i % 2 == 0:
            btn_color = (44, 125, 160)  # #2c7da0
            border_color = (20, 70, 90)  # darker shade
        else:
            btn_color = (1, 79, 134)    # #014f86
            border_color = (0, 40, 70)  # darker shade
        def make_callback(c=choice):  # Capture choice as default argument
            return lambda: show_result(c.lower() == original_word.lower())
        btn = Button(choice.upper(), WIDTH - 400, 200 + i*70, 250, 60, make_callback(), btn_color, WHITE, border_color)
        choice_buttons.append(btn)
    state = "decrypt_question"

def show_question():
    global state, choice_buttons
    choice_buttons = []
    for i, choice in enumerate(choices):
        # Alternate button colors
        if i % 2 == 0:
            btn_color = (44, 125, 160)  # #2c7da0
            border_color = (20, 70, 90)  # darker shade
        else:
            btn_color = (1, 79, 134)    # #014f86
            border_color = (0, 40, 70)  # darker shade
        def make_callback(c=choice):
            return lambda: show_result(c == encrypted_word)
        btn = Button(choice.upper(), WIDTH - 400, 200 + i*70, 250, 60, make_callback(), btn_color, WHITE, border_color)
        choice_buttons.append(btn)
    state = "question"

def generate_random_word(length=4):
    """Generate a random word of given length (default 4 letters)"""
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))

def quit_game():
    pygame.quit()
    sys.exit()

def create_vertical_gradient(width, height, color=(0, 0, 0), alpha_start=180, alpha_end=0):
    """Create a vertical gradient surface from color with alpha_start to alpha_end."""
    gradient = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(height):
        alpha = int(alpha_start + (alpha_end - alpha_start) * (y / height))
        pygame.draw.line(gradient, (*color, alpha), (0, y), (width, y))
    return gradient

# Create a black-to-transparent vertical gradient overlay
# Make the gradient darker by increasing alpha_start
gradient_overlay = create_vertical_gradient(WIDTH, HEIGHT, color=(0, 0, 0), alpha_start=230, alpha_end=0)

# Initialize main menu buttons after all functions are defined
init_main_menu_buttons()

# Main game loop
clock = pygame.time.Clock()
running = True

# Use a brighter purple for the title
BRIGHT_PURPLE = (204, 51, 255)

while running:
    # Draw the image background at the start of each frame
    screen.blit(bg_image, (0, 0))
    # Draw the gradient overlay
    screen.blit(gradient_overlay, (0, 0))

    # Smooth scrolling
    if state in ["steps", "question", "decrypt_question"]:
        scroll_offset += (target_scroll_offset - scroll_offset) * scroll_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if state == "main_menu":
            for btn in main_menu_buttons:
                btn.handle_event(event)
        
        elif state == "input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cleaned_input = ''.join([c for c in user_input if c.isalpha()])
                    if len(cleaned_input) < 2:
                        pass
                    else:
                        original_word = cleaned_input
                        encrypted_word, encryption_steps = encrypt_hill(cleaned_input)
                        choices = generate_choices(encrypted_word)
                        show_question()
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isalpha():
                    user_input += event.unicode
        
        if state in ["steps", "question", "decrypt_question"] and event.type == pygame.MOUSEWHEEL:
            target_scroll_offset -= event.y * 10
            target_scroll_offset = max(0, min(target_scroll_offset, max_scroll))
        
        for btn in choice_buttons:
            btn.handle_event(event)
        
        if state == "result" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if current_mode == "encryption":
                    start_encryption()
                else:
                    start_decryption()
            elif event.key == pygame.K_q:
                state = "main_menu"

    # Draw states
    if state == "main_menu":
        # Draw title
        title = BIG_FONT.render("Hill Cipher", True, BRIGHT_PURPLE)
        subtitle = FONT.render("Encryption and Decryption Challenge", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 60))
        
        # Draw main menu buttons
        for btn in main_menu_buttons:
            btn.draw(screen)
    
    elif state == "input":
        title = FONT.render("Enter text to encrypt (letters only, min 2):", True, WHITE)
        # Draw a text box
        box_width = 400
        box_height = 60
        box_x = WIDTH//2 - box_width//2
        box_y = 150
        pygame.draw.rect(screen, (30, 30, 30), (box_x, box_y, box_width, box_height), border_radius=8)  # dark background
        pygame.draw.rect(screen, BLUE, (box_x, box_y, box_width, box_height), 3, border_radius=8)  # blue border
        input_text = FONT.render(user_input.upper(), True, BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        # Show placeholder if empty
        if not user_input:
            placeholder = SMALL_FONT.render("Type here...", True, (120, 120, 120))
            screen.blit(placeholder, (box_x + 15, box_y + (box_height - placeholder.get_height())//2))
        else:
            screen.blit(input_text, (box_x + 15, box_y + (box_height - input_text.get_height())//2))
        
        if len(''.join([c for c in user_input if c.isalpha()])) < 2 and user_input:
            error = FONT.render("Please enter at least 2 letters", True, RED)
            screen.blit(error, (WIDTH//2 - error.get_width()//2, box_y + box_height + 20))
    
    elif state in ["steps", "question", "decrypt_question"]:
        # Draw dividing line
        pygame.draw.line(screen, WHITE, (WIDTH - 480, 0), (WIDTH - 480, HEIGHT), 2)
        
        # Left side: Steps
        steps_title = FONT.render("Decryption Steps:" if state == "decrypt_question" else "Encryption Steps:", True, PURPLE)
        screen.blit(steps_title, (50, 30))
        
        # Scrollable content area for left side
        content_area = pygame.Rect(50, 70, WIDTH-530, HEIGHT-100)
        # Create a transparent surface for content
        content_surface = pygame.Surface((content_area.width, content_area.height), pygame.SRCALPHA)
        # Do NOT fill the surface, keep it transparent
        
        # Select correct steps to show
        steps_to_show = decryption_steps if state == "decrypt_question" else encryption_steps
        
        # Calculate total content height for scrolling
        total_height = 0
        for step in steps_to_show:
            if isinstance(step[0], str) and step[0].endswith(":"):
                total_height += 50
            elif step[0] == "matrix":
                total_height += 120
            else:
                total_height += 55 if step[0] else 30
        
        # Update max scroll value
        max_scroll = max(0, total_height - content_area.height)
        target_scroll_offset = max(0, min(target_scroll_offset, max_scroll))
        
        # Draw steps on content surface
        y_pos = -scroll_offset
        
        for step in steps_to_show:
            if isinstance(step[0], str) and step[0].endswith(":"):
                header = STEP_FONT.render(step[0], True, BLUE)
                detail = SMALL_FONT.render(step[1], True, WHITE)
                if y_pos + 50 > 0 and y_pos < content_area.height:  # Only render if visible
                    content_surface.blit(header, (0, y_pos))
                    content_surface.blit(detail, (20, y_pos + 25))
                y_pos += 50
            elif step[0] == "matrix":
                if y_pos + 120 > 0 and y_pos < content_area.height:  # Only render if visible
                    draw_matrix(step[1], 0, y_pos, content_surface)
                    hint = SMALL_FONT.render("Remember: A=0, B=1, C=2, ..., Z=25", True, WHITE)
                    content_surface.blit(hint, (110, y_pos + 30))
                y_pos += 120
            else:
                if step[0]:
                    header = STEP_FONT.render(step[0], True, WHITE)
                    if y_pos + 25 > 0 and y_pos < content_area.height:  # Only render if visible
                        content_surface.blit(header, (0, y_pos))
                    y_pos += 25
                detail = SMALL_FONT.render(step[1], True, WHITE)
                if y_pos + 30 > 0 and y_pos < content_area.height:  # Only render if visible
                    content_surface.blit(detail, (20, y_pos))
                y_pos += 30
        
        # Draw content surface to screen
        screen.blit(content_surface, (content_area.x, content_area.y))
        
        # Draw scroll indicators if content is scrollable
        if max_scroll > 0:
            if scroll_offset > 0:  # Show up arrow
                pygame.draw.polygon(screen, WHITE, [
                    (content_area.x + content_area.width - 20, content_area.y + 10),
                    (content_area.x + content_area.width - 10, content_area.y + 20),
                    (content_area.x + content_area.width - 30, content_area.y + 20)
                ])
            if scroll_offset < max_scroll:  # Show down arrow
                pygame.draw.polygon(screen, WHITE, [
                    (content_area.x + content_area.width - 20, content_area.y + content_area.height - 10),
                    (content_area.x + content_area.width - 10, content_area.y + content_area.height - 20),
                    (content_area.x + content_area.width - 30, content_area.y + content_area.height - 20)
                ])
        
        # Right side
        if state == "decrypt_question":
            question = FONT.render("What was the original text?", True, WHITE)
            screen.blit(question, (WIDTH - 450, 100))
            
            encrypted_text = FONT.render(f"Encrypted text: {encrypted_word.upper()}", True, BLUE)
            screen.blit(encrypted_text, (WIDTH - 450, 150))
        else:
            question = FONT.render("Select the encrypted result:", True, WHITE)
            screen.blit(question, (WIDTH - 450, 150))
        
        # Draw choice buttons
        for btn in choice_buttons:
            btn.draw(screen)
    
    elif state == "result":
        color = GREEN if result_message == "CORRECT!" else RED
        result_text = BIG_FONT.render(result_message, True, color)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 100))
        
        orig_text = FONT.render(f"Original text: {original_word.upper()}", True, WHITE)
        enc_text = FONT.render(f"Encrypted result: {encrypted_word.upper()}", True, BLUE)
        screen.blit(orig_text, (WIDTH//2 - orig_text.get_width()//2, 180))
        screen.blit(enc_text, (WIDTH//2 - enc_text.get_width()//2, 230))
        
        instr = FONT.render("Press R to restart or Q to quit", True, WHITE)
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 500))
    
    pygame.display.flip()
    clock.tick(30)  # 30 FPS is good for video playback

# Cleanup
pygame.quit()
sys.exit()