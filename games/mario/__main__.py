"""Permite probar el juego SOLO con:  python -m games.mario"""

from pathlib import Path

from arcade.dev import run_single

run_single(Path(__file__).resolve().parent.name)
