"""Simple Pygame UI screens: menu, settings, leaderboard, username, game over."""

from __future__ import annotations

import sys
from typing import Any

import pygame
from pygame.locals import *

from persistence import VALID_COLORS, VALID_DIFFICULTIES, load_leaderboard, save_settings

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (80, 80, 80)
DARK = (25, 25, 30)
BLUE = (55, 130, 220)
LIGHT_BLUE = (100, 170, 240)
GREEN = (40, 170, 90)
RED = (210, 60, 60)
YELLOW = (230, 200, 60)

CAR_COLORS = {
    "blue": (45, 120, 230),
    "red": (220, 60, 60),
    "green": (40, 180, 90),
    "yellow": (230, 200, 40),
    "purple": (145, 80, 220),
}

pygame.font.init()
FONT_TITLE = pygame.font.SysFont("Verdana", 42, bold=True)
FONT_BIG = pygame.font.SysFont("Verdana", 30, bold=True)
FONT_MEDIUM = pygame.font.SysFont("Verdana", 22)
FONT_SMALL = pygame.font.SysFont("Verdana", 17)


class Button:
    """A simple rectangle button that can be clicked with the mouse."""

    def __init__(self, text: str, rect: tuple[int, int, int, int], color=BLUE):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.color = color

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the button and highlight it when the mouse is above it."""
        mouse_pos = pygame.mouse.get_pos()
        color = LIGHT_BLUE if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=12)

        text_surface = FONT_MEDIUM.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Return True if this button was clicked."""
        return event.type == MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)


