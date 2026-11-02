"""Mario 2D (versión simple). (Alumno: por asignar)"""

from arcade.game_base import GameInfo

from .game import MarioGame

GAME = GameInfo(
    id=__name__.rsplit(".", 1)[-1],
    title="Mario 2D",
    description="Plataformas sencillo: corre, salta y llega a la meta.",
    author="Por asignar",
    color="#E63946",
    screen_class=MarioGame,
    orientation="portrait",
    order=30,
)
