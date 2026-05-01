"""Main Racer gameplay module for TSIS 3.

This file contains the actual race: scrolling road, traffic cars, obstacles,
road events, coins, power-ups, distance meter, difficulty scaling, and scoring.
"""

from __future__ import annotations

import math
import random
import time
from typing import Any

import pygame
from pygame.locals import *

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60

ROAD_X = 70
ROAD_WIDTH = 360
LANES = 4
LANE_WIDTH = ROAD_WIDTH // LANES
LANE_CENTERS = [ROAD_X + LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(LANES)]

FINISH_DISTANCE = 5000
SPEED_UP_EVERY_COINS = 5

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)
ROAD_GRAY = (55, 55, 60)
YELLOW = (235, 210, 60)
ORANGE = (235, 145, 45)
RED = (215, 60, 60)
GREEN = (40, 180, 90)
BLUE = (45, 120, 230)
PURPLE = (145, 80, 220)
CYAN = (40, 210, 230)

CAR_COLORS = {
    "blue": BLUE,
    "red": RED,
    "green": GREEN,
    "yellow": YELLOW,
    "purple": PURPLE,
}

DIFFICULTY_DATA = {
    "easy": {"spawn_factor": 0.80, "speed_factor": 0.90, "start_traffic": 1},
    "normal": {"spawn_factor": 1.00, "speed_factor": 1.00, "start_traffic": 2},
    "hard": {"spawn_factor": 1.25, "speed_factor": 1.15, "start_traffic": 3},
}

pygame.font.init()
FONT_BIG = pygame.font.SysFont("Verdana", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("Verdana", 17)
FONT_TINY = pygame.font.SysFont("Verdana", 14)


class Player(pygame.sprite.Sprite):
    """The player's car. It moves between lanes using arrow keys or A/D."""

    def __init__(self, car_color: tuple[int, int, int]):
        super().__init__()
        self.lane = 1
        self.image = self.create_car_image(car_color)
        self.rect = self.image.get_rect(center=(LANE_CENTERS[self.lane], SCREEN_HEIGHT - 105))
        self.target_x = self.rect.centerx

    def create_car_image(self, color: tuple[int, int, int]) -> pygame.Surface:
        """Create a simple car using Pygame shapes, so no image file is required."""
        image = pygame.Surface((54, 88), pygame.SRCALPHA)
        pygame.draw.rect(image, color, (8, 8, 38, 72), border_radius=10)
        pygame.draw.rect(image, (180, 220, 255), (15, 15, 24, 18), border_radius=5)
        pygame.draw.rect(image, (180, 220, 255), (15, 52, 24, 18), border_radius=5)
        pygame.draw.rect(image, BLACK, (3, 18, 8, 18), border_radius=3)
        pygame.draw.rect(image, BLACK, (43, 18, 8, 18), border_radius=3)
        pygame.draw.rect(image, BLACK, (3, 55, 8, 18), border_radius=3)
        pygame.draw.rect(image, BLACK, (43, 55, 8, 18), border_radius=3)
        return image

    def move(self) -> None:
        """Move the player lane by lane."""
        keys = pygame.key.get_pressed()

        # Lane switch is handled by KEYDOWN in run_game, but smooth movement is here.
        if self.rect.centerx < self.target_x:
            self.rect.centerx = min(self.rect.centerx + 10, self.target_x)
        elif self.rect.centerx > self.target_x:
            self.rect.centerx = max(self.rect.centerx - 10, self.target_x)

        # Small vertical control for extra dodging.
        if keys[K_UP] and self.rect.top > 120:
            self.rect.move_ip(0, -4)
        if keys[K_DOWN] and self.rect.bottom < SCREEN_HEIGHT - 20:
            self.rect.move_ip(0, 4)

    def change_lane(self, direction: int) -> None:
        """Change lane: direction -1 means left, +1 means right."""
        self.lane = max(0, min(LANES - 1, self.lane + direction))
        self.target_x = LANE_CENTERS[self.lane]


class TrafficCar(pygame.sprite.Sprite):
    """Enemy traffic car. Collision with it ends the run unless shield is active."""

    COLORS = [RED, ORANGE, PURPLE, (30, 170, 180)]

    def __init__(self, player: Player, speed: float):
        super().__init__()
        self.speed = speed
        self.image = self.create_car_image(random.choice(self.COLORS))
        self.rect = self.image.get_rect()
        self.reset(player)

    def create_car_image(self, color: tuple[int, int, int]) -> pygame.Surface:
        """Create enemy vehicle image."""
        image = pygame.Surface((52, 84), pygame.SRCALPHA)
        pygame.draw.rect(image, color, (8, 8, 36, 68), border_radius=10)
        pygame.draw.rect(image, (220, 230, 245), (15, 15, 22, 17), border_radius=4)
        pygame.draw.rect(image, (220, 230, 245), (15, 50, 22, 17), border_radius=4)
        pygame.draw.rect(image, BLACK, (3, 17, 8, 17), border_radius=3)
        pygame.draw.rect(image, BLACK, (41, 17, 8, 17), border_radius=3)
        pygame.draw.rect(image, BLACK, (3, 53, 8, 17), border_radius=3)
        pygame.draw.rect(image, BLACK, (41, 53, 8, 17), border_radius=3)
        return image

    def reset(self, player: Player) -> None:
        """Respawn car above the screen. Avoid spawning too close to the player's lane."""
        possible_lanes = list(range(LANES))
        if player.lane in possible_lanes and random.random() < 0.65:
            possible_lanes.remove(player.lane)

        lane = random.choice(possible_lanes)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-800, -100))
        self.speed = random.uniform(4.0, 7.0)

    def update(self, road_speed: float, player: Player) -> None:
        """Move traffic down the road."""
        self.rect.move_ip(0, self.speed + road_speed * 0.35)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset(player)


