
import pygame
import sys
import random
import numpy as np

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 1000, 700  # Increased width for better layout
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hill Cipher Challenge")

# Fonts
FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 48)
SMALL_FONT = pygame.font.Font(None, 24)
STEP_FONT = pygame.font.Font(None, 28)
MATRIX_FONT = pygame.font.Font(None, 32)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (173, 216, 230)
BUTTON_HOVER = (180, 180, 180)
BUTTON_ACTIVE = (150, 150, 150)

# Hill cipher key matrix
KEY_MATRIX = np.array([[3, 3], [2, 5]])

def text_to_numbers(text):
    """Convert text to numerical representation (a=0, b=1, ..., z=25)"""
    return [ord(c.lower()) - ord('a') for c in text if c.isalpha()]

def numbers_to_text(numbers):
    """Convert numbers back to text"""
    return ''.join([chr(n % 26 + ord('a')) for n in numbers])

def draw_matrix(matrix, x, y, cell_size=50, highlight_cells=None):
    """Draw a matrix with optional cell highlighting"""
    rows, cols = matrix.shape
    if highlight_cells is None:
        highlight_cells = []
    
    for i in range(rows):
        for j in range(cols):
            rect = pygame.Rect(x + j * cell_size, y + i * cell_size, cell_size, cell_size)
            
            # Draw highlight if this cell is selected
            if (i, j) in highlight_cells:
                pygame.draw.rect(screen, LIGHT_BLUE, rect)
            
            # Draw cell border and text
            pygame.draw.rect(screen, BLACK, rect, 1)
            num = MATRIX_FONT.render(str(matrix[i, j]), True, BLACK)
            screen.blit(num, (x + j * cell_size + (cell_size - num.get_width()) // 2, 
                             y + i * cell_size + (cell_size - num.get_height()) // 2))

def encrypt_hill(text):
    """Encrypt text using Hill cipher and return detailed steps"""
    text = ''.join([c for c in text if c.isalpha()])  # Remove non-alphabet chars
    if len(text) % 2 != 0:
        text += 'x'  # Add padding if odd length
    
    result = []
    steps = []
    
    # Step 0: Show the key matrix
    steps.append(("Key Matrix:", "This is our encryption key"))
    steps.append(("matrix", KEY_MATRIX)) # Special marker for matrix
    
    for i in range(0, len(text), 2):
        pair = text[i:i+2]
        vec = np.array([[ord(pair[0]) - ord('a')], [ord(pair[1]) - ord('a')]])
        
        # Step 1: Show letter to number conversion
        steps.append((f"Convert '{pair.upper()}' to numbers:", 
                     f"A=0, B=1, ..., Z=25 → [{vec[0][0]}, {vec[1][0]}]"))
        
        # Step 2: Matrix multiplication
        steps.append(("Matrix multiplication:", 
             f"{KEY_MATRIX[0][0]}×{vec[0][0]} + {KEY_MATRIX[0][1]}×{vec[1][0]} = ?"))
        steps.append(("Matrix multiplication:", 
             f"{KEY_MATRIX[1][0]}×{vec[0][0]} + {KEY_MATRIX[1][1]}×{vec[1][0]} = ?"))
        
        # Actual calculation
        enc = np.dot(KEY_MATRIX, vec)
        
        # Step 3: Show calculation results
        steps.append(("Calculation results:", 
             f"First element: {enc[0][0]}, Second element: {enc[1][0]}"))
        
        # Step 4: Mod 26 operation
        enc_mod = enc % 26
        steps.append(("Apply modulo 26:", 
                     f"[{enc[0][0]}, {enc[1][0]}] mod 26 → [{enc_mod[0][0]}, {enc_mod[1][0]}]"))
        
        result.extend(enc_mod.flatten())
    
    encrypted = numbers_to_text(result)
    return encrypted, steps

def generate_choices(encrypted_word):
    """Generate multiple choice options including the correct answer"""
    encrypted = encrypted_word.lower()
    choices = []
    
    # Create wrong answers by modifying the encrypted text
    for i in range(3):
        # Change one character
        pos = random.randint(0, len(encrypted)-1)
        delta = random.choice([1, -1, 2, -2])  # Vary the changes
        new_char = chr((ord(encrypted[pos]) - ord('a') + delta) % 26 + ord('a'))
        wrong = encrypted[:pos] + new_char + encrypted[pos+1:]
        choices.append(wrong)
    
    choices.append(encrypted)  # Add correct answer
    random.shuffle(choices)
    return choices

class Button:
    def __init__(self, text, x, y, w, h, callback, color=GRAY, text_color=BLACK):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.callback = callback
        self.is_hovered = False
        self.is_active = False
        self.color = color
        self.text_color = text_color

    def draw(self, screen):
        color = BUTTON_ACTIVE if self.is_active else BUTTON_HOVER if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=5)
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
state = "menu"
user_input = ""
encrypted_word = ""
encryption_steps = []
choices = []
choice_buttons = []
result_message = ""
original_word = ""
scroll_offset = 0
max_scroll = 0

def start_game():
    global state, user_input, encrypted_word, encryption_steps, choices, original_word, scroll_offset
    user_input = ""
    encrypted_word = ""
    encryption_steps = []
    choices = []
    original_word = ""
    scroll_offset = 0
    state = "input"

def show_question():
    global state, choice_buttons
    choice_buttons = []
    for i, choice in enumerate(choices):
        def make_callback(c=choice):
            return lambda: show_result(c == encrypted_word)
        btn_color = LIGHT_BLUE if i % 2 == 0 else GRAY
        btn = Button(choice.upper(), WIDTH - 400, 200 + i*70, 250, 60, make_callback(), btn_color)
        choice_buttons.append(btn)
    state = "question"

def show_result(is_correct):
    global state, result_message
    result_message = "CORRECT!" if is_correct else "INCORRECT"
    state = "result"

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Handle input state
        if state == "input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    cleaned_input = ''.join([c for c in user_input if c.isalpha()])
                    if len(cleaned_input) < 2:
                        pass  # Error handled in drawing
                    else:
                        original_word = cleaned_input
                        encrypted_word, encryption_steps = encrypt_hill(cleaned_input)
                        choices = generate_choices(encrypted_word)
                        show_question()
                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.unicode.isalpha():
                    user_input += event.unicode
        
        # Handle scrolling
        if state in ["steps", "question"] and event.type == pygame.MOUSEWHEEL:
            scroll_offset -= event.y * 10
            scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        # Handle buttons
        if state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if WIDTH//2 - 100 <= event.pos[0] <= WIDTH//2 + 100 and HEIGHT//2 <= event.pos[1] <= HEIGHT//2 + 50:
                    start_game()
        
        for btn in choice_buttons:
            btn.handle_event(event)
        
        if state == "result" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                start_game()
            elif event.key == pygame.K_q:
                running = False
    
    # Draw current state
    if state == "menu":
        title = BIG_FONT.render("Hill Cipher Challenge", True, BLACK)
        subtitle = FONT.render("Decrypt the message using the steps shown", True, BLACK)
        start_btn = Button("Start Game", WIDTH//2 - 100, HEIGHT//2, 200, 50, start_game)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 180))
        start_btn.draw(screen)
    
    elif state == "input":
        title = FONT.render("Enter text to encrypt (letters only, min 2):", True, BLACK)
        input_text = FONT.render(user_input.upper(), True, BLUE)
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(input_text, (WIDTH//2 - input_text.get_width()//2, 150))
        
        if len(''.join([c for c in user_input if c.isalpha()])) < 2 and user_input:
            error = FONT.render("Please enter at least 2 letters", True, RED)
            screen.blit(error, (WIDTH//2 - error.get_width()//2, 200))
    
    elif state in ["steps", "question"]:
        # Draw dividing line
        pygame.draw.line(screen, BLACK, (WIDTH - 480, 0), (WIDTH - 480, HEIGHT), 2)
        
        # Left side: Steps
        steps_title = FONT.render("Encryption Steps:", True, PURPLE)
        screen.blit(steps_title, (50, 30))
        y_pos = 70 - scroll_offset
        

        # Calculate total height needed for all steps and max scroll
        total_height = 0
        for step in encryption_steps:
            if isinstance(step[0], str) and step[0].endswith(":"):
                total_height += 50
            elif step[0] == "matrix":
                total_height += 120
            else:
                total_height += 55 if step[0] else 30
        
        max_scroll = max(0, total_height - 400)  # 400 is roughly the visible area height
        scroll_offset = max(0, min(scroll_offset, max_scroll))
        
        # Show all steps with scrolling
        y_pos = 70
        for step in encryption_steps:
            visible_y = y_pos - scroll_offset + 70
            
            # Only render if this step is visible on screen
            if visible_y + 120 > 0 and visible_y < HEIGHT:  # 120 is max step height
                if isinstance(step[0], str) and step[0].endswith(":"):
                    # Header step
                    header = STEP_FONT.render(step[0], True, BLUE)
                    detail = SMALL_FONT.render(step[1], True, BLACK)
                    screen.blit(header, (50, visible_y))
                    screen.blit(detail, (70, visible_y + 25))
                    y_pos += 50
                elif step[0] == "matrix":
                    # Matrix display
                    draw_matrix(step[1], 50, visible_y)
                    hint = SMALL_FONT.render("Remember: A=0, B=1, C=2, ..., Z=25", True, BLACK)
                    screen.blit(hint, (160, visible_y + 30))
                    y_pos += 120
                else:
                    # Regular step
                    if step[0]:  # If there's a header
                        header = STEP_FONT.render(step[0], True, BLACK)
                        screen.blit(header, (50, visible_y))
                        y_pos += 25
                    detail = SMALL_FONT.render(step[1], True, BLACK)
                    screen.blit(detail, (70, visible_y))
                    y_pos += 30
            else:
                # Still need to account for the height even if not visible
                if isinstance(step[0], str) and step[0].endswith(":"):
                    y_pos += 50
                elif step[0] == "matrix":
                    y_pos += 120
                else:
                    y_pos += 55 if step[0] else 30
        
        # Right side: Choices (only in question state)
        if state == "question":
            question = FONT.render("Select the encrypted result:", True, BLACK)
            screen.blit(question, (WIDTH - 450, 150))
            
            for btn in choice_buttons:
                btn.draw(screen)
    
    elif state == "result":
        # Show result
        color = GREEN if result_message == "CORRECT!" else RED
        result_text = BIG_FONT.render(result_message, True, color)
        screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, 100))
        
        # Show original and encrypted
        orig_text = FONT.render(f"Original text: {original_word.upper()}", True, BLACK)
        enc_text = FONT.render(f"Encrypted result: {encrypted_word.upper()}", True, BLUE)
        screen.blit(orig_text, (WIDTH//2 - orig_text.get_width()//2, 180))
        screen.blit(enc_text, (WIDTH//2 - enc_text.get_width()//2, 230))
        
        # Show instructions
        instr = FONT.render("Press R to restart or Q to quit", True, BLACK)
        screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 500))
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()

