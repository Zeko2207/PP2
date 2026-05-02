"""Helper tools for the TSIS 2 Paint application."""

from __future__ import annotations

from collections import deque
from datetime import datetime
from pathlib import Path
import math
from typing import Iterable

import pygame

# Window and canvas settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TOOLBAR_HEIGHT = 120
CANVAS_WIDTH = SCREEN_WIDTH
CANVAS_HEIGHT = SCREEN_HEIGHT - TOOLBAR_HEIGHT
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (80, 80, 80)
LIGHT_GRAY = (235, 235, 235)
BLUE = (60, 130, 240)
GREEN = (30, 170, 90)
RED = (220, 50, 50)
YELLOW = (245, 210, 50)
ORANGE = (245, 150, 40)
PURPLE = (150, 80, 200)
PINK = (255, 130, 180)
BROWN = (145, 90, 45)

COLOR_PALETTE = [
    BLACK,
    RED,
    ORANGE,
    YELLOW,
    GREEN,
    BLUE,
    PURPLE,
    PINK,
    BROWN,
    WHITE,
]

TOOLS = [
    ("pencil", "Pencil"),
    ("line", "Line"),
    ("rect", "Rect"),
    ("circle", "Circle"),
    ("eraser", "Eraser"),
    ("fill", "Fill"),
    ("text", "Text"),
    ("picker", "Picker"),
    ("square", "Square"),
    ("right_triangle", "R.Tri"),
    ("equilateral_triangle", "Eq.Tri"),
    ("rhombus", "Rhombus"),
]

BRUSH_SIZES = {
    "Small": 2,
    "Medium": 5,
    "Large": 10,
}


class Button:
    """Simple rectangular button drawn with pygame."""

    def __init__(self, rect: pygame.Rect, text: str, value: str | tuple[int, int, int]):
        self.rect = rect
        self.text = text
        self.value = value

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        *,
        active: bool = False,
        fill_color: tuple[int, int, int] | None = None,
    ) -> None:
        """Draw the button on a surface."""
        color = fill_color if fill_color is not None else (250, 250, 250)
        border_color = BLUE if active else DARK_GRAY
        border_width = 3 if active else 1

        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=6)

        if self.text:
            text_color = BLACK if fill_color != BLACK else WHITE
            text_surf = font.render(self.text, True, text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, text_rect)

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        """Return True if mouse position is inside the button."""
        return self.rect.collidepoint(pos)


def make_toolbar_buttons() -> tuple[list[Button], list[Button], list[Button]]:
    """Create tool buttons, brush size buttons, and color buttons."""
    tool_buttons: list[Button] = []
    size_buttons: list[Button] = []
    color_buttons: list[Button] = []

    x = 10
    y = 10
    w = 75
    h = 30
    gap = 6

    for index, (tool_id, label) in enumerate(TOOLS):
        row = index // 8
        col = index % 8
        rect = pygame.Rect(x + col * (w + gap), y + row * (h + gap), w, h)
        tool_buttons.append(Button(rect, label, tool_id))

    size_x = 670
    for i, (label, value) in enumerate(BRUSH_SIZES.items()):
        rect = pygame.Rect(size_x + i * 88, 10, 80, 30)
        size_buttons.append(Button(rect, f"{label[0]}: {value}", str(value)))

    color_x = 670
    color_y = 55
    color_size = 25
    for i, color in enumerate(COLOR_PALETTE):
        rect = pygame.Rect(color_x + i * (color_size + 6), color_y, color_size, color_size)
        color_buttons.append(Button(rect, "", color))

    return tool_buttons, size_buttons, color_buttons


def is_on_canvas(pos: tuple[int, int]) -> bool:
    """Check if a screen position is inside the drawing canvas."""
    x, y = pos
    return 0 <= x < CANVAS_WIDTH and TOOLBAR_HEIGHT <= y < SCREEN_HEIGHT


def to_canvas_pos(pos: tuple[int, int]) -> tuple[int, int]:
    """Convert screen coordinates to canvas coordinates."""
    x, y = pos
    return x, y - TOOLBAR_HEIGHT


def clamp_canvas_pos(pos: tuple[int, int]) -> tuple[int, int]:
    """Keep a canvas position inside the canvas bounds."""
    x, y = pos
    x = max(0, min(CANVAS_WIDTH - 1, x))
    y = max(0, min(CANVAS_HEIGHT - 1, y))
    return x, y


