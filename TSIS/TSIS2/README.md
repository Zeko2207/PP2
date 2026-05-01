# TSIS 2 Paint Application

Extended Paint application made with Pygame only.

## Features

- Pencil freehand drawing tool
- Straight line tool with live preview
- Rectangle, circle, square, right triangle, equilateral triangle, and rhombus tools
- Eraser
- Color picker
- Flood-fill tool using `Surface.get_at()` and `Surface.set_at()`
- Text tool: click, type, Enter to confirm, Escape to cancel
- Three brush sizes: 2 px, 5 px, 10 px
- Brush size applies to pencil, line, rectangle, circle, and all shapes
- Ctrl+S saves the canvas as a timestamped PNG into `saved_images/`

## How to run

```bash
cd TSIS2
python3 -m pip install pygame
python3 paint.py
```

## Controls

- `1` = small brush, 2 px
- `2` = medium brush, 5 px
- `3` = large brush, 10 px
- `G` = toggle grid preview
- `Ctrl+S` = save canvas as PNG
- Text tool: `Enter` = confirm, `Escape` = cancel, `Backspace` = delete character

## GitHub example

```bash
git init
git add .
git commit -m "Initial TSIS2 paint application"
git branch -M main
git remote add origin YOUR_REPOSITORY_LINK
git push -u origin main
```
