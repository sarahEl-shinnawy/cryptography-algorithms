
import pygame
import random
import string
import time

# Initialize Pygame library
pygame.init()

# Screen dimensions and setup
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DES Memory Decrypt")
clock = pygame.time.Clock()  # Controls game frame rate

# Font settings for game text
FONT = pygame.font.Font(None, 48)  # Main font for cards
SMALL_FONT = pygame.font.Font(None, 32)  # Smaller font for UI
LARGE_FONT = pygame.font.Font(None, 72)  # For game over message

# Color definitions
WHITE = (255, 255, 255)  # Background
GRAY = (200, 200, 200)  # Card back
DARK_GRAY = (100, 100, 100)  # Revealed card
BLACK = (0, 0, 0)  # Text and borders
GREEN = (0, 200, 0)  # Correct matches
RED = (200, 0, 0)  # Timer and game over
BLUE = (0, 100, 255)  # Button highlight

# Game configuration
WORDS = ["HELLO", "WORLD", "PYTHON", "GAMES", "MEMORY", "CIPHER", "DECODE", "SECRET", "PUZZLE", "CRYPTO", "PIZZA", "ALGORITHIM", "CAKE"]
GRID_SIZE = 4  # 4x4 grid of cards
CARD_SIZE = 100  # Size of each card in pixels
MARGIN = 20  # Space between cards
DELAY_FLIP_BACK = 700  # Time cards stay revealed (milliseconds)
GAME_DURATION = 60  # 60 seconds game duration

class Card:
    """Represents a single card in the memory game"""
    def __init__(self, x, y, letter):
        # Card position and size
        self.rect = pygame.Rect(x, y, CARD_SIZE, CARD_SIZE)
        self.letter = letter  # The character displayed on the card
        self.revealed = False  # Temporarily shown
        self.permanently_revealed = False  # Correct match stays shown

    def draw(self, surface):
        """Draw the card on the screen with appropriate state"""
        # Choose color based on card state
        color = GREEN if self.permanently_revealed else DARK_GRAY if self.revealed else GRAY
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Border
        
        # Show letter if card is revealed
        if self.revealed or self.permanently_revealed:
            text = FONT.render(self.letter, True, WHITE)
            surface.blit(text, (
                self.rect.x + CARD_SIZE // 2 - text.get_width() // 2,
                self.rect.y + CARD_SIZE // 2 - text.get_height() // 2
            ))

    def is_clicked(self, pos):
        """Check if card was clicked"""
        return self.rect.collidepoint(pos)

class Button:
    """Interactive button for UI"""
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        """Draw button with hover effect"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        text = SMALL_FONT.render(self.text, True, BLACK)
        surface.blit(text, (
            self.rect.x + self.rect.width // 2 - text.get_width() // 2,
            self.rect.y + self.rect.height // 2 - text.get_height() // 2
        ))

    def check_hover(self, pos):
        """Update hover state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        """Check if button was clicked"""
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos)

def create_card_grid(word):
    """
    Create a grid of cards containing the target word letters and random filler letters
    Returns list of Card objects
    """
    letters = list(word)
    # Add random letters to fill the grid
    extras = random.choices(string.ascii_uppercase, k=GRID_SIZE * GRID_SIZE - len(letters))
    all_letters = letters + extras
    random.shuffle(all_letters)  # Shuffle all letters

    cards = []
    # Create grid layout of cards
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = MARGIN + col * (CARD_SIZE + MARGIN)
            y = MARGIN + row * (CARD_SIZE + MARGIN) + 60  # Offset from top
            letter = all_letters.pop()
            cards.append(Card(x, y, letter))
    return cards

def new_game():
    """Initialize a new game with random word"""
    target_word = random.choice(WORDS)
    scrambled_word = ''.join(random.sample(target_word, len(target_word)))
    cards = create_card_grid(target_word)
    return target_word, scrambled_word, cards, time.time() + GAME_DURATION

