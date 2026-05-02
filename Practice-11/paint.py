import pygame
import math

pygame.init()

# -------------------- SCREEN SETTINGS --------------------

WIDTH, HEIGHT = 900, 600
TOOLBAR_HEIGHT = 90

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint Project")

clock = pygame.time.Clock()

# -------------------- COLORS --------------------

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (210, 210, 210)
DARK_GRAY = (80, 80, 80)

RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 220, 0)
PURPLE = (160, 60, 200)
ORANGE = (255, 140, 0)

# Dictionary for color selection
COLORS = {
    "K": BLACK,
    "R": RED,
    "G": GREEN,
    "B": BLUE,
    "Y": YELLOW,
    "P": PURPLE,
    "O": ORANGE,
    "W": WHITE,
}

# -------------------- CANVAS --------------------

# The canvas is a separate surface where all drawings are saved
canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
canvas.fill(WHITE)

# -------------------- GAME VARIABLES --------------------

current_color = BLACK
current_tool = "brush"

brush_size = 8
eraser_size = 30
shape_width = 3

drawing = False
start_pos = None
last_pos = None

font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)


# -------------------- HELPER FUNCTIONS --------------------

def is_inside_canvas(pos):
    """Check if the mouse position is inside the drawing area."""
    x, y = pos
    return 0 <= x < WIDTH and TOOLBAR_HEIGHT <= y < HEIGHT


def to_canvas_pos(pos):
    """Convert screen coordinates to canvas coordinates."""
    x, y = pos
    return x, y - TOOLBAR_HEIGHT


def get_rect(start, end):
    """Create a rectangle from two points."""
    x1, y1 = start
    x2, y2 = end

    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    return pygame.Rect(left, top, width, height)


def get_square_rect(start, end):
    """Create a square from two points."""
    x1, y1 = start
    x2, y2 = end

    dx = x2 - x1
    dy = y2 - y1

    # The side of a square must be equal in width and height
    side = max(abs(dx), abs(dy))

    if dx < 0:
        x2 = x1 - side
    else:
        x2 = x1 + side

    if dy < 0:
        y2 = y1 - side
    else:
        y2 = y1 + side

    return get_rect(start, (x2, y2))


def draw_smooth_line(surface, start, end, color, size):
    """Draw a smooth brush line between two points."""
    pygame.draw.line(surface, color, start, end, size)
    pygame.draw.circle(surface, color, start, size // 2)
    pygame.draw.circle(surface, color, end, size // 2)


def draw_shape(surface, tool, start, end, color):
    """Draw the selected shape on the surface."""

    if tool == "rectangle":
        rect = get_rect(start, end)
        pygame.draw.rect(surface, color, rect, shape_width)

    elif tool == "circle":
        # The first point is the center, the second point gives the radius
        x1, y1 = start
        x2, y2 = end
        radius = int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

        if radius > 0:
            pygame.draw.circle(surface, color, start, radius, shape_width)

    elif tool == "square":
        rect = get_square_rect(start, end)
        pygame.draw.rect(surface, color, rect, shape_width)

    elif tool == "right_triangle":
        x1, y1 = start
        x2, y2 = end

        # Three points form a right triangle
        points = [
            (x1, y1),
            (x1, y2),
            (x2, y2)
        ]

        pygame.draw.polygon(surface, color, points, shape_width)

    elif tool == "equilateral_triangle":
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        # Rotate the base vector by 60 degrees to get the third point
        angle = math.radians(60)

        x3 = x1 + dx * math.cos(angle) - dy * math.sin(angle)
        y3 = y1 + dx * math.sin(angle) + dy * math.cos(angle)

        points = [
            (x1, y1),
            (x2, y2),
            (int(x3), int(y3))
        ]

        pygame.draw.polygon(surface, color, points, shape_width)

    elif tool == "rhombus":
        rect = get_rect(start, end)

        # A rhombus can be drawn using the middle points of a rectangle
        points = [
            (rect.centerx, rect.top),
            (rect.right, rect.centery),
            (rect.centerx, rect.bottom),
            (rect.left, rect.centery)
        ]

        pygame.draw.polygon(surface, color, points, shape_width)


def draw_toolbar():
    """Draw the toolbar with instructions."""

    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, TOOLBAR_HEIGHT))

    tool_text = (
        "Tools: 1 Brush | 2 Rectangle | 3 Circle | 4 Eraser | "
        "5 Square | 6 Right Triangle | 7 Equilateral Triangle | 8 Rhombus"
    )

    color_text = "Colors: K Black | R Red | G Green | B Blue | Y Yellow | P Purple | O Orange | W White"

    info_text = f"Current tool: {current_tool}     Current color: {current_color}"

    screen.blit(font.render(tool_text, True, BLACK), (10, 10))
    screen.blit(font.render(color_text, True, BLACK), (10, 35))
    screen.blit(small_font.render(info_text, True, DARK_GRAY), (10, 65))


