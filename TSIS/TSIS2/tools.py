import pygame
from collections import deque


def draw_toolbar(screen, font, tool_name, color, brush_size, saved_message):
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, screen.get_width(), 80))
    pygame.draw.line(screen, (120, 120, 120), (0, 80), (screen.get_width(), 80), 2)

    line1 = "Tools: P Pencil | L Line | R Rectangle | C Circle | E Eraser | S Square | F Fill | T Text"
    line2 = "Shapes: 4 Right triangle | 5 Equilateral triangle | 6 Rhombus"
    line3 = "Brush: 1 Small(2px) | 2 Medium(5px) | 3 Large(10px) | Colors: B Black G Green U Blue Y Yellow D Red | Ctrl+S Save"

    screen.blit(font.render(line1, True, (0, 0, 0)), (10, 8))
    screen.blit(font.render(line2, True, (0, 0, 0)), (10, 30))
    screen.blit(font.render(line3, True, (0, 0, 0)), (10, 52))

    status = f"Tool: {tool_name} | Brush: {brush_size}px | Color: {color}"
    screen.blit(font.render(status, True, (0, 0, 0)), (670, 8))

    if saved_message:
        screen.blit(font.render(saved_message, True, (0, 120, 0)), (670, 32))


def flood_fill(surface, start_pos, fill_color):
    width, height = surface.get_size()
    x, y = start_pos

    if x < 0 or x >= width or y < 0 or y >= height:
        return

    target_color = surface.get_at((x, y))

    if target_color == fill_color:
        return

    queue = deque([(x, y)])

    while queue:
        current_x, current_y = queue.popleft()

        if current_x < 0 or current_x >= width or current_y < 0 or current_y >= height:
            continue

        if surface.get_at((current_x, current_y)) != target_color:
            continue

        surface.set_at((current_x, current_y), fill_color)

        queue.append((current_x + 1, current_y))
        queue.append((current_x - 1, current_y))
        queue.append((current_x, current_y + 1))
        queue.append((current_x, current_y - 1))


def draw_right_triangle(surface, start, end, color, brush_size):
    x1, y1 = start
    x2, y2 = end
    points = [(x1, y1), (x1, y2), (x2, y2)]
    pygame.draw.polygon(surface, color, points, brush_size)


def draw_equilateral_triangle(surface, start, end, color, brush_size):
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    middle_x = (left + right) // 2

    points = [(middle_x, top), (left, bottom), (right, bottom)]
    pygame.draw.polygon(surface, color, points, brush_size)


def draw_rhombus(surface, start, end, color, brush_size):
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    middle_x = (left + right) // 2
    middle_y = (top + bottom) // 2

    points = [(middle_x, top), (right, middle_y), (middle_x, bottom), (left, middle_y)]
    pygame.draw.polygon(surface, color, points, brush_size)


def draw_shape(surface, tool, start, end, color, brush_size):
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    rect = pygame.Rect(left, top, width, height)

    if tool == "line":
        pygame.draw.line(surface, color, start, end, brush_size)
    elif tool == "rectangle":
        pygame.draw.rect(surface, color, rect, brush_size)
    elif tool == "circle":
        radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
        pygame.draw.circle(surface, color, start, radius, brush_size)
    elif tool == "square":
        side = min(width, height)
        square_x = x1 - side if x2 < x1 else x1
        square_y = y1 - side if y2 < y1 else y1
        square_rect = pygame.Rect(square_x, square_y, side, side)
        pygame.draw.rect(surface, color, square_rect, brush_size)
    elif tool == "right_triangle":
        draw_right_triangle(surface, start, end, color, brush_size)
    elif tool == "equilateral_triangle":
        draw_equilateral_triangle(surface, start, end, color, brush_size)
    elif tool == "rhombus":
        draw_rhombus(surface, start, end, color, brush_size)