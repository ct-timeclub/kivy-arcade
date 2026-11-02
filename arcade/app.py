"""La App principal: crea las pantallas, navega entre ellas y lanza los juegos."""

from pathlib import Path

from kivy.animation import Animation
from kivy.app import App
from kivy.base import ExceptionManager
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from arcade import theme
from arcade.config import APP_NAME
from arcade.game_base import GameErrorHandler, GameScreen
from arcade.registry import discover
from arcade.screens import AboutScreen, GamesScreen, MenuScreen, ScoresScreen, SettingsScreen
from arcade.storage import Storage
from arcade.widgets import Toast

ESC_KEY = 27  # la tecla Esc en el PC y el botón «atrás» en Android generan este código


class ArcadeApp(App):
    """Ventana principal con menú, lista de juegos, puntuaciones y ajustes."""

    def __init__(self, storage_path=None, **kwargs):
        """`storage_path` permite cambiar dónde se guardan los datos (útil en las pruebas)."""
        super().__init__(**kwargs)
        self._storage_path = storage_path
        self.entries = []
        self.storage = None
        self.manager = None
        self._history = []          # pila de pantallas visitadas, para el botón «atrás»
        self._game_screens = {}     # juegos ya creados (se crean la primera vez que se juegan)

    # ------------------------------------------------------------------ construcción
    def build(self):
        self.title = APP_NAME
        Window.clearcolor = theme.BG

        path = self._storage_path or Path(self.user_data_dir) / "arcade.json"
        self.storage = Storage(path)
        self.entries = discover()

        self.manager = ScreenManager(transition=SlideTransition(duration=0.22))
        for screen_class, name in (
            (MenuScreen, "menu"),
            (GamesScreen, "games"),
            (ScoresScreen, "scores"),
            (SettingsScreen, "settings"),
            (AboutScreen, "about"),
        ):
            self.manager.add_widget(screen_class(name=name))

        self._toast = Toast()
        root = FloatLayout()
        root.add_widget(self.manager)
        root.add_widget(self._toast)

        Window.bind(on_keyboard=self._on_keyboard)
        ExceptionManager.add_handler(GameErrorHandler(self.current_game))
        return root

    # ------------------------------------------------------------------ navegación
    def go(self, name, direction="left"):
        """Muestra la pantalla `name` con una animación deslizante."""
        if self.manager.current == name:
            return
        self._history.append(self.manager.current)
        self.manager.transition = SlideTransition(direction=direction, duration=0.22)
        self.manager.current = name

    def go_back(self):
        """Vuelve a la pantalla anterior (o al menú si no hay historial)."""
        target = self._history.pop() if self._history else "menu"
        self.manager.transition = SlideTransition(direction="right", duration=0.22)
        self.manager.current = target

    def current_game(self):
        """El GameScreen que está en pantalla ahora mismo (o None)."""
        screen = self.manager.current_screen if self.manager else None
        return screen if isinstance(screen, GameScreen) else None

    # ------------------------------------------------------------------ juegos
    def play(self, game_id):
        """Abre un juego. Si falla al crearse, muestra un aviso y no pasa nada más."""
        screen = self._game_screens.get(game_id)
        if screen is None:
            entry = next((e for e in self.entries if e.ok and e.info.id == game_id), None)
            if entry is None:
                self.toast(f"El juego '{game_id}' no está disponible")
                return
            try:
                screen = entry.info.screen_class(info=entry.info, storage=self.storage)
            except Exception as exc:  # noqa: BLE001 - el error del juego no debe tumbar la app
                Logger.exception("Game: no se pudo crear '%s'", game_id)
                self.toast(f"{entry.info.title} no pudo abrirse: {type(exc).__name__}: {exc}")
                return
            screen.bind(on_exit_game=lambda *_: self.go_back())
            self._game_screens[game_id] = screen
            self.manager.add_widget(screen)
        self.go(game_id)

    # ------------------------------------------------------------------ avisos
    def toast(self, message, seconds=2.4):
        """Muestra un aviso breve en la parte baja de la pantalla."""
        Animation.cancel_all(self._toast)
        self._toast.text = message
        (
            Animation(opacity=1, d=0.15)
            + Animation(opacity=1, d=seconds)
            + Animation(opacity=0, d=0.3)
        ).start(self._toast)

    # ------------------------------------------------------------------ eventos del sistema
    def _on_keyboard(self, _window, key, *_args):
        """Esc / botón atrás: se comporta como «volver». En el menú, cierra la app."""
        if key != ESC_KEY:
            return False
        game = self.current_game()
        if game is not None:
            game.handle_back()
            return True
        if self.manager.current != "menu":
            self.go_back()
            return True
        return False

    def on_pause(self):
        """Android/iOS: la app pasa a segundo plano. Pausamos el juego en curso."""
        game = self.current_game()
        if game is not None:
            game.pause()
        return True  # True = permitir que la app se quede en pausa (no cerrarla)

    def on_resume(self):
        """Volvimos a la app. El juego sigue en pausa hasta que el jugador pulse «Continuar»."""
