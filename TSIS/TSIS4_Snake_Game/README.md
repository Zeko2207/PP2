# TSIS 4 Snake Game — PostgreSQL, Power-ups, Obstacles

This project extends a basic Snake game with PostgreSQL leaderboard persistence, poison food, power-ups, obstacles, settings saved to JSON, and Pygame screens.

## Project structure

```text
TSIS4_Snake_Game/
├── main.py
├── game.py
├── db.py
├── config.py
├── settings.json
├── requirements.txt
└── assets/
```

## Features

- PostgreSQL tables: `players`, `game_sessions`
- Username input on the main menu
- Auto-save results after Game Over
- Top 10 leaderboard loaded from PostgreSQL
- Personal best displayed during gameplay
- Weighted food with timeout
- Poison food that shortens the snake by 2 segments
- Power-ups:
  - Speed boost for 5 seconds
  - Slow motion for 5 seconds
  - Shield until the next wall/self-collision
- Obstacles starting from Level 3
- Obstacles avoid trapping the snake head at spawn time
- Food and power-ups avoid snake and obstacles
- Settings saved in `settings.json`:
  - Snake color
  - Grid overlay
  - Sound on/off
- Screens:
  - Main Menu
  - Leaderboard
  - Settings
  - Game Over

## Install

```bash
cd TSIS4_Snake_Game
python3 -m pip install -r requirements.txt
```

## PostgreSQL setup

Open `psql` and create the database:

```sql
CREATE DATABASE snake_db;
```

Then set your PostgreSQL login data in Terminal:

```bash
export PGDATABASE=snake_db
export PGUSER=postgres
export PGPASSWORD=your_password
export PGHOST=localhost
export PGPORT=5432
```

Or edit `DB_CONFIG` in `config.py` directly.

The game automatically creates these tables on startup:

```sql
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER NOT NULL,
    level_reached INTEGER NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
```

## Run

```bash
python3 main.py
```

If macOS shows `Operation not permitted`, move the project outside Desktop/Downloads:

```bash
mkdir -p ~/Projects
mv ~/Downloads/TSIS4_Snake_Game ~/Projects/
cd ~/Projects/TSIS4_Snake_Game
python3 main.py
```

## Controls

- Arrow keys: move snake
- Space: pause
- Esc: end current run

## GitHub commands

```bash
git init
git add .
git commit -m "Create TSIS4 snake game with PostgreSQL leaderboard"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```