# Initialize game state
target_word, scrambled_word, cards, end_time = new_game()
current_index = 0  # Tracks which letter in target word we're looking for
flipped_cards = []  # Cards currently revealed
flip_time = 0  # When cards were flipped
game_won = False  # Game completion state
game_over = False  # Timer ran out

# Create UI buttons on the right side
button_width = 150
button_x = WIDTH - button_width - MARGIN
play_again_button = Button(button_x, HEIGHT - 120, button_width, 40, "Restart", GRAY, BLUE)
quit_button = Button(button_x, HEIGHT - 60, button_width, 40, "Quit", GRAY, BLUE)

# Main game loop
running = True
while running:
    screen.fill(WHITE)
    now = pygame.time.get_ticks() / 1000  # Current time in seconds
    remaining_time = max(0, end_time - now)
    mouse_pos = pygame.mouse.get_pos()  # Current mouse position

    # Check if time ran out
    if remaining_time <= 0 and not game_won and not game_over:
        game_over = True

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_won and not game_over:
            # Card clicking logic
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Only allow one card flip at a time by checking if no cards are currently flipped
                if not flipped_cards:
                    for card in cards:
                        if card.is_clicked(mouse_pos) and not card.revealed and not card.permanently_revealed:
                            card.revealed = True
                            flipped_cards.append(card)
                            flip_time = pygame.time.get_ticks()
                            break  # Only flip one card per click
        
        # Button handling
        play_again_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if play_again_button.is_clicked(mouse_pos, event):
                # Reset game state
                target_word, scrambled_word, cards, end_time = new_game()
                current_index = 0
                flipped_cards = []
                game_won = False
                game_over = False
            elif quit_button.is_clicked(mouse_pos, event):
                running = False

    # Card flipping logic
    if not game_won and not game_over and flipped_cards and pygame.time.get_ticks() - flip_time > DELAY_FLIP_BACK:
        matched = False
        for card in flipped_cards:
            if card.letter == target_word[current_index]:
                card.permanently_revealed = True  # Keep correct matches shown
                matched = True
            else:
                card.revealed = False  # Hide incorrect cards
        
        if matched:
            current_index += 1
            if current_index >= len(target_word):
                game_won = True
        
        flipped_cards = []  # Reset flipped cards

    # Draw all cards
    for card in cards:
        card.draw(screen)

    # Draw UI elements
    # Scrambled word display
    header = SMALL_FONT.render(f"Find: {scrambled_word}", True, BLACK)
    screen.blit(header, (MARGIN, 10))
    
    # Timer display (red when less than 10 seconds remain)
    timer_color = RED if remaining_time < 10 else BLACK
    timer_text = SMALL_FONT.render(f"Time: {int(remaining_time)}s", True, timer_color)
    screen.blit(timer_text, (WIDTH - timer_text.get_width() - MARGIN, 10))
    
    # Draw buttons (always visible)
    play_again_button.draw(screen)
    quit_button.draw(screen)

    # Game over messages
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        game_over_text = LARGE_FONT.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (
            WIDTH // 2 - game_over_text.get_width() // 2,
            HEIGHT // 2 - game_over_text.get_height() // 2
        ))
        
        progress = SMALL_FONT.render(f"Found: {target_word[:current_index]}", True, WHITE)
        screen.blit(progress, (
            WIDTH // 2 - progress.get_width() // 2,
            HEIGHT // 2 + 50
        ))
    
    if game_won:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        win_text = LARGE_FONT.render("Decryption Complete!", True, GREEN)
        screen.blit(win_text, (
            WIDTH // 2 - win_text.get_width() // 2,
            HEIGHT // 2 - win_text.get_height() // 2
        ))
        
        time_left = SMALL_FONT.render(f"Time remaining: {int(remaining_time)}s", True, WHITE)
        screen.blit(time_left, (
            WIDTH // 2 - time_left.get_width() // 2,
            HEIGHT // 2 + 50
        ))

    pygame.display.flip()  # Update screen
    clock.tick(30)  # Maintain 30 FPS

pygame.quit()  # Clean up