class Coin(pygame.sprite.Sprite):
    """Weighted coin. Weight 1, 2, or 3 gives different score values."""

    def __init__(self, player: Player):
        super().__init__()
        self.weight = 1
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.reset(player)

    def create_image(self) -> pygame.Surface:
        """Create coin image based on weight."""
        radius = 12 + self.weight * 3
        color = [YELLOW, ORANGE, GREEN][self.weight - 1]
        image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(image, color, (radius, radius), radius)
        pygame.draw.circle(image, WHITE, (radius, radius), radius, 2)
        text = FONT_TINY.render(str(self.weight), True, BLACK)
        image.blit(text, text.get_rect(center=(radius, radius)))
        return image

    def reset(self, player: Player) -> None:
        """Respawn coin above the screen."""
        self.weight = random.choice([1, 1, 2, 2, 3])
        self.image = self.create_image()
        self.rect = self.image.get_rect()
        lane = random.randrange(LANES)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-700, -80))

    def update(self, road_speed: float, player: Player) -> None:
        """Move coin down the road."""
        self.rect.move_ip(0, road_speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset(player)


class Obstacle(pygame.sprite.Sprite):
    """Road obstacle: barrier, oil spill, or pothole."""

    TYPES = ["barrier", "oil", "pothole"]

    def __init__(self, player: Player):
        super().__init__()
        self.kind = "barrier"
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.reset(player)

    def create_image(self) -> pygame.Surface:
        """Create obstacle image depending on its type."""
        if self.kind == "barrier":
            image = pygame.Surface((64, 28), pygame.SRCALPHA)
            pygame.draw.rect(image, RED, (0, 0, 64, 28), border_radius=6)
            pygame.draw.line(image, WHITE, (8, 24), (28, 4), 4)
            pygame.draw.line(image, WHITE, (36, 24), (56, 4), 4)
            return image

        if self.kind == "oil":
            image = pygame.Surface((58, 36), pygame.SRCALPHA)
            pygame.draw.ellipse(image, BLACK, (2, 4, 54, 28))
            pygame.draw.ellipse(image, (60, 60, 80), (15, 10, 20, 10))
            return image

        image = pygame.Surface((58, 42), pygame.SRCALPHA)
        pygame.draw.ellipse(image, DARK_GRAY, (3, 5, 52, 30))
        pygame.draw.ellipse(image, BLACK, (12, 12, 35, 16))
        return image

    def reset(self, player: Player) -> None:
        """Respawn obstacle while trying not to make an impossible immediate collision."""
        self.kind = random.choice(self.TYPES)
        self.image = self.create_image()
        self.rect = self.image.get_rect()

        possible_lanes = list(range(LANES))
        if random.random() < 0.55 and player.lane in possible_lanes:
            possible_lanes.remove(player.lane)

        lane = random.choice(possible_lanes)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-900, -150))

    def update(self, road_speed: float, player: Player) -> None:
        """Move obstacle down."""
        self.rect.move_ip(0, road_speed)
        if self.rect.top > SCREEN_HEIGHT:
            self.reset(player)


