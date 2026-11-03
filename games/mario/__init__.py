"""Mario 2D (versión terminada de la demo)."""

from arcade.game_base import GameInfo

from .game import MarioGame

GAME = GameInfo(
    id=__name__.rsplit(".", 1)[-1],
    title="Mario 2D",
    description="Plataformas: salta, junta monedas, pisa enemigos y llega a la bandera.",
    author="Demo del docente",
    color="#E63946",
    screen_class=MarioGame,
    orientation="portrait",
    order=30,
)
