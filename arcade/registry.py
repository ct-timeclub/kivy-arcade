"""Descubrimiento automático de juegos.

La app NO tiene una lista de juegos escrita a mano. Al arrancar recorre la carpeta
`games/` y carga cada subcarpeta que no empiece por "_". Por eso:

  * Añadir un juego = crear una carpeta nueva. No hay que tocar ningún archivo compartido,
    así los 3 alumnos casi nunca tendrán conflictos de git.
  * Si un juego tiene un error, se muestra como "no se pudo cargar" en su tarjeta y
    el resto de la app (y de los juegos) sigue funcionando.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
import traceback
from dataclasses import dataclass

from arcade.config import GAMES_PACKAGE
from arcade.game_base import GameInfo, GameScreen

log = logging.getLogger("arcade.registry")


@dataclass(frozen=True)
class GameEntry:
    """Resultado de intentar cargar una carpeta de juego."""

    folder: str                     # nombre de la carpeta, p. ej. "snake"
    info: GameInfo | None = None    # los datos del juego, si cargó bien
    error: str | None = None        # el motivo del fallo, si no cargó

    @property
    def ok(self) -> bool:
        return self.info is not None


def load_game(folder: str, package: str = GAMES_PACKAGE) -> GameEntry:
    """Importa `games.<folder>` y valida que cumpla el contrato (variable GAME)."""
    module_name = f"{package}.{folder}"
    try:
        module = importlib.import_module(module_name)
        info = getattr(module, "GAME", None)
        if info is None:
            raise ValueError("falta la variable GAME en el __init__.py del juego")
        if not isinstance(info, GameInfo):
            raise TypeError("GAME debe ser un GameInfo(...)")
        if info.id != folder:
            raise ValueError(
                f"el id '{info.id}' no coincide con el nombre de la carpeta '{folder}'"
            )
        if not (isinstance(info.screen_class, type) and issubclass(info.screen_class, GameScreen)):
            raise TypeError("screen_class debe ser una clase que herede de GameScreen")
        return GameEntry(folder, info=info)
    except Exception as exc:  # noqa: BLE001 - queremos atrapar CUALQUIER error del juego
        log.error("No se pudo cargar el juego '%s':\n%s", folder, traceback.format_exc())
        return GameEntry(folder, error=f"{type(exc).__name__}: {exc}")


def discover(package: str = GAMES_PACKAGE) -> list[GameEntry]:
    """Devuelve una entrada por cada subcarpeta de `package` (ignorando las que empiezan con _)."""
    pkg = importlib.import_module(package)
    entries = [
        load_game(module.name, package)
        for module in pkgutil.iter_modules(pkg.__path__)
        if module.ispkg and not module.name.startswith("_")
    ]
    # Primero los que cargaron bien (por orden y título), al final los que fallaron.
    entries.sort(
        key=lambda e: (0, e.info.order, e.info.title.lower()) if e.ok else (1, 0, e.folder)
    )
    return entries
