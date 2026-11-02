"""Arranca UN solo juego de forma aislada, sin el menú ni los demás juegos.

Es la herramienta principal de cada alumno mientras desarrolla:

    python run_game.py snake          (desde la raíz del repositorio)
    python -m games.snake             (equivalente)

Así puede probar su juego sin depender de nadie ni afectar a los demás.
En el PC la ventana imita un teléfono (vertical u horizontal según GameInfo.orientation).
"""

import sys
from pathlib import Path

from kivy.app import App
from kivy.base import ExceptionManager
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from arcade import theme
from arcade.config import DEV_WINDOW_LANDSCAPE, DEV_WINDOW_PORTRAIT
from arcade.game_base import GameErrorHandler
from arcade.registry import load_game
from arcade.storage import Storage


class SoloApp(App):
    """App mínima que contiene únicamente el juego indicado."""

    def __init__(self, game_id, storage_path=None, **kwargs):
        super().__init__(**kwargs)
        self.game_id = game_id
        self._storage_path = storage_path
        self.screen = None

    def build(self):
        entry = load_game(self.game_id)
        if not entry.ok:
            raise SystemExit(f"No se pudo cargar el juego '{self.game_id}': {entry.error}")
        info = entry.info

        self.title = f"{info.title} (modo solo)"
        Window.clearcolor = theme.BG
        if platform not in ("android", "ios"):
            Window.size = (
                DEV_WINDOW_LANDSCAPE if info.orientation == "landscape" else DEV_WINDOW_PORTRAIT
            )

        path = self._storage_path or Path(self.user_data_dir) / "arcade_dev.json"
        self.screen = info.screen_class(info=info, storage=Storage(path))
        self.screen.bind(on_exit_game=lambda *_: self.stop())

        manager = ScreenManager()
        manager.add_widget(self.screen)
        ExceptionManager.add_handler(GameErrorHandler(lambda: self.screen))
        return manager


def run_single(game_id=None, argv=None):
    """Punto de entrada: `run_single("snake")` abre solo ese juego."""
    if game_id is None:
        args = list(sys.argv[1:] if argv is None else argv)
        if not args:
            raise SystemExit("Uso: python run_game.py <id_del_juego>   (ej.: snake)")
        game_id = args[0]
    SoloApp(game_id).run()
