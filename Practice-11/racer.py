import pygame
import sys
import random
import time
from pygame.locals import *

# Initialize pygame
pygame.init()

# -----------------------------
# Basic game settings
# -----------------------------
FPS = 60
FramePerSec = pygame.time.Clock()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

PLAYER_SPEED = 5
ENEMY_SPEED = 5

# After every N collected coins, enemy speed increases
SPEED_UP_EVERY = 5
SPEED_INCREASE = 1

# Counters
coins_collected = 0      # How many coins the player collected
coin_score = 0           # Total score based on coin weights

# -----------------------------
# Colors
# -----------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 215, 0)
ORANGE = (255, 165, 0)
GREEN = (0, 200, 0)

# -----------------------------
# Screen and fonts
# -----------------------------
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

font_big = pygame.font.SysFont("Verdana", 55)
font_small = pygame.font.SysFont("Verdana", 18)
coin_font = pygame.font.SysFont("Verdana", 14)

game_over = font_big.render("Game Over", True, BLACK)


# -----------------------------
# Helper function for images
# -----------------------------

background = pygame.image.load("/Users/zere/Desktop/Lectures01/PP2/race/images/racer_bg.jpg").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# -----------------------------
# Enemy class
# -----------------------------
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load enemy image or use a red rectangle
        self.image = pygame.image.load("/Users/zere/Desktop/Lectures01/PP2/race/images/Car_Enemy.png")
        self.image = pygame.transform.scale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

        # Start enemy at a random x-position
        self.reset_position()

    def reset_position(self):
        """Places the enemy at the top of the screen randomly."""
        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-120, -40)
        )

    def move(self):
        """Moves the enemy downward."""
        self.rect.move_ip(0, ENEMY_SPEED)

        # If enemy leaves the screen, reset it to the top
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_position()


# -----------------------------
# Player class
# -----------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Load player image or use a green rectangle
        self.image = pygame.image.load("/Users/zere/Desktop/Lectures01/PP2/race/images/Car_Player.png")
        self.image = pygame.transform.scale(self.image, (50, 100))

        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)

        # Starting position of the player
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 70)

    def move(self):
        """Moves the player left and right using arrow keys."""
        pressed_keys = pygame.key.get_pressed()

        # Move left, but do not leave the screen
        if pressed_keys[K_LEFT] and self.rect.left > 0:
            self.rect.move_ip(-PLAYER_SPEED, 0)

        # Move right, but do not leave the screen
        if pressed_keys[K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(PLAYER_SPEED, 0)


# -----------------------------
# Coin class
# -----------------------------
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Coin will receive random weight and position
        self.weight = 1
        self.image = None
        self.rect = None

        self.reset_coin()

    def create_coin_image(self):
        """
        Creates a coin image based on its weight.
        Bigger weight = bigger coin and different color.
        """
        if self.weight == 1:
            radius = 12
            color = YELLOW
        elif self.weight == 2:
            radius = 15
            color = ORANGE
        else:
            radius = 18
            color = GREEN

        size = radius * 2
        image = pygame.Surface((size, size), pygame.SRCALPHA)

        # Draw the coin circle
        pygame.draw.circle(image, color, (radius, radius), radius)

        # Draw the weight number inside the coin
        text = coin_font.render(str(self.weight), True, BLACK)
        text_rect = text.get_rect(center=(radius, radius))
        image.blit(text, text_rect)

        return image

    def reset_coin(self):
        """
        Randomly chooses coin weight and places it above the screen.
        The coin will then fall down the road.
        """
        self.weight = random.choice([1, 2, 3])
        self.image = self.create_coin_image()
        self.rect = self.image.get_rect()

        self.rect.center = (
            random.randint(40, SCREEN_WIDTH - 40),
            random.randint(-300, -40)
        )

    def move(self):
        """Moves the coin downward."""
        self.rect.move_ip(0, 4)

        # If coin leaves the screen, create a new random coin
        if self.rect.top > SCREEN_HEIGHT:
            self.reset_coin()


# -----------------------------
# Create objects
# -----------------------------
P1 = Player()
E1 = Enemy()

# Groups help us draw and check collisions easily
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()

# Create several coins on the road
for i in range(3):
    coin = Coin()
    coins.add(coin)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)

for coin in coins:
    all_sprites.add(coin)


# -----------------------------
# Helper function for top-right text
# -----------------------------
def draw_text_top_right(text, y):
    """
    Draws text in the top right corner.
    y controls vertical position.
    """
    surface = font_small.render(text, True, BLACK)
    x = SCREEN_WIDTH - surface.get_width() - 10
    DISPLAYSURF.blit(surface, (x, y))


# -----------------------------
# Game loop
# -----------------------------
while True:
    # Check all events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))

    # Move player, enemy, and coins
    P1.move()
    E1.move()

    for coin in coins:
        coin.move()

    # -----------------------------
    # Coin collision
    # -----------------------------
    old_coin_count = coins_collected

    # Check if player touches any coin
    touched_coins = pygame.sprite.spritecollide(P1, coins, False)

    for coin in touched_coins:
        coins_collected += 1
        coin_score += coin.weight

        # After collection, the coin appears again randomly
        coin.reset_coin()

    # Increase enemy speed after every N collected coins
    old_level = old_coin_count // SPEED_UP_EVERY
    new_level = coins_collected // SPEED_UP_EVERY

    if new_level > old_level:
        ENEMY_SPEED += SPEED_INCREASE

    # -----------------------------
    # Draw all sprites
    # -----------------------------
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)

    # -----------------------------
    # Draw score in the top right corner
    # -----------------------------
    draw_text_top_right(f"Coins: {coins_collected}", 10)
    draw_text_top_right(f"Score: {coin_score}", 35)
    draw_text_top_right(f"Enemy speed: {ENEMY_SPEED}", 60)

    # -----------------------------
    # Enemy collision = Game Over
    # -----------------------------
    if pygame.sprite.spritecollideany(P1, enemies):
        time.sleep(0.5)

        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))

        pygame.display.update()
        time.sleep(2)

        pygame.quit()
        sys.exit()

    pygame.display.update()
    FramePerSec.tick(FPS)