class PowerUp(pygame.sprite.Sprite):
    """Collectible power-up: Nitro, Shield, or Repair."""

    TYPES = ["nitro", "shield", "repair"]

    def __init__(self, player: Player):
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.spawn_time = time.time()
        self.visible_since: float | None = None
        self.lifetime = 7.0
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.reset(player)

    def create_image(self) -> pygame.Surface:
        """Create power-up icon."""
        image = pygame.Surface((42, 42), pygame.SRCALPHA)
        if self.kind == "nitro":
            color = CYAN
            label = "N"
        elif self.kind == "shield":
            color = BLUE
            label = "S"
        else:
            color = GREEN
            label = "+"

        pygame.draw.circle(image, color, (21, 21), 20)
        pygame.draw.circle(image, WHITE, (21, 21), 20, 3)
        text = FONT_SMALL.render(label, True, WHITE)
        image.blit(text, text.get_rect(center=(21, 20)))
        return image

    def reset(self, player: Player) -> None:
        """Respawn power-up above the screen."""
        self.kind = random.choice(self.TYPES)
        self.image = self.create_image()
        self.rect = self.image.get_rect()
        lane = random.randrange(LANES)
        self.rect.center = (LANE_CENTERS[lane], random.randint(-1800, -600))
        self.spawn_time = time.time()
        self.visible_since = None
        self.lifetime = 7.0

    def update(self, road_speed: float, player: Player) -> None:
        """Move power-up and remove it after timeout."""
        self.rect.move_ip(0, road_speed)

        # The timeout starts only after the power-up becomes visible.
        if self.rect.top >= 0 and self.visible_since is None:
            self.visible_since = time.time()

        timed_out = self.visible_since is not None and time.time() - self.visible_since > self.lifetime
        if self.rect.top > SCREEN_HEIGHT or timed_out:
            self.reset(player)


class RoadEvent(pygame.sprite.Sprite):
    """Dynamic road event: moving barrier, speed bump, or nitro strip."""

    TYPES = ["moving_barrier", "speed_bump", "nitro_strip"]

    def __init__(self, player: Player):
        super().__init__()
        self.kind = random.choice(self.TYPES)
        self.direction = random.choice([-1, 1])
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.reset(player)

    def create_image(self) -> pygame.Surface:
        """Create the visual for each road event."""
        if self.kind == "moving_barrier":
            image = pygame.Surface((90, 26), pygame.SRCALPHA)
            pygame.draw.rect(image, RED, (0, 0, 90, 26), border_radius=6)
            pygame.draw.rect(image, WHITE, (10, 8, 70, 10), border_radius=4)
            return image

        if self.kind == "speed_bump":
            image = pygame.Surface((LANE_WIDTH - 10, 24), pygame.SRCALPHA)
            pygame.draw.rect(image, ORANGE, (0, 0, LANE_WIDTH - 10, 24), border_radius=10)
            pygame.draw.line(image, BLACK, (8, 12), (LANE_WIDTH - 18, 12), 3)
            return image

        image = pygame.Surface((LANE_WIDTH - 10, 32), pygame.SRCALPHA)
        pygame.draw.rect(image, CYAN, (0, 0, LANE_WIDTH - 10, 32), border_radius=10)
        pygame.draw.polygon(image, WHITE, [(18, 6), (45, 16), (18, 26)])
        return image

    def reset(self, player: Player) -> None:
        """Respawn event."""
        self.kind = random.choice(self.TYPES)
        self.direction = random.choice([-1, 1])
        self.image = self.create_image()
        self.rect = self.image.get_rect()

        if self.kind == "moving_barrier":
            self.rect.center = (random.choice(LANE_CENTERS), random.randint(-2500, -1000))
        else:
            lane = random.randrange(LANES)
            self.rect.center = (LANE_CENTERS[lane], random.randint(-2500, -900))

    def update(self, road_speed: float, player: Player) -> None:
        """Move the event. Moving barrier also moves sideways."""
        self.rect.move_ip(0, road_speed)

        if self.kind == "moving_barrier":
            self.rect.move_ip(self.direction * 2.5, 0)
            if self.rect.left < ROAD_X or self.rect.right > ROAD_X + ROAD_WIDTH:
                self.direction *= -1

        if self.rect.top > SCREEN_HEIGHT:
            self.reset(player)


