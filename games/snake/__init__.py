"""Snake (versión terminada de la demo)."""

from arcade.game_base import GameInfo

from .game import SnakeGame

GAME = GameInfo(
    id=__name__.rsplit(".", 1)[-1],
    title="Snake",
    description="Desliza para girar, come manzanas y busca la dorada. No te muerdas.",
    author="Demo del docente",
    color="#2EC4B6",
    screen_class=SnakeGame,
    orientation="portrait",
    order=20,
)
