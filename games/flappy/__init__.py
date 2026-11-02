"""Flappy Bird. (Alumno: por asignar)"""

from arcade.game_base import GameInfo

from .game import FlappyGame

GAME = GameInfo(
    id=__name__.rsplit(".", 1)[-1],
    title="Flappy Bird",
    description="Toca para volar y esquiva los tubos.",
    author="Por asignar",
    color="#FFB703",
    screen_class=FlappyGame,
    orientation="portrait",
    order=10,
)
