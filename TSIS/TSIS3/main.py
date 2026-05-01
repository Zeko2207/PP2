"""TSIS 3 Racer Game entry point."""

import pygame

from persistence import add_score, load_settings, save_settings
from racer import SCREEN_HEIGHT, SCREEN_WIDTH, run_game
from ui import game_over_screen, leaderboard_screen, main_menu, settings_screen, username_screen


def main() -> None:
    """Start the game and manage screen navigation."""
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        # The game still works if the computer has no available audio device.
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("TSIS 3 Racer Game")
    clock = pygame.time.Clock()

    settings = load_settings()
    save_settings(settings)  # Create settings.json if it does not exist yet.

    while True:
        action = main_menu(screen, clock)

        if action == "settings":
            settings = settings_screen(screen, clock, settings)

        elif action == "leaderboard":
            leaderboard_screen(screen, clock)

        elif action == "play":
            username = username_screen(screen, clock)
            if username == "__BACK__":
                continue

            while True:
                result = run_game(screen, clock, settings, username)
                add_score(result)

                next_action = game_over_screen(screen, clock, result)

                if next_action == "retry":
                    continue
                if next_action == "leaderboard":
                    leaderboard_screen(screen, clock)
                    continue
                if next_action == "menu":
                    break


if __name__ == "__main__":
    main()
