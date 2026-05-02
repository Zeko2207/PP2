import pygame
import random
from dataclasses import dataclass

pygame.init()

# -------------------- SETTINGS --------------------

WIDTH, HEIGHT = 600, 400
CELL_SIZE = 20

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 120, 0)
GRAY = (90, 90, 90)
RED = (220, 50, 50)
BLUE = (60, 160, 255)
YELLOW = (255, 210, 60)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Game speed
START_SPEED = 8
SPEED_INCREASE = 2

# Level increases after this many eaten foods
FOODS_FOR_NEXT_LEVEL = 3


# -------------------- FOOD CLASS --------------------

@dataclass
class Food:
    position: tuple
    weight: int
    color: tuple
    spawn_time: int
    lifetime: int


# -------------------- FUNCTIONS --------------------

def draw_text(text, x, y, color=WHITE):
    """Draw text on the screen."""
    label = font.render(text, True, color)
    screen.blit(label, (x, y))


def draw_walls():
    """Draw border walls around the playing area."""
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.rect(screen, GRAY, (x, 0, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (x, HEIGHT - CELL_SIZE, CELL_SIZE, CELL_SIZE))

    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.rect(screen, GRAY, (0, y, CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, GRAY, (WIDTH - CELL_SIZE, y, CELL_SIZE, CELL_SIZE))


def is_wall_collision(position):
    """Check whether the snake hits the wall."""
    x, y = position

    return (
        x < CELL_SIZE or
        x >= WIDTH - CELL_SIZE or
        y < CELL_SIZE or
        y >= HEIGHT - CELL_SIZE
    )


def generate_food(snake):
    """
    Generate random food position.

    Food cannot appear:
    1. On the wall
    2. On the snake
    """

    free_positions = []

    for x in range(CELL_SIZE, WIDTH - CELL_SIZE, CELL_SIZE):
        for y in range(CELL_SIZE, HEIGHT - CELL_SIZE, CELL_SIZE):
            if (x, y) not in snake:
                free_positions.append((x, y))

    # If there is no free space, return None
    if not free_positions:
        return None

    position = random.choice(free_positions)

    # Different types of food with different weights
    food_types = [
        {"weight": 1, "color": RED, "lifetime": 7000},
        {"weight": 2, "color": BLUE, "lifetime": 5500},
        {"weight": 3, "color": YELLOW, "lifetime": 4000},
    ]

    # Food with bigger weight appears less often
    food_type = random.choices(
        food_types,
        weights=[70, 20, 10],
        k=1
    )[0]

    return Food(
        position=position,
        weight=food_type["weight"],
        color=food_type["color"],
        spawn_time=pygame.time.get_ticks(),
        lifetime=food_type["lifetime"]
    )


def reset_game():
    """Reset all game variables."""

    snake = [
        (WIDTH // 2, HEIGHT // 2),
        (WIDTH // 2 - CELL_SIZE, HEIGHT // 2),
        (WIDTH // 2 - 2 * CELL_SIZE, HEIGHT // 2)
    ]

    direction = (CELL_SIZE, 0)
    next_direction = direction

    score = 0
    level = 1
    speed = START_SPEED
    eaten_foods = 0
    game_over = False

    food = generate_food(snake)

    return snake, direction, next_direction, score, level, speed, eaten_foods, food, game_over


# -------------------- MAIN GAME --------------------

snake, direction, next_direction, score, level, speed, eaten_foods, food, game_over = reset_game()

running = True

while running:
    screen.fill(BLACK)

    # -------------------- EVENTS --------------------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # Restart the game after losing
            if game_over and event.key == pygame.K_r:
                snake, direction, next_direction, score, level, speed, eaten_foods, food, game_over = reset_game()

            if event.key == pygame.K_ESCAPE:
                running = False

            # Change direction.
            # The snake cannot immediately move in the opposite direction.
            if not game_over:
                if event.key == pygame.K_UP and direction != (0, CELL_SIZE):
                    next_direction = (0, -CELL_SIZE)

                elif event.key == pygame.K_DOWN and direction != (0, -CELL_SIZE):
                    next_direction = (0, CELL_SIZE)

                elif event.key == pygame.K_LEFT and direction != (CELL_SIZE, 0):
                    next_direction = (-CELL_SIZE, 0)

                elif event.key == pygame.K_RIGHT and direction != (-CELL_SIZE, 0):
                    next_direction = (CELL_SIZE, 0)

    # -------------------- GAME LOGIC --------------------

    if not game_over:
        direction = next_direction

        head_x, head_y = snake[0]
        dx, dy = direction

        # Create new head position
        new_head = (head_x + dx, head_y + dy)

        # Check collision with wall
        if is_wall_collision(new_head):
            game_over = True

        # Check collision with itself
        elif new_head in snake:
            game_over = True

        else:
            # Add new head to the snake
            snake.insert(0, new_head)

            # Check if snake eats food
            if food is not None and new_head == food.position:
                score += food.weight
                eaten_foods += 1

                # Increase level after eating several foods
                if eaten_foods % FOODS_FOR_NEXT_LEVEL == 0:
                    level += 1
                    speed += SPEED_INCREASE

                food = generate_food(snake)

            else:
                # If food was not eaten, remove tail
                snake.pop()

        # Food disappears after some time
        if food is not None:
            current_time = pygame.time.get_ticks()

            if current_time - food.spawn_time > food.lifetime:
                food = generate_food(snake)

    # -------------------- DRAWING --------------------

    draw_walls()

    # Draw snake
    for i, block in enumerate(snake):
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(screen, color, (block[0], block[1], CELL_SIZE, CELL_SIZE))

    # Draw food
    if food is not None:
        pygame.draw.rect(
            screen,
            food.color,
            (food.position[0], food.position[1], CELL_SIZE, CELL_SIZE)
        )

        # Show food weight on food
        small_font = pygame.font.SysFont("Arial", 16)
        weight_text = small_font.render(str(food.weight), True, BLACK)
        screen.blit(weight_text, (food.position[0] + 6, food.position[1] + 2))

    # Draw score and level counter
    draw_text(f"Score: {score}", 10, 10)
    draw_text(f"Level: {level}", 10, 35)
    draw_text(f"Speed: {speed}", 10, 60)

    # Game over message
    if game_over:
        draw_text("GAME OVER", WIDTH // 2 - 80, HEIGHT // 2 - 30, RED)
        draw_text("Press R to restart", WIDTH // 2 - 95, HEIGHT // 2)

    pygame.display.update()
    clock.tick(speed)

pygame.quit()