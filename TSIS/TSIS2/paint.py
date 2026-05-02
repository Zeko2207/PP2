"""TSIS 2 Paint Application with extended drawing tools."""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from tools import (
    BLACK,
    BLUE,
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    DARK_GRAY,
    FPS,
    GRAY,
    LIGHT_GRAY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TOOLBAR_HEIGHT,
    WHITE,
    Button,
    BRUSH_SIZES,
    clamp_canvas_pos,
    draw_grid,
    draw_shape,
    flood_fill,
    is_on_canvas,
    make_toolbar_buttons,
    save_canvas,
    to_canvas_pos,
)


class PaintApp:
    """Main Paint application class."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("TSIS 2 Paint Application")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # The canvas is a separate surface. Only this surface is saved as an image.
        self.canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(WHITE)

        self.font = pygame.font.SysFont("Verdana", 14)
        self.small_font = pygame.font.SysFont("Verdana", 12)
        self.text_font = pygame.font.SysFont("Verdana", 26)

        self.tool_buttons, self.size_buttons, self.color_buttons = make_toolbar_buttons()

        self.active_tool = "pencil"
        self.current_color = BLACK
        self.brush_size = BRUSH_SIZES["Medium"]

        self.drawing = False
        self.start_pos: tuple[int, int] | None = None
        self.last_pos: tuple[int, int] | None = None
        self.current_mouse_canvas_pos: tuple[int, int] | None = None

        # Text tool state
        self.text_active = False
        self.text_pos: tuple[int, int] | None = None
        self.text_buffer = ""

        self.status_message = "Ready"
        self.show_grid = False

        self.output_dir = Path("saved_images")

    def run(self) -> None:
        """Run the main event loop."""
        while True:
            self.handle_events()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

    # -----------------------------
    # Event handling
    # -----------------------------
    def handle_events(self) -> None:
        """Handle keyboard, mouse, and quit events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_app()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_mouse_down(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event.pos)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.handle_mouse_up(event.pos)

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard shortcuts and typing for the text tool."""
        # Ctrl+S saves the canvas as a timestamped PNG.
        if event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
            filename = save_canvas(self.canvas, self.output_dir)
            self.status_message = f"Saved: {filename}"
            return

        # Numbers 1, 2, 3 switch brush thickness.
        if event.key == pygame.K_1:
            self.brush_size = BRUSH_SIZES["Small"]
            self.status_message = "Brush size: small"
            return
        if event.key == pygame.K_2:
            self.brush_size = BRUSH_SIZES["Medium"]
            self.status_message = "Brush size: medium"
            return
        if event.key == pygame.K_3:
            self.brush_size = BRUSH_SIZES["Large"]
            self.status_message = "Brush size: large"
            return

        # G toggles a helper grid. It is not saved on the canvas.
        if event.key == pygame.K_g:
            self.show_grid = not self.show_grid
            self.status_message = f"Grid: {'on' if self.show_grid else 'off'}"
            return

        # Text input mode: type, confirm with Enter, cancel with Escape.
        if self.text_active:
            if event.key == pygame.K_RETURN:
                self.commit_text()
            elif event.key == pygame.K_ESCAPE:
                self.cancel_text()
            elif event.key == pygame.K_BACKSPACE:
                self.text_buffer = self.text_buffer[:-1]
            else:
                self.text_buffer += event.unicode

    def handle_mouse_down(self, pos: tuple[int, int]) -> None:
        """Handle a left mouse click."""
        if self.handle_toolbar_click(pos):
            return

        if not is_on_canvas(pos):
            return

        canvas_pos = to_canvas_pos(pos)
        canvas_pos = clamp_canvas_pos(canvas_pos)

        if self.active_tool == "fill":
            flood_fill(self.canvas, canvas_pos, self.current_color)
            self.status_message = "Flood fill applied"
            return

        if self.active_tool == "picker":
            picked = self.canvas.get_at(canvas_pos)
            self.current_color = (picked.r, picked.g, picked.b)
            self.status_message = f"Picked color: {self.current_color}"
            return

        if self.active_tool == "text":
            self.text_active = True
            self.text_pos = canvas_pos
            self.text_buffer = ""
            self.status_message = "Typing text: Enter = confirm, Esc = cancel"
            return

        self.drawing = True
        self.start_pos = canvas_pos
        self.last_pos = canvas_pos
        self.current_mouse_canvas_pos = canvas_pos

        # Pencil and eraser should start drawing immediately.
        if self.active_tool in ("pencil", "eraser"):
            color = WHITE if self.active_tool == "eraser" else self.current_color
            pygame.draw.circle(self.canvas, color, canvas_pos, max(1, self.brush_size // 2))

    def handle_mouse_motion(self, pos: tuple[int, int]) -> None:
        """Draw freehand strokes or update shape preview while the mouse moves."""
        if not is_on_canvas(pos):
            return

        canvas_pos = to_canvas_pos(pos)
        canvas_pos = clamp_canvas_pos(canvas_pos)
        self.current_mouse_canvas_pos = canvas_pos

        if not self.drawing:
            return

        if self.active_tool in ("pencil", "eraser") and self.last_pos is not None:
            color = WHITE if self.active_tool == "eraser" else self.current_color
            pygame.draw.line(self.canvas, color, self.last_pos, canvas_pos, self.brush_size)
            pygame.draw.circle(self.canvas, color, canvas_pos, max(1, self.brush_size // 2))
            self.last_pos = canvas_pos

    def handle_mouse_up(self, pos: tuple[int, int]) -> None:
        """Finish drawing a shape when the mouse button is released."""
        if not self.drawing:
            return

        self.drawing = False

        if not is_on_canvas(pos):
            return

        end_pos = clamp_canvas_pos(to_canvas_pos(pos))

        if self.start_pos is None:
            return

        if self.active_tool not in ("pencil", "eraser"):
            draw_shape(
                self.canvas,
                self.active_tool,
                self.start_pos,
                end_pos,
                self.current_color,
                self.brush_size,
            )

        self.start_pos = None
        self.last_pos = None
        self.current_mouse_canvas_pos = None

    def handle_toolbar_click(self, pos: tuple[int, int]) -> bool:
        """Check whether the user clicked a toolbar button."""
        for button in self.tool_buttons:
            if button.is_clicked(pos):
                self.active_tool = str(button.value)
                self.cancel_text()
                self.status_message = f"Tool: {button.text}"
                return True

        for button in self.size_buttons:
            if button.is_clicked(pos):
                self.brush_size = int(button.value)
                self.status_message = f"Brush size: {self.brush_size}px"
                return True

        for button in self.color_buttons:
            if button.is_clicked(pos):
                self.current_color = button.value  # type: ignore[assignment]
                self.status_message = f"Color: {self.current_color}"
                return True

        return False

    # -----------------------------
    # Text tool
    # -----------------------------
    def commit_text(self) -> None:
        """Render typed text permanently onto the canvas."""
        if self.text_pos is not None and self.text_buffer:
            text_surface = self.text_font.render(self.text_buffer, True, self.current_color)
            self.canvas.blit(text_surface, self.text_pos)
            self.status_message = "Text added to canvas"
        self.cancel_text(clear_status=False)

    def cancel_text(self, *, clear_status: bool = True) -> None:
        """Cancel the current text placement."""
        self.text_active = False
        self.text_pos = None
        self.text_buffer = ""
        if clear_status:
            self.status_message = "Text cancelled"

    # -----------------------------
    # Drawing
    # -----------------------------
    def draw(self) -> None:
        """Draw the toolbar, canvas, previews, and status text."""
        self.screen.fill(GRAY)
        self.draw_toolbar()

        # Work on a preview copy so shape preview does not permanently affect the canvas.
        preview_canvas = self.canvas.copy()

        if self.show_grid:
            draw_grid(preview_canvas)

        if (
            self.drawing
            and self.active_tool not in ("pencil", "eraser")
            and self.start_pos is not None
            and self.current_mouse_canvas_pos is not None
        ):
            draw_shape(
                preview_canvas,
                self.active_tool,
                self.start_pos,
                self.current_mouse_canvas_pos,
                self.current_color,
                self.brush_size,
            )

        if self.text_active and self.text_pos is not None:
            self.draw_text_preview(preview_canvas)

        self.screen.blit(preview_canvas, (0, TOOLBAR_HEIGHT))
        pygame.draw.rect(self.screen, DARK_GRAY, (0, TOOLBAR_HEIGHT, CANVAS_WIDTH, CANVAS_HEIGHT), 2)

    def draw_toolbar(self) -> None:
        """Draw all toolbar controls."""
        pygame.draw.rect(self.screen, LIGHT_GRAY, (0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(self.screen, DARK_GRAY, (0, TOOLBAR_HEIGHT - 1), (SCREEN_WIDTH, TOOLBAR_HEIGHT - 1), 2)

        for button in self.tool_buttons:
            button.draw(
                self.screen,
                self.small_font,
                active=(button.value == self.active_tool),
            )

        for button in self.size_buttons:
            button.draw(
                self.screen,
                self.small_font,
                active=(int(button.value) == self.brush_size),
            )

        for button in self.color_buttons:
            button.draw(
                self.screen,
                self.small_font,
                active=(button.value == self.current_color),
                fill_color=button.value,  # type: ignore[arg-type]
            )

        # Current color preview
        pygame.draw.rect(self.screen, self.current_color, (670, 88, 40, 22))
        pygame.draw.rect(self.screen, DARK_GRAY, (670, 88, 40, 22), 1)
        label = self.small_font.render(f"Tool: {self.active_tool} | Size: {self.brush_size}px", True, BLACK)
        self.screen.blit(label, (720, 89))

        hints = "Shortcuts: 1/2/3 = size, G = grid, Ctrl+S = save PNG"
        hints_surf = self.small_font.render(hints, True, DARK_GRAY)
        self.screen.blit(hints_surf, (10, 86))

        status = self.small_font.render(self.status_message, True, BLUE)
        self.screen.blit(status, (10, 102))

    def draw_text_preview(self, surface: pygame.Surface) -> None:
        """Show temporary text before Enter confirms it."""
        assert self.text_pos is not None
        display_text = self.text_buffer + "|"
        text_surface = self.text_font.render(display_text, True, self.current_color)
        surface.blit(text_surface, self.text_pos)

    def quit_app(self) -> None:
        """Close pygame and exit the program."""
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    PaintApp().run()