def normalized_rect(start: tuple[int, int], end: tuple[int, int]) -> pygame.Rect:
    """Create a pygame.Rect from two opposite corners."""
    x1, y1 = start
    x2, y2 = end
    return pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def square_rect(start: tuple[int, int], end: tuple[int, int]) -> pygame.Rect:
    """Create a square rectangle from start point and current mouse point."""
    x1, y1 = start
    x2, y2 = end
    side = min(abs(x2 - x1), abs(y2 - y1))

    if x2 < x1:
        x1 -= side
    if y2 < y1:
        y1 -= side

    return pygame.Rect(x1, y1, side, side)


def right_triangle_points(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Return three points for a right triangle."""
    x1, y1 = start
    x2, y2 = end
    return [(x1, y1), (x1, y2), (x2, y2)]


def equilateral_triangle_points(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Return approximate points for an equilateral triangle."""
    x1, y1 = start
    x2, y2 = end
    side = x2 - x1
    if side == 0:
        side = 1

    direction = 1 if side > 0 else -1
    side_abs = abs(side)
    height = int(math.sqrt(3) / 2 * side_abs)

    base_left = (x1, y2)
    base_right = (x1 + direction * side_abs, y2)
    top = (x1 + direction * side_abs // 2, y2 - height if y2 >= y1 else y2 + height)

    return [top, base_left, base_right]


def rhombus_points(start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    """Return four points for a rhombus inside the drag rectangle."""
    rect = normalized_rect(start, end)
    center_x = rect.centerx
    center_y = rect.centery
    return [
        (center_x, rect.top),
        (rect.right, center_y),
        (center_x, rect.bottom),
        (rect.left, center_y),
    ]


def draw_shape(
    surface: pygame.Surface,
    tool: str,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    brush_size: int,
) -> None:
    """Draw one of the supported shape tools on the canvas."""
    start = clamp_canvas_pos(start)
    end = clamp_canvas_pos(end)

    if tool == "line":
        pygame.draw.line(surface, color, start, end, brush_size)

    elif tool == "rect":
        rect = normalized_rect(start, end)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == "circle":
        x1, y1 = start
        x2, y2 = end
        radius = int(math.hypot(x2 - x1, y2 - y1))
        if radius > 0:
            pygame.draw.circle(surface, color, start, radius, brush_size)

    elif tool == "square":
        rect = square_rect(start, end)
        if rect.width > 0 and rect.height > 0:
            pygame.draw.rect(surface, color, rect, brush_size)

    elif tool == "right_triangle":
        points = right_triangle_points(start, end)
        pygame.draw.polygon(surface, color, points, brush_size)

    elif tool == "equilateral_triangle":
        points = equilateral_triangle_points(start, end)
        pygame.draw.polygon(surface, color, points, brush_size)

    elif tool == "rhombus":
        points = rhombus_points(start, end)
        pygame.draw.polygon(surface, color, points, brush_size)


def flood_fill(surface: pygame.Surface, start_pos: tuple[int, int], fill_color: tuple[int, int, int]) -> None:
    """
    Fill a closed region using exact-color flood fill.

    It reads pixels with get_at() and writes pixels with set_at(), as required.
    """
    start_pos = clamp_canvas_pos(start_pos)
    width, height = surface.get_size()
    target_color = surface.get_at(start_pos)
    replacement_color = pygame.Color(*fill_color)

    if target_color == replacement_color:
        return

    queue: deque[tuple[int, int]] = deque([start_pos])
    visited: set[tuple[int, int]] = set()

    surface.lock()
    try:
        while queue:
            x, y = queue.popleft()

            if (x, y) in visited:
                continue
            visited.add((x, y))

            if x < 0 or x >= width or y < 0 or y >= height:
                continue

            if surface.get_at((x, y)) != target_color:
                continue

            surface.set_at((x, y), replacement_color)

            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))
    finally:
        surface.unlock()


def save_canvas(canvas: pygame.Surface, directory: str | Path = ".") -> Path:
    """Save the canvas to a timestamped PNG file."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = directory / f"paint_{timestamp}.png"
    pygame.image.save(canvas, str(filename))
    return filename


def draw_grid(surface: pygame.Surface, grid_size: int = 25) -> None:
    """Draw a light grid on top of the canvas preview."""
    for x in range(0, CANVAS_WIDTH, grid_size):
        pygame.draw.line(surface, (230, 230, 230), (x, 0), (x, CANVAS_HEIGHT))
    for y in range(0, CANVAS_HEIGHT, grid_size):
        pygame.draw.line(surface, (230, 230, 230), (0, y), (CANVAS_WIDTH, y))