def draw_text_center(screen: pygame.Surface, text: str, font: pygame.font.Font, color, y: int) -> None:
    """Draw text horizontally centered."""
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(SCREEN_WIDTH // 2, y))
    screen.blit(surface, rect)


def quit_game() -> None:
    """Close the game safely."""
    pygame.quit()
    sys.exit()


def main_menu(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Show main menu and return the chosen action."""
    buttons = {
        "play": Button("Play", (150, 250, 200, 55), GREEN),
        "leaderboard": Button("Leaderboard", (150, 320, 200, 55), BLUE),
        "settings": Button("Settings", (150, 390, 200, 55), BLUE),
        "quit": Button("Quit", (150, 460, 200, 55), RED),
    }

    while True:
        screen.fill(DARK)
        draw_text_center(screen, "RACER GAME", FONT_TITLE, WHITE, 150)
        draw_text_center(screen, "TSIS 3 Edition", FONT_SMALL, YELLOW, 195)

        for button in buttons.values():
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            if buttons["play"].is_clicked(event):
                return "play"
            if buttons["leaderboard"].is_clicked(event):
                return "leaderboard"
            if buttons["settings"].is_clicked(event):
                return "settings"
            if buttons["quit"].is_clicked(event):
                quit_game()

        pygame.display.update()
        clock.tick(FPS)


def username_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> str:
    """Ask the player to enter a username before starting."""
    name = ""
    start_button = Button("Start", (150, 430, 200, 55), GREEN)
    back_button = Button("Back", (150, 500, 200, 50), RED)

    while True:
        screen.fill(DARK)
        draw_text_center(screen, "Enter your name", FONT_BIG, WHITE, 170)
        draw_text_center(screen, "Press Enter or click Start", FONT_SMALL, YELLOW, 215)

        input_rect = pygame.Rect(100, 280, 300, 60)
        pygame.draw.rect(screen, WHITE, input_rect, border_radius=10)
        pygame.draw.rect(screen, BLUE, input_rect, 3, border_radius=10)

        shown_name = name if name else "Player"
        text = FONT_MEDIUM.render(shown_name, True, BLACK)
        screen.blit(text, (input_rect.x + 15, input_rect.y + 17))

        start_button.draw(screen)
        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()

            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return name.strip() or "Player"
                if event.key == K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode

            if start_button.is_clicked(event):
                return name.strip() or "Player"
            if back_button.is_clicked(event):
                return "__BACK__"

        pygame.display.update()
        clock.tick(FPS)


def settings_screen(screen: pygame.Surface, clock: pygame.time.Clock, settings: dict[str, Any]) -> dict[str, Any]:
    """Allow sound, car color, and difficulty changes."""
    local_settings = settings.copy()

    sound_button = Button("", (110, 220, 280, 50), BLUE)
    color_button = Button("", (110, 295, 280, 50), BLUE)
    difficulty_button = Button("", (110, 370, 280, 50), BLUE)
    back_button = Button("Save and Back", (110, 500, 280, 55), GREEN)

    while True:
        screen.fill(DARK)
        draw_text_center(screen, "Settings", FONT_TITLE, WHITE, 145)

        sound_button.text = f"Sound: {'ON' if local_settings['sound'] else 'OFF'}"
        color_button.text = f"Car color: {local_settings['car_color']}"
        difficulty_button.text = f"Difficulty: {local_settings['difficulty']}"

        for button in [sound_button, color_button, difficulty_button, back_button]:
            button.draw(screen)

        # Preview of selected car color
        car_color = CAR_COLORS.get(local_settings["car_color"], CAR_COLORS["blue"])
        pygame.draw.rect(screen, car_color, (220, 440, 60, 38), border_radius=8)
        pygame.draw.rect(screen, WHITE, (220, 440, 60, 38), 2, border_radius=8)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()

            if sound_button.is_clicked(event):
                local_settings["sound"] = not local_settings["sound"]

            if color_button.is_clicked(event):
                current = VALID_COLORS.index(local_settings["car_color"])
                local_settings["car_color"] = VALID_COLORS[(current + 1) % len(VALID_COLORS)]

            if difficulty_button.is_clicked(event):
                current = VALID_DIFFICULTIES.index(local_settings["difficulty"])
                local_settings["difficulty"] = VALID_DIFFICULTIES[(current + 1) % len(VALID_DIFFICULTIES)]

            if back_button.is_clicked(event):
                save_settings(local_settings)
                return local_settings

            if event.type == KEYDOWN and event.key == K_ESCAPE:
                save_settings(local_settings)
                return local_settings

        pygame.display.update()
        clock.tick(FPS)


def leaderboard_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> None:
    """Display top 10 saved scores."""
    back_button = Button("Back", (150, 610, 200, 50), RED)

    while True:
        entries = load_leaderboard()
        screen.fill(DARK)
        draw_text_center(screen, "Top 10 Leaderboard", FONT_BIG, WHITE, 80)

        header = FONT_SMALL.render("Rank   Name          Score     Distance", True, YELLOW)
        screen.blit(header, (45, 135))

        y = 175
        if not entries:
            draw_text_center(screen, "No scores yet", FONT_MEDIUM, WHITE, 260)
        else:
            for index, entry in enumerate(entries, start=1):
                row = f"{index:<5} {entry['name']:<12} {entry['score']:<8} {entry['distance']}m"
                row_surface = FONT_SMALL.render(row, True, WHITE)
                screen.blit(row_surface, (45, y))
                y += 38

        back_button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            if back_button.is_clicked(event):
                return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return

        pygame.display.update()
        clock.tick(FPS)


def game_over_screen(screen: pygame.Surface, clock: pygame.time.Clock, result: dict[str, Any]) -> str:
    """Show score after death or finish. Return retry/menu/leaderboard."""
    retry_button = Button("Retry", (150, 390, 200, 55), GREEN)
    menu_button = Button("Main Menu", (150, 460, 200, 55), BLUE)
    leaderboard_button = Button("Leaderboard", (150, 530, 200, 55), BLUE)

    title = "FINISH!" if result.get("finished") else "GAME OVER"

    while True:
        screen.fill((100, 20, 20) if not result.get("finished") else (20, 85, 50))
        draw_text_center(screen, title, FONT_TITLE, WHITE, 110)

        draw_text_center(screen, f"Name: {result['name']}", FONT_SMALL, WHITE, 190)
        draw_text_center(screen, f"Score: {result['score']}", FONT_MEDIUM, WHITE, 230)
        draw_text_center(screen, f"Distance: {result['distance']}m", FONT_SMALL, WHITE, 270)
        draw_text_center(screen, f"Coins: {result['coins']}", FONT_SMALL, WHITE, 300)

        retry_button.draw(screen)
        menu_button.draw(screen)
        leaderboard_button.draw(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            if retry_button.is_clicked(event):
                return "retry"
            if menu_button.is_clicked(event):
                return "menu"
            if leaderboard_button.is_clicked(event):
                return "leaderboard"

        pygame.display.update()
        clock.tick(FPS)