# -------------------- MAIN LOOP --------------------

running = True

while running:
    # Draw background and canvas
    screen.fill(WHITE)

    # Create preview canvas for shapes while dragging
    preview_canvas = canvas.copy()

    if drawing and start_pos is not None and current_tool not in ["brush", "eraser"]:
        mouse_pos = pygame.mouse.get_pos()

        if is_inside_canvas(mouse_pos):
            current_pos = to_canvas_pos(mouse_pos)
            draw_shape(preview_canvas, current_tool, start_pos, current_pos, current_color)

    # Show canvas
    screen.blit(preview_canvas, (0, TOOLBAR_HEIGHT))

    # Draw toolbar
    draw_toolbar()

    # -------------------- EVENTS --------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Keyboard controls
        if event.type == pygame.KEYDOWN:

            # Exit program
            if event.key == pygame.K_ESCAPE:
                running = False

            # Clear canvas
            elif event.key == pygame.K_c:
                canvas.fill(WHITE)

            # Tool selection
            elif event.key == pygame.K_1:
                current_tool = "brush"

            elif event.key == pygame.K_2:
                current_tool = "rectangle"

            elif event.key == pygame.K_3:
                current_tool = "circle"

            elif event.key == pygame.K_4:
                current_tool = "eraser"

            elif event.key == pygame.K_5:
                current_tool = "square"

            elif event.key == pygame.K_6:
                current_tool = "right_triangle"

            elif event.key == pygame.K_7:
                current_tool = "equilateral_triangle"

            elif event.key == pygame.K_8:
                current_tool = "rhombus"

            # Color selection
            elif event.key == pygame.K_k:
                current_color = BLACK

            elif event.key == pygame.K_r:
                current_color = RED

            elif event.key == pygame.K_g:
                current_color = GREEN

            elif event.key == pygame.K_b:
                current_color = BLUE

            elif event.key == pygame.K_y:
                current_color = YELLOW

            elif event.key == pygame.K_p:
                current_color = PURPLE

            elif event.key == pygame.K_o:
                current_color = ORANGE

            elif event.key == pygame.K_w:
                current_color = WHITE

            # Increase brush size
            elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                brush_size += 1
                eraser_size += 1

            # Decrease brush size
            elif event.key == pygame.K_MINUS:
                brush_size = max(1, brush_size - 1)
                eraser_size = max(5, eraser_size - 1)

        # Mouse button pressed
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and is_inside_canvas(event.pos):
                drawing = True
                start_pos = to_canvas_pos(event.pos)
                last_pos = start_pos

                # Draw one dot immediately for brush or eraser
                if current_tool == "brush":
                    pygame.draw.circle(canvas, current_color, start_pos, brush_size // 2)

                elif current_tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, start_pos, eraser_size // 2)

        # Mouse movement
        if event.type == pygame.MOUSEMOTION:
            if drawing and is_inside_canvas(event.pos):
                current_pos = to_canvas_pos(event.pos)

                # Brush draws while mouse is moving
                if current_tool == "brush":
                    draw_smooth_line(canvas, last_pos, current_pos, current_color, brush_size)
                    last_pos = current_pos

                # Eraser draws white color
                elif current_tool == "eraser":
                    draw_smooth_line(canvas, last_pos, current_pos, WHITE, eraser_size)
                    last_pos = current_pos

        # Mouse button released
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                if is_inside_canvas(event.pos):
                    end_pos = to_canvas_pos(event.pos)

                    # Finalize shape on the canvas
                    if current_tool not in ["brush", "eraser"]:
                        draw_shape(canvas, current_tool, start_pos, end_pos, current_color)

                drawing = False
                start_pos = None
                last_pos = None

    pygame.display.flip()
    clock.tick(60)

pygame.quit()