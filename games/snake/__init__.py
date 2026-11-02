"""Snake. (Alumno: por asignar)"""

from arcade.game_base import GameInfo

from .game import SnakeGame

GAME = GameInfo(
    id=__name__.rsplit(".", 1)[-1],
    title="Snake",
    description="Come manzanas, crece y no choques contigo misma.",
    author="Por asignar",
    color="#2EC4B6",
    screen_class=SnakeGame,
    orientation="portrait",
    order=20,
)
