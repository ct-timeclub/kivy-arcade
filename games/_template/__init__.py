"""Plantilla de juego. COPIA ESTA CARPETA para crear el tuyo.

Pasos:
  1. Copia games/_template a games/<tu_juego>   (nombre en minúsculas, sin espacios).
  2. Edita los datos de GAME aquí abajo (título, descripción, autor, color).
  3. Programa tu juego en game.py.
  4. Pruébalo SOLO con:  python run_game.py <tu_juego>

Este archivo es lo único que la app lee para saber que tu juego existe.
"""

from arcade.game_base import GameInfo

from .game import TemplateGame

GAME = GameInfo(
    # El id debe ser igual al nombre de la carpeta. Aquí se toma solo de ella,
    # así que NO tienes que cambiarlo al copiar la plantilla.
    id=__name__.rsplit(".", 1)[-1],
    title="Plantilla",
    description="Toca el círculo todas las veces que puedas antes de que se acabe el tiempo.",
    author="Tu nombre",
    color="#FF6B6B",
    screen_class=TemplateGame,   # la clase de game.py (si le cambias el nombre, cámbialo aquí)
    orientation="portrait",      # "portrait", "landscape" o "any"
)
