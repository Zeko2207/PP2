"""Main Pygame UI and Snake gameplay for TSIS 4."""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import Callable

import pygame
from pygame.locals import KEYDOWN, K_BACKSPACE, K_DOWN, K_ESCAPE, K_LEFT, K_RETURN, K_RIGHT, K_SPACE, K_UP, QUIT

from config import (
    BLACK,
    BLUE,
    BOARD_COLS,
    BOARD_HEIGHT,
    BOARD_LEFT,
    BOARD_ROWS,
    BOARD_TOP,
    BOARD_WIDTH,
    CELL_SIZE,
    CYAN,
    DARK_GRAY,
    DARK_GREEN,
    DARK_RED,
    DEFAULT_SETTINGS,
    FOOD_LIFETIME_MS,
    FOODS_PER_LEVEL,
    FPS,
    GRAY,
    GREEN,
    LIGHT_GRAY,
    ORANGE,
    PANEL_LEFT,
    POWERUP_DURATION_MS,
    POWERUP_LIFETIME_MS,
    POWERUP_SPAWN_MAX_MS,
    POWERUP_SPAWN_MIN_MS,
    PURPLE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
    YELLOW,
    load_settings,
    save_settings,
    tuple_color,
)
from db import get_personal_best, get_top_scores, init_db, save_game_session


# -----------------------------
# Dataclasses for game objects
# -----------------------------
@dataclass
class Food:
    position: tuple[int, int]
    weight: int
    spawn_time: int


@dataclass
class PowerUp:
    kind: str
    position: tuple[int, int]
    spawn_time: int


# -----------------------------
# Small UI button class
# -----------------------------
@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: str

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        mouse_pos = pygame.mouse.get_pos()
        color = (80, 100, 130) if self.rect.collidepoint(mouse_pos) else (55, 70, 95)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=10)
        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


# -----------------------------
# Helper drawing functions
# -----------------------------
def make_fonts() -> dict[str, pygame.font.Font]:
    """Create fonts used by all screens."""
    return {
        "title": pygame.font.SysFont("Verdana", 44, bold=True),
        "big": pygame.font.SysFont("Verdana", 32, bold=True),
        "normal": pygame.font.SysFont("Verdana", 22),
        "small": pygame.font.SysFont("Verdana", 16),
        "tiny": pygame.font.SysFont("Verdana", 13),
    }


def draw_text(screen: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], x: int, y: int) -> None:
    """Draw text at a fixed position."""
    screen.blit(font.render(text, True, color), (x, y))


