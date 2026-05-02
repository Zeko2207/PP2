import pygame
import sys
from datetime import datetime

from tools import draw_toolbar, draw_shape, flood_fill

WIDTH = 1000
HEIGHT = 700
TOOLBAR_HEIGHT = 80

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
GREEN = (0, 160, 0)
BLUE = (0, 0, 220)
YELLOW = (240, 200, 0)

BRUSH_SIZES = {
    "small": 2,
    "medium": 5,
    "large": 10
}


def save_canvas(canvas):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"paint_{timestamp}.png"
    pygame.image.save(canvas, filename)
    return filename


def main():
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("TSIS2 Paint Application")

    font = pygame.font.SysFont(None, 24)
    text_font = pygame.font.SysFont(None, 36)

    canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_HEIGHT))
    canvas.fill(WHITE)

    current_tool = "pencil"
    current_color = BLACK
    brush_size = BRUSH_SIZES["medium"]

    drawing = False
    start_pos = None
    last_pos = None

    text_mode = False
    text_pos = None
    text_value = ""

    saved_message = ""
    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        canvas_mouse_pos = (mouse_x, mouse_y - TOOLBAR_HEIGHT)

        if drawing and start_pos is not None and current_tool in (
            "line", "rectangle", "circle", "square",
            "right_triangle", "equilateral_triangle", "rhombus"
        ):
            preview_canvas = canvas.copy()
            draw_shape(preview_canvas, current_tool, start_pos, canvas_mouse_pos, current_color, brush_size)
            screen.blit(preview_canvas, (0, TOOLBAR_HEIGHT))

        if text_mode and text_pos is not None:
            text_surface = text_font.render(text_value, True, current_color)
            screen.blit(text_surface, (text_pos[0], text_pos[1] + TOOLBAR_HEIGHT))

        draw_toolbar(screen, font, current_tool, current_color, brush_size, saved_message)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    if event.key == pygame.K_s:
                        filename = save_canvas(canvas)
                        saved_message = f"Saved: {filename}"
                        continue

                if text_mode:
                    if event.key == pygame.K_RETURN:
                        text_surface = text_font.render(text_value, True, current_color)
                        canvas.blit(text_surface, text_pos)
                        text_mode = False
                        text_pos = None
                        text_value = ""
                        continue
                    elif event.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_pos = None
                        text_value = ""
                        continue
                    elif event.key == pygame.K_BACKSPACE:
                        text_value = text_value[:-1]
                        continue
                    else:
                        text_value += event.unicode
                        continue

                if event.key == pygame.K_p:
                    current_tool = "pencil"
                elif event.key == pygame.K_l:
                    current_tool = "line"
                elif event.key == pygame.K_r:
                    current_tool = "rectangle"
                elif event.key == pygame.K_c:
                    current_tool = "circle"
                elif event.key == pygame.K_e:
                    current_tool = "eraser"
                elif event.key == pygame.K_s:
                    current_tool = "square"
                elif event.key == pygame.K_4:
                    current_tool = "right_triangle"
                elif event.key == pygame.K_5:
                    current_tool = "equilateral_triangle"
                elif event.key == pygame.K_6:
                    current_tool = "rhombus"
                elif event.key == pygame.K_f:
                    current_tool = "fill"
                elif event.key == pygame.K_t:
                    current_tool = "text"
                elif event.key == pygame.K_1:
                    brush_size = BRUSH_SIZES["small"]
                elif event.key == pygame.K_2:
                    brush_size = BRUSH_SIZES["medium"]
                elif event.key == pygame.K_3:
                    brush_size = BRUSH_SIZES["large"]
                elif event.key == pygame.K_b:
                    current_color = BLACK
                elif event.key == pygame.K_g:
                    current_color = GREEN
                elif event.key == pygame.K_u:
                    current_color = BLUE
                elif event.key == pygame.K_y:
                    current_color = YELLOW
                elif event.key == pygame.K_d:
                    current_color = RED

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    if y < TOOLBAR_HEIGHT:
                        continue

                    canvas_pos = (x, y - TOOLBAR_HEIGHT)

                    if current_tool == "fill":
                        flood_fill(canvas, canvas_pos, current_color)
                    elif current_tool == "text":
                        text_mode = True
                        text_pos = canvas_pos
                        text_value = ""
                    elif current_tool == "pencil":
                        drawing = True
                        last_pos = canvas_pos
                    elif current_tool == "eraser":
                        drawing = True
                        last_pos = canvas_pos
                    else:
                        drawing = True
                        start_pos = canvas_pos

            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    x, y = event.pos
                    if y < TOOLBAR_HEIGHT:
                        continue

                    canvas_pos = (x, y - TOOLBAR_HEIGHT)

                    if current_tool == "pencil" and last_pos is not None:
                        pygame.draw.line(canvas, current_color, last_pos, canvas_pos, brush_size)
                        last_pos = canvas_pos
                    elif current_tool == "eraser" and last_pos is not None:
                        pygame.draw.line(canvas, WHITE, last_pos, canvas_pos, brush_size)
                        last_pos = canvas_pos

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and drawing:
                    x, y = event.pos
                    if y >= TOOLBAR_HEIGHT:
                        end_pos = (x, y - TOOLBAR_HEIGHT)
                        if current_tool in (
                            "line", "rectangle", "circle", "square",
                            "right_triangle", "equilateral_triangle", "rhombus"
                        ):
                            draw_shape(canvas, current_tool, start_pos, end_pos, current_color, brush_size)

                    drawing = False
                    start_pos = None
                    last_pos = None

        clock.tick(60)


if __name__ == "__main__":
    main()