def draw_road(screen: pygame.Surface, line_offset: float) -> None:
    """Draw scrolling road and lane markings."""
    screen.fill((35, 140, 65))
    pygame.draw.rect(screen, ROAD_GRAY, (ROAD_X, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_X - 6, 0, 6, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WHITE, (ROAD_X + ROAD_WIDTH, 0, 6, SCREEN_HEIGHT))

    # Lane dividers scroll downward.
    for i in range(1, LANES):
        x = ROAD_X + i * LANE_WIDTH
        y = -80 + int(line_offset) % 80
        while y < SCREEN_HEIGHT:
            pygame.draw.rect(screen, WHITE, (x - 3, y, 6, 45), border_radius=3)
            y += 80


def draw_hud(
    screen: pygame.Surface,
    coins_collected: int,
    coin_score: int,
    score: int,
    distance: float,
    active_power: str | None,
    power_end_time: float,
    shield_ready: bool,
) -> None:
    """Draw score, coins, distance, and active power-up information."""
    score_text = FONT_SMALL.render(f"Score: {score}", True, WHITE)
    coins_text = FONT_SMALL.render(f"Coins: {coins_collected}  Value: {coin_score}", True, WHITE)
    dist_text = FONT_SMALL.render(f"Distance: {int(distance)}m / {FINISH_DISTANCE}m", True, WHITE)

    screen.blit(score_text, (12, 10))
    screen.blit(coins_text, (12, 35))
    screen.blit(dist_text, (12, 60))

    remaining = max(0, FINISH_DISTANCE - int(distance))
    remain_text = FONT_SMALL.render(f"Remaining: {remaining}m", True, WHITE)
    screen.blit(remain_text, (SCREEN_WIDTH - remain_text.get_width() - 12, 10))

    if active_power == "nitro":
        time_left = max(0, power_end_time - time.time())
        power_text = FONT_SMALL.render(f"Power: NITRO {time_left:.1f}s", True, CYAN)
    elif active_power == "shield" or shield_ready:
        power_text = FONT_SMALL.render("Power: SHIELD ready", True, BLUE)
    else:
        power_text = FONT_SMALL.render("Power: none", True, WHITE)

    screen.blit(power_text, (SCREEN_WIDTH - power_text.get_width() - 12, 35))


def calculate_score(distance: float, coin_score: int, power_bonus: int) -> int:
    """Combine distance, weighted coins, and power-up bonuses."""
    return int(distance) + coin_score * 20 + power_bonus


def clear_near_player(player: Player, obstacles: pygame.sprite.Group, traffic: pygame.sprite.Group) -> int:
    """Repair effect: remove one dangerous object near the player."""
    candidates = []
    for group in [obstacles, traffic]:
        for sprite in group:
            if abs(sprite.rect.centery - player.rect.centery) < 240:
                candidates.append(sprite)

    if not candidates:
        return 0

    target = min(candidates, key=lambda sprite: abs(sprite.rect.centery - player.rect.centery))
    if hasattr(target, "reset"):
        target.reset(player)
    return 50


def run_game(screen: pygame.Surface, clock: pygame.time.Clock, settings: dict[str, Any], username: str) -> dict[str, Any]:
    """Run one race and return result data for leaderboard/game-over screen."""
    difficulty = DIFFICULTY_DATA.get(settings.get("difficulty", "normal"), DIFFICULTY_DATA["normal"])
    car_color = CAR_COLORS.get(settings.get("car_color", "blue"), BLUE)

    player = Player(car_color)

    traffic = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    road_events = pygame.sprite.Group()

    # Starting objects. More will be added as difficulty scales.
    for _ in range(difficulty["start_traffic"]):
        traffic.add(TrafficCar(player, 5))
    for _ in range(4):
        coins.add(Coin(player))
    for _ in range(2):
        obstacles.add(Obstacle(player))
    powerups.add(PowerUp(player))
    road_events.add(RoadEvent(player))

    base_road_speed = 5.0 * difficulty["speed_factor"]
    enemy_speed_bonus = 0.0
    distance = 0.0
    line_offset = 0.0

    coins_collected = 0
    coin_score = 0
    power_bonus = 0
    score = 0

    active_power: str | None = None
    power_end_time = 0.0
    shield_ready = False
    slowed_until = 0.0

    start_ticks = pygame.time.get_ticks()

    while True:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == KEYDOWN:
                if event.key in (K_LEFT, K_a):
                    player.change_lane(-1)
                if event.key in (K_RIGHT, K_d):
                    player.change_lane(1)
                if event.key == K_ESCAPE:
                    return {
                        "name": username,
                        "score": score,
                        "distance": int(distance),
                        "coins": coins_collected,
                        "finished": False,
                    }

        # Active power-up timer.
        if active_power == "nitro" and time.time() > power_end_time:
            active_power = None

        nitro_multiplier = 1.55 if active_power == "nitro" else 1.0
        slow_multiplier = 0.55 if time.time() < slowed_until else 1.0
        road_speed = (base_road_speed + enemy_speed_bonus + distance / 1600) * nitro_multiplier * slow_multiplier

        # Distance and score.
        distance += road_speed * 6 * dt
        line_offset += road_speed
        score = calculate_score(distance, coin_score, power_bonus)

        # Difficulty scaling: add more traffic and obstacles as distance increases.
        target_traffic = min(7, difficulty["start_traffic"] + int(distance // 900))
        target_obstacles = min(6, 2 + int(distance // 1200))
        if len(traffic) < target_traffic:
            traffic.add(TrafficCar(player, road_speed))
        if len(obstacles) < target_obstacles:
            obstacles.add(Obstacle(player))
        if distance > 1500 and len(road_events) < 2:
            road_events.add(RoadEvent(player))

        # Update objects.
        player.move()
        traffic.update(road_speed, player)
        coins.update(road_speed, player)
        obstacles.update(road_speed, player)
        powerups.update(road_speed, player)
        road_events.update(road_speed, player)

        # Coin collection. Weighted coins affect score value.
        touched_coins = pygame.sprite.spritecollide(player, coins, False)
        old_coin_count = coins_collected
        for coin in touched_coins:
            coins_collected += 1
            coin_score += coin.weight
            coin.reset(player)

        # Increase enemy/road speed after collecting every N coins.
        old_level = old_coin_count // SPEED_UP_EVERY_COINS
        new_level = coins_collected // SPEED_UP_EVERY_COINS
        if new_level > old_level:
            enemy_speed_bonus += 0.45

        # Power-up collection. Only one can be active at a time.
        touched_powerups = pygame.sprite.spritecollide(player, powerups, False)
        for power in touched_powerups:
            if power.kind == "repair":
                power_bonus += clear_near_player(player, obstacles, traffic) + 100
            elif active_power is None and not shield_ready:
                if power.kind == "nitro":
                    active_power = "nitro"
                    power_end_time = time.time() + random.uniform(3.0, 5.0)
                    power_bonus += 75
                elif power.kind == "shield":
                    active_power = "shield"
                    shield_ready = True
                    power_bonus += 75
            power.reset(player)

        # Road events.
        touched_events = pygame.sprite.spritecollide(player, road_events, False)
        for event in touched_events:
            if event.kind == "nitro_strip" and active_power is None and not shield_ready:
                active_power = "nitro"
                power_end_time = time.time() + 3.5
                power_bonus += 60
                event.reset(player)
            elif event.kind == "speed_bump":
                slowed_until = time.time() + 1.6
                event.reset(player)
            elif event.kind == "moving_barrier":
                if shield_ready:
                    shield_ready = False
                    active_power = None
                    event.reset(player)
                else:
                    return {
                        "name": username,
                        "score": score,
                        "distance": int(distance),
                        "coins": coins_collected,
                        "finished": False,
                    }

        # Obstacle collisions.
        touched_obstacles = pygame.sprite.spritecollide(player, obstacles, False)
        for obstacle in touched_obstacles:
            if obstacle.kind == "oil":
                slowed_until = time.time() + 2.0
                obstacle.reset(player)
            else:
                if shield_ready:
                    shield_ready = False
                    active_power = None
                    obstacle.reset(player)
                else:
                    return {
                        "name": username,
                        "score": score,
                        "distance": int(distance),
                        "coins": coins_collected,
                        "finished": False,
                    }

        # Traffic collisions.
        touched_traffic = pygame.sprite.spritecollide(player, traffic, False)
        if touched_traffic:
            if shield_ready:
                shield_ready = False
                active_power = None
                for car in touched_traffic:
                    car.reset(player)
            else:
                return {
                    "name": username,
                    "score": score,
                    "distance": int(distance),
                    "coins": coins_collected,
                    "finished": False,
                }

        # Finish line condition.
        if distance >= FINISH_DISTANCE:
            score += 1000
            return {
                "name": username,
                "score": score,
                "distance": int(distance),
                "coins": coins_collected,
                "finished": True,
            }

        # Draw everything.
        draw_road(screen, line_offset)

        for group in [coins, powerups, obstacles, road_events, traffic]:
            for sprite in group:
                screen.blit(sprite.image, sprite.rect)

        # Shield visual effect around the player.
        if shield_ready:
            pygame.draw.circle(screen, CYAN, player.rect.center, 56, 3)

        screen.blit(player.image, player.rect)

        draw_hud(screen, coins_collected, coin_score, score, distance, active_power, power_end_time, shield_ready)

        # Tiny help text.
        if pygame.time.get_ticks() - start_ticks < 4000:
            help_text = FONT_TINY.render("Use LEFT/RIGHT or A/D. Avoid traffic and barriers.", True, WHITE)
            screen.blit(help_text, help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)))

        pygame.display.update()