def draw_center(screen: pygame.Surface, text: str, font: pygame.font.Font, color: tuple[int, int, int], y: int) -> None:
    """Draw text centered horizontally."""
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=(SCREEN_WIDTH // 2, y)))


def draw_background(screen: pygame.Surface) -> None:
    """Draw a dark background for menus."""
    screen.fill((25, 30, 40))
    pygame.draw.rect(screen, (35, 43, 58), (40, 40, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80), border_radius=18)


def draw_board(screen: pygame.Surface, settings: dict) -> None:
    """Draw game board, border, and optional grid overlay."""
    board_rect = pygame.Rect(BOARD_LEFT, BOARD_TOP, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, (20, 25, 20), board_rect)
    pygame.draw.rect(screen, WHITE, board_rect, width=2)

    if settings.get("grid_overlay", True):
        for x in range(BOARD_LEFT, BOARD_LEFT + BOARD_WIDTH + 1, CELL_SIZE):
            pygame.draw.line(screen, (45, 55, 45), (x, BOARD_TOP), (x, BOARD_TOP + BOARD_HEIGHT))
        for y in range(BOARD_TOP, BOARD_TOP + BOARD_HEIGHT + 1, CELL_SIZE):
            pygame.draw.line(screen, (45, 55, 45), (BOARD_LEFT, y), (BOARD_LEFT + BOARD_WIDTH, y))


def cell_rect(position: tuple[int, int]) -> pygame.Rect:
    """Convert grid coordinates to a pygame Rect."""
    x, y = position
    return pygame.Rect(BOARD_LEFT + x * CELL_SIZE, BOARD_TOP + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)


def random_empty_cell(occupied: set[tuple[int, int]]) -> tuple[int, int]:
    """Return a random cell that is not occupied by snake, food, obstacles, or power-ups."""
    for _ in range(1000):
        pos = (random.randrange(BOARD_COLS), random.randrange(BOARD_ROWS))
        if pos not in occupied:
            return pos
    # Safe fallback if the board is almost full.
    for y in range(BOARD_ROWS):
        for x in range(BOARD_COLS):
            if (x, y) not in occupied:
                return (x, y)
    return (0, 0)


# -----------------------------
# Menu screens
# -----------------------------
def main_menu(screen: pygame.Surface, clock: pygame.time.Clock, db_status: str) -> tuple[str, str]:
    """Show main menu and username input field."""
    fonts = make_fonts()
    username = "Player"
    active_input = False
    buttons = [
        Button(pygame.Rect(300, 260, 220, 48), "Play", "play"),
        Button(pygame.Rect(300, 320, 220, 48), "Leaderboard", "leaderboard"),
        Button(pygame.Rect(300, 380, 220, 48), "Settings", "settings"),
        Button(pygame.Rect(300, 440, 220, 48), "Quit", "quit"),
    ]
    input_rect = pygame.Rect(260, 175, 300, 44)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                active_input = input_rect.collidepoint(event.pos)
                for button in buttons:
                    if button.clicked(event):
                        if button.action == "quit":
                            pygame.quit()
                            sys.exit()
                        return button.action, username.strip() or "Player"

            if event.type == KEYDOWN and active_input:
                if event.key == K_BACKSPACE:
                    username = username[:-1]
                elif event.key == K_RETURN:
                    return "play", username.strip() or "Player"
                elif len(username) < 16 and event.unicode.isprintable():
                    username += event.unicode

        draw_background(screen)
        draw_center(screen, "TSIS 4 Snake Game", fonts["title"], WHITE, 100)
        draw_center(screen, "Type username, then press Play", fonts["normal"], LIGHT_GRAY, 145)

        pygame.draw.rect(screen, (15, 20, 30), input_rect, border_radius=8)
        pygame.draw.rect(screen, CYAN if active_input else WHITE, input_rect, width=2, border_radius=8)
        draw_text(screen, username, fonts["normal"], WHITE, input_rect.x + 12, input_rect.y + 8)

        status_color = GREEN if db_status == "Database connected" else ORANGE
        draw_center(screen, db_status[:70], fonts["tiny"], status_color, 235)

        for button in buttons:
            button.draw(screen, fonts["normal"])

        pygame.display.flip()
        clock.tick(FPS)


def leaderboard_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Display Top 10 all-time scores from PostgreSQL."""
    fonts = make_fonts()
    back = Button(pygame.Rect(310, 545, 200, 45), "Back", "back")

    while True:
        rows = get_top_scores(10)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if back.clicked(event):
                return

        draw_background(screen)
        draw_center(screen, "Leaderboard - Top 10", fonts["big"], WHITE, 85)

        x0, y0 = 85, 145
        headers = ["Rank", "Username", "Score", "Level", "Date"]
        widths = [70, 180, 120, 90, 220]
        x = x0
        for header, width in zip(headers, widths):
            draw_text(screen, header, fonts["small"], YELLOW, x, y0)
            x += width

        pygame.draw.line(screen, LIGHT_GRAY, (x0, y0 + 28), (735, y0 + 28), 1)

        if not rows:
            draw_center(screen, "No scores yet or database is not connected.", fonts["normal"], ORANGE, 260)
        else:
            for i, row in enumerate(rows, start=1):
                y = y0 + 38 + (i - 1) * 34
                values = [
                    str(i),
                    str(row["username"]),
                    str(row["score"]),
                    str(row["level"]),
                    str(row["date"]),
                ]
                x = x0
                for value, width in zip(values, widths):
                    draw_text(screen, value[:22], fonts["small"], WHITE, x, y)
                    x += width

        back.draw(screen, fonts["normal"])
        pygame.display.flip()
        clock.tick(FPS)


def settings_screen(screen: pygame.Surface, clock: pygame.time.Clock, settings: dict) -> dict:
    """Settings screen: grid, sound, and snake color selection."""
    fonts = make_fonts()
    current = settings.copy()
    colors = [
        ("Green", [40, 200, 90]),
        ("Blue", [70, 130, 240]),
        ("Yellow", [240, 210, 60]),
        ("Purple", [150, 80, 230]),
        ("Orange", [240, 150, 40]),
    ]
    buttons = [
        Button(pygame.Rect(285, 190, 250, 45), "Toggle Grid", "grid"),
        Button(pygame.Rect(285, 250, 250, 45), "Toggle Sound", "sound"),
        Button(pygame.Rect(285, 470, 250, 45), "Save & Back", "save"),
    ]
    color_rects: list[tuple[pygame.Rect, list[int]]] = []
    for i, (_, rgb) in enumerate(colors):
        color_rects.append((pygame.Rect(215 + i * 80, 350, 50, 50), rgb))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return settings
            for button in buttons:
                if button.clicked(event):
                    if button.action == "grid":
                        current["grid_overlay"] = not current.get("grid_overlay", True)
                    elif button.action == "sound":
                        current["sound"] = not current.get("sound", True)
                    elif button.action == "save":
                        save_settings(current)
                        return current
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, rgb in color_rects:
                    if rect.collidepoint(event.pos):
                        current["snake_color"] = rgb

        draw_background(screen)
        draw_center(screen, "Settings", fonts["big"], WHITE, 95)
        draw_center(screen, f"Grid overlay: {'ON' if current.get('grid_overlay', True) else 'OFF'}", fonts["normal"], LIGHT_GRAY, 150)
        draw_center(screen, f"Sound: {'ON' if current.get('sound', True) else 'OFF'}", fonts["normal"], LIGHT_GRAY, 175)

        for button in buttons:
            button.draw(screen, fonts["normal"])

        draw_center(screen, "Pick snake color", fonts["normal"], WHITE, 320)
        selected = current.get("snake_color", DEFAULT_SETTINGS["snake_color"])
        for rect, rgb in color_rects:
            pygame.draw.rect(screen, tuple(rgb), rect, border_radius=8)
            border = CYAN if rgb == selected else WHITE
            pygame.draw.rect(screen, border, rect, width=3, border_radius=8)

        pygame.display.flip()
        clock.tick(FPS)


def game_over_screen(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    username: str,
    score: int,
    level: int,
    personal_best: int,
    saved_message: str,
) -> str:
    """Display Game Over screen and return retry/menu action."""
    fonts = make_fonts()
    retry = Button(pygame.Rect(210, 430, 180, 50), "Retry", "retry")
    menu = Button(pygame.Rect(430, 430, 180, 50), "Main Menu", "menu")

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if retry.clicked(event):
                return "retry"
            if menu.clicked(event):
                return "menu"
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return "retry"
                if event.key == K_ESCAPE:
                    return "menu"

        draw_background(screen)
        draw_center(screen, "GAME OVER", fonts["title"], RED, 120)
        draw_center(screen, f"Player: {username}", fonts["normal"], WHITE, 195)
        draw_center(screen, f"Final score: {score}", fonts["normal"], WHITE, 235)
        draw_center(screen, f"Level reached: {level}", fonts["normal"], WHITE, 270)
        draw_center(screen, f"Personal best: {max(personal_best, score)}", fonts["normal"], YELLOW, 305)
        draw_center(screen, saved_message[:70], fonts["small"], LIGHT_GRAY, 350)
        retry.draw(screen, fonts["normal"])
        menu.draw(screen, fonts["normal"])

        pygame.display.flip()
        clock.tick(FPS)


# -----------------------------
# Snake gameplay
# -----------------------------
class SnakeGame:
    """One playable Snake game session."""

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, username: str, settings: dict) -> None:
        self.screen = screen
        self.clock = clock
        self.username = username.strip()[:50] or "Player"
        self.settings = settings
        self.fonts = make_fonts()

        self.snake_color = tuple_color(settings.get("snake_color"))
        self.snake: list[tuple[int, int]] = [(8, 15), (7, 15), (6, 15)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)

        self.score = 0
        self.foods_eaten = 0
        self.level = 1
        self.base_move_delay = 150
        self.last_move_time = pygame.time.get_ticks()

        self.personal_best = get_personal_best(self.username)

        self.obstacles: set[tuple[int, int]] = set()
        self.food = self.spawn_food()
        self.poison = self.spawn_poison()
        self.field_powerup: PowerUp | None = None
        self.next_powerup_spawn = pygame.time.get_ticks() + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)

        self.active_power: str | None = None
        self.active_power_end = 0
        self.shield_ready = False

        self.running = True

    def occupied_cells(self) -> set[tuple[int, int]]:
        """Return every cell that new items must avoid."""
        occupied = set(self.snake) | set(self.obstacles)
        food = getattr(self, "food", None)
        poison = getattr(self, "poison", None)
        field_powerup = getattr(self, "field_powerup", None)
        if food:
            occupied.add(food.position)
        if poison:
            occupied.add(poison.position)
        if field_powerup:
            occupied.add(field_powerup.position)
        return occupied

    def spawn_food(self) -> Food:
        """Create weighted food that expires after a timer."""
        weights = [1, 1, 1, 2, 2, 3]
        weight = random.choice(weights)
        return Food(random_empty_cell(self.occupied_cells() if hasattr(self, "snake") else set()), weight, pygame.time.get_ticks())

    def spawn_poison(self) -> Food:
        """Create poison food in a random safe cell."""
        return Food(random_empty_cell(self.occupied_cells()), 0, pygame.time.get_ticks())

    def spawn_powerup_if_needed(self, now: int) -> None:
        """Spawn one temporary power-up if there is no active/field power-up."""
        if self.field_powerup is not None:
            if now - self.field_powerup.spawn_time > POWERUP_LIFETIME_MS:
                self.field_powerup = None
                self.next_powerup_spawn = now + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)
            return

        # Only one power-up active at a time.
        if self.active_power is not None:
            return

        if now >= self.next_powerup_spawn:
            kind = random.choice(["speed", "slow", "shield"])
            pos = random_empty_cell(self.occupied_cells())
            self.field_powerup = PowerUp(kind, pos, now)

    def update_powerup_timer(self, now: int) -> None:
        """Turn off temporary timed power-ups after 5 seconds."""
        if self.active_power in {"speed", "slow"} and now >= self.active_power_end:
            self.active_power = None
            self.active_power_end = 0
            self.next_powerup_spawn = now + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)

    def move_delay(self) -> int:
        """Calculate current movement delay based on level and active power-up."""
        delay = max(60, self.base_move_delay - (self.level - 1) * 8)
        if self.active_power == "speed":
            delay = int(delay * 0.60)
        elif self.active_power == "slow":
            delay = int(delay * 1.60)
        return max(40, delay)

    def set_direction(self, new_dir: tuple[int, int]) -> None:
        """Set direction, but block direct 180-degree turns."""
        if (new_dir[0] + self.direction[0], new_dir[1] + self.direction[1]) != (0, 0):
            self.next_direction = new_dir

    def handle_events(self) -> None:
        """Handle quit and keyboard controls."""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                elif event.key == K_UP:
                    self.set_direction((0, -1))
                elif event.key == K_DOWN:
                    self.set_direction((0, 1))
                elif event.key == K_LEFT:
                    self.set_direction((-1, 0))
                elif event.key == K_RIGHT:
                    self.set_direction((1, 0))
                elif event.key == K_SPACE:
                    # Space pauses the game until another key is pressed.
                    self.pause()

    def pause(self) -> None:
        """Simple pause screen."""
        draw_center(self.screen, "PAUSED - press any key", self.fonts["normal"], YELLOW, SCREEN_HEIGHT // 2)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waiting = False
            self.clock.tick(FPS)

    def handle_level_up(self) -> None:
        """Increase level every N foods and create new obstacles from Level 3."""
        new_level = self.foods_eaten // FOODS_PER_LEVEL + 1
        if new_level > self.level:
            self.level = new_level
            if self.level >= 3:
                self.generate_obstacles()

    def generate_obstacles(self) -> None:
        """Randomly place obstacle blocks without trapping the snake head."""
        head = self.snake[0]
        amount = min(8 + self.level * 2, 55)

        for _ in range(80):
            new_obstacles: set[tuple[int, int]] = set()
            blocked_area = {
                (head[0] + dx, head[1] + dy)
                for dx in range(-2, 3)
                for dy in range(-2, 3)
                if 0 <= head[0] + dx < BOARD_COLS and 0 <= head[1] + dy < BOARD_ROWS
            }
            occupied = set(self.snake) | blocked_area
            while len(new_obstacles) < amount:
                pos = random_empty_cell(occupied | new_obstacles)
                new_obstacles.add(pos)

            # Guarantee the current head still has at least two open neighbor cells.
            free_neighbors = 0
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                n = (head[0] + dx, head[1] + dy)
                if 0 <= n[0] < BOARD_COLS and 0 <= n[1] < BOARD_ROWS and n not in new_obstacles:
                    free_neighbors += 1
            if free_neighbors >= 2:
                self.obstacles = new_obstacles
                self.food = self.spawn_food()
                self.poison = self.spawn_poison()
                return

    def consume_shield(self) -> None:
        """Use shield once and remove the active effect."""
        self.shield_ready = False
        self.active_power = None
        self.active_power_end = 0
        self.next_powerup_spawn = pygame.time.get_ticks() + random.randint(POWERUP_SPAWN_MIN_MS, POWERUP_SPAWN_MAX_MS)

    def update(self) -> None:
        """Update timers and move snake when enough time has passed."""
        now = pygame.time.get_ticks()
        self.update_powerup_timer(now)
        self.spawn_powerup_if_needed(now)

        # Normal food disappears after a timer, then respawns.
        if now - self.food.spawn_time > FOOD_LIFETIME_MS:
            self.food = self.spawn_food()

        if now - self.last_move_time >= self.move_delay():
            self.last_move_time = now
            self.move_snake()

    def move_snake(self) -> None:
        """Move snake one cell and process all collisions."""
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])

        # Border collision. Shield saves the snake once by wrapping to the opposite side.
        if not (0 <= new_head[0] < BOARD_COLS and 0 <= new_head[1] < BOARD_ROWS):
            if self.shield_ready:
                self.consume_shield()
                new_head = (new_head[0] % BOARD_COLS, new_head[1] % BOARD_ROWS)
            else:
                self.running = False
                return

        # Obstacle collision. In this project, obstacle blocks are hard walls.
        if new_head in self.obstacles:
            self.running = False
            return

        # Self-collision. Shield cuts the snake at the collision point and saves the run once.
        if new_head in self.snake:
            if self.shield_ready:
                self.consume_shield()
                index = self.snake.index(new_head)
                self.snake = self.snake[: max(1, index)]
            else:
                self.running = False
                return

        grow_by = 0
        self.snake.insert(0, new_head)

        # Eat normal weighted food.
        if new_head == self.food.position:
            grow_by = self.food.weight
            self.score += self.food.weight * 10
            self.foods_eaten += 1
            self.food = self.spawn_food()
            self.handle_level_up()

        # Eat poison: shorten snake by 2 segments.
        if new_head == self.poison.position:
            self.score = max(0, self.score - 15)
            self.poison = self.spawn_poison()
            for _ in range(2):
                if len(self.snake) > 1:
                    self.snake.pop()
            if len(self.snake) <= 1:
                self.running = False
                return

        # Collect a power-up.
        if self.field_powerup and new_head == self.field_powerup.position:
            self.activate_powerup(self.field_powerup.kind)
            self.field_powerup = None

        # Remove tail unless snake has eaten food.
        # weight 1 grows by 1, weight 2 grows by 2, etc.
        if grow_by == 0:
            self.snake.pop()
        else:
            for _ in range(grow_by - 1):
                self.snake.append(self.snake[-1])

    def activate_powerup(self, kind: str) -> None:
        """Activate speed, slow, or shield power-up."""
        now = pygame.time.get_ticks()
        self.active_power = kind
        if kind == "shield":
            self.shield_ready = True
            self.active_power_end = 0
        else:
            self.shield_ready = False
            self.active_power_end = now + POWERUP_DURATION_MS
        self.score += 20

    def active_power_text(self) -> str:
        """Return text for current active power-up and remaining time."""
        if self.active_power is None:
            return "None"
        if self.active_power == "shield":
            return "Shield: until hit"
        remaining = max(0, (self.active_power_end - pygame.time.get_ticks()) // 1000 + 1)
        return f"{self.active_power.title()}: {remaining}s"

    def draw(self) -> None:
        """Draw the whole game frame."""
        self.screen.fill((12, 15, 18))
        draw_board(self.screen, self.settings)

        # Draw obstacles.
        for pos in self.obstacles:
            rect = cell_rect(pos)
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, width=2)

        # Draw normal food with number weight.
        food_rect = cell_rect(self.food.position)
        food_color = [GREEN, YELLOW, ORANGE][self.food.weight - 1]
        pygame.draw.ellipse(self.screen, food_color, food_rect.inflate(-3, -3))
        weight_label = self.fonts["tiny"].render(str(self.food.weight), True, BLACK)
        self.screen.blit(weight_label, weight_label.get_rect(center=food_rect.center))

        # Draw poison.
        poison_rect = cell_rect(self.poison.position)
        pygame.draw.ellipse(self.screen, DARK_RED, poison_rect.inflate(-2, -2))
        draw_center_small = self.fonts["tiny"].render("P", True, WHITE)
        self.screen.blit(draw_center_small, draw_center_small.get_rect(center=poison_rect.center))

        # Draw field power-up.
        if self.field_powerup:
            rect = cell_rect(self.field_powerup.position)
            color = {"speed": CYAN, "slow": BLUE, "shield": PURPLE}[self.field_powerup.kind]
            pygame.draw.rect(self.screen, color, rect.inflate(-2, -2), border_radius=5)
            label = self.fonts["tiny"].render(self.field_powerup.kind[0].upper(), True, WHITE)
            self.screen.blit(label, label.get_rect(center=rect.center))

        # Draw snake body.
        for i, pos in enumerate(self.snake):
            rect = cell_rect(pos)
            color = self.snake_color if i == 0 else DARK_GREEN
            pygame.draw.rect(self.screen, color, rect.inflate(-2, -2), border_radius=5)

        # Draw side panel.
        draw_text(self.screen, f"Player: {self.username}", self.fonts["small"], WHITE, PANEL_LEFT, 25)
        draw_text(self.screen, f"Score: {self.score}", self.fonts["normal"], YELLOW, PANEL_LEFT, 65)
        draw_text(self.screen, f"Level: {self.level}", self.fonts["normal"], WHITE, PANEL_LEFT, 100)
        draw_text(self.screen, f"Food eaten: {self.foods_eaten}", self.fonts["small"], LIGHT_GRAY, PANEL_LEFT, 140)
        draw_text(self.screen, f"Best: {self.personal_best}", self.fonts["small"], CYAN, PANEL_LEFT, 170)
        draw_text(self.screen, "Power-up:", self.fonts["small"], WHITE, PANEL_LEFT, 225)
        draw_text(self.screen, self.active_power_text(), self.fonts["small"], ORANGE, PANEL_LEFT, 252)
        draw_text(self.screen, "Controls:", self.fonts["small"], WHITE, PANEL_LEFT, 330)
        draw_text(self.screen, "Arrow keys - move", self.fonts["tiny"], LIGHT_GRAY, PANEL_LEFT, 360)
        draw_text(self.screen, "Space - pause", self.fonts["tiny"], LIGHT_GRAY, PANEL_LEFT, 382)
        draw_text(self.screen, "Esc - end run", self.fonts["tiny"], LIGHT_GRAY, PANEL_LEFT, 404)

        pygame.display.flip()

    def run(self) -> tuple[int, int, int]:
        """Run one game session and return score, level, and personal best."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        return self.score, self.level, self.personal_best


def run_game(screen: pygame.Surface, clock: pygame.time.Clock, username: str, settings: dict) -> tuple[int, int, int]:
    """Public helper used by main.py to run one Snake session."""
    return SnakeGame(screen, clock, username, settings).run()


# -----------------------------
# Main program loop
# -----------------------------
def run_app() -> None:
    """Initialize pygame, database, settings, and start screen navigation."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TSIS 4 Snake Game")
    clock = pygame.time.Clock()

    settings = load_settings()
    db_ok, db_status = init_db()
    if not db_ok:
        db_status = "DB error: check config.py / PostgreSQL"

    while True:
        action, username = main_menu(screen, clock, db_status)

        if action == "leaderboard":
            leaderboard_screen(screen, clock)

        elif action == "settings":
            settings = settings_screen(screen, clock, settings)

        elif action == "play":
            while True:
                score, level, personal_best = run_game(screen, clock, username, settings)
                saved, message = save_game_session(username, score, level)
                saved_message = "Result saved to PostgreSQL" if saved else f"Could not save: {message[:45]}"
                next_action = game_over_screen(screen, clock, username, score, level, personal_best, saved_message)
                if next_action == "retry":
                    continue
                break
