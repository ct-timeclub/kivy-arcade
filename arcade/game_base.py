"""El «contrato» que cumple cada juego para integrarse en la app.

Cada juego es una carpeta dentro de `games/` con dos cosas:

  1. Un `__init__.py` que define la variable `GAME = GameInfo(...)` (nombre, color, etc.).
  2. Una clase que hereda de `GameScreen` y rellena unos pocos «ganchos» (hooks).

GameScreen se encarga de todo lo común, para que el alumno solo programe su juego:
  * el bucle de actualización (60 veces por segundo),
  * la barra superior con la puntuación y el botón de pausa,
  * los menús de pausa y de «fin del juego»,
  * guardar la mejor puntuación,
  * atrapar los errores del juego para que NO tumben el resto de la app.

Mira games/_template/ para ver un ejemplo mínimo que funciona.
"""

from __future__ import annotations

import re
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

from kivy.base import ExceptionHandler, ExceptionManager
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    ColorProperty,
    NumericProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.utils import platform

from arcade import theme
from arcade.sound import SoundBank
from arcade.widgets import RoundedButton

# Minúsculas, números y guion bajo. (Puede empezar con _ porque la plantilla se llama «_template».)
_ID_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


@dataclass(frozen=True)
class GameInfo:
    """Datos de un juego. Se declaran en el `__init__.py` del juego como `GAME = GameInfo(...)`.

    id            nombre corto en minúsculas. DEBE ser igual al nombre de la carpeta.
    title         nombre que se muestra en la tarjeta.
    description   una o dos frases sobre el juego.
    author        quién lo hizo.
    color         color de la tarjeta, en hexadecimal (por ejemplo "#2EC4B6").
    screen_class  la clase del juego (hereda de GameScreen).
    version       versión del juego (libre).
    orientation   "portrait" (vertical), "landscape" (horizontal) o "any". Hoy solo orienta
                  el tamaño de la ventana al probar en el PC; el móvil usa la orientación de la app.
    order         posición en la lista (menor = antes). Si hay empate, por título.
    """

    id: str
    title: str
    description: str
    author: str
    color: str
    screen_class: type
    version: str = "0.1.0"
    orientation: str = "portrait"
    order: int = 100

    def __post_init__(self):
        if not _ID_PATTERN.match(self.id):
            raise ValueError(
                f"id '{self.id}' no es válido: usa solo minúsculas, números y _ (sin espacios)"
            )
        if not (self.color.startswith("#") and len(self.color) in (4, 7)):
            raise ValueError(f"color '{self.color}' no es válido: usa formato '#RRGGBB'")
        if self.orientation not in ("portrait", "landscape", "any"):
            raise ValueError("orientation debe ser 'portrait', 'landscape' o 'any'")


class GameHUD(FloatLayout):
    """Barra superior: botón de pausa, puntuación actual y mejor puntuación."""

    score = NumericProperty(0)
    best = NumericProperty(0)
    show_score = BooleanProperty(True)   # False si el juego dibuja su propio marcador
    __events__ = ("on_pause_pressed",)

    def on_pause_pressed(self):
        """Evento: el jugador tocó el botón de pausa."""


class Overlay(FloatLayout):
    """Panel modal (pausa, fin del juego, error) que bloquea los toques al juego de abajo."""

    title = StringProperty("")
    subtitle = StringProperty("")

    def set_buttons(self, buttons):
        """`buttons` es una lista de (texto, función, color_de_fondo)."""
        box = self.ids.buttons
        box.clear_widgets()
        for text, callback, color in buttons:
            btn = RoundedButton(text=text, bg=color, size_hint_y=None)
            btn.height = dp(54)
            btn.bind(on_release=lambda *_args, cb=callback: cb())
            box.add_widget(btn)

    # Modal: consumimos TODOS los toques para que no lleguen al juego de abajo.
    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        return True

    def on_touch_move(self, touch):
        super().on_touch_move(touch)
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        return True


class GameScreen(Screen):
    """Clase base de todos los juegos.

    ┌─ LO QUE TÚ ESCRIBES (ganchos, todos opcionales salvo build_game) ───────────────┐
    │ build_game(layer)       se llama UNA vez: crea tus widgets dentro de `layer`.   │
    │ new_game()              se llama al empezar o reiniciar: deja todo como al inicio│
    │ update(dt)              se llama ~60 veces/s mientras se juega: mueve cosas.    │
    │ on_game_paused()        el juego se pausó.                                      │
    │ on_game_resumed()       el juego continuó.                                      │
    │ on_game_finished(score, new_record)   la partida terminó.                       │
    └──────────────────────────────────────────────────────────────────────────────────┘
    ┌─ LO QUE TÚ LLAMAS ──────────────────────────────────────────────────────────────┐
    │ self.add_score(n)       suma puntos (por defecto 1).                            │
    │ self.game_over()        termina la partida (guarda récord y muestra el menú).   │
    │ self.asset("img.png")   ruta de un archivo de games/<tu_juego>/assets/.         │
    │ self.layer              el contenedor donde pones tus widgets.                  │
    │ self.score / self.best  puntuación actual / mejor guardada.                     │
    │ self.state              "playing", "paused", "over", "error" o "idle".          │
    └──────────────────────────────────────────────────────────────────────────────────┘

    Para recibir toques, sobrescribe on_touch_down y llama primero a `super()`:

        def on_touch_down(self, touch):
            if super().on_touch_down(touch):    # el botón de pausa o un menú lo usó
                return True
            ...tu lógica...
    """

    score = NumericProperty(0)
    best = NumericProperty(0)
    state = OptionProperty("idle", options=("idle", "playing", "paused", "over", "error"))
    background = ColorProperty(theme.BG)

    # Evento que escucha la app para saber que el jugador quiere salir del juego.
    __events__ = ("on_exit_game",)

    # Pon False si tu juego dibuja su propio marcador de puntos y no quieres el número del HUD.
    hud_score = True

    # Ticks por segundo del bucle de juego.
    FPS = 60
    # Si un cuadro tarda más que esto (segundos), se recorta para evitar «saltos» enormes.
    MAX_DT = 0.05

    def __init__(self, info: GameInfo, storage, **kwargs):
        kwargs.setdefault("name", info.id)
        super().__init__(**kwargs)
        self.info = info
        self.storage = storage
        self._loop = None
        self._overlay = None
        # Kivy crea los widgets con tamaño 100x100 y los ajusta después, al dibujar el primer
        # cuadro. Si empezáramos la partida antes, new_game() vería self.width/height falsos.
        self._sized = False
        self._start_pending = False
        self.bind(size=self._on_size_changed)

        self.layer = FloatLayout()
        self.hud = GameHUD(show_score=self.hud_score)
        self.hud.bind(on_pause_pressed=lambda *_: self.pause())
        self.bind(score=self.hud.setter("score"), best=self.hud.setter("best"))
        self.add_widget(self.layer)
        self.add_widget(self.hud)

        self.build_game(self.layer)

    # ------------------------------------------------------------------ ganchos
    def build_game(self, layer):
        """GANCHO. Crea aquí tus widgets (se ejecuta una sola vez)."""

    def new_game(self):
        """GANCHO. Deja el juego listo para una partida nueva."""

    def update(self, dt):
        """GANCHO. Se ejecuta cada cuadro mientras se juega. `dt` = segundos desde el anterior."""

    def on_game_paused(self):
        """GANCHO. El juego se pausó."""

    def on_game_resumed(self):
        """GANCHO. El juego continuó tras una pausa."""

    def on_game_finished(self, score, new_record):
        """GANCHO. La partida terminó con `score` puntos."""

    def on_exit_game(self):
        """Evento (lo conecta la app). Se dispara con exit_game()."""

    # ------------------------------------------------------------------ API para el juego
    @property
    def sound_enabled(self) -> bool:
        """True si el jugador no desactivó el sonido en Ajustes."""
        return bool(self.storage.get_setting("sound", True))

    def asset(self, *parts) -> str:
        """Ruta absoluta a un archivo de la carpeta `assets/` del juego.

        Ejemplo: Image(source=self.asset("bird.png")) busca games/<tu_juego>/assets/bird.png
        """
        module_file = sys.modules[type(self).__module__].__file__
        return str(Path(module_file).resolve().parent.joinpath("assets", *parts))

    def play_sound(self, name):
        """Reproduce un efecto de sonido (si el jugador no lo desactivó en Ajustes).

        Nombres disponibles: ver arcade/sound.py (flap, point, hit, eat, jump, coin, win...).
        """
        if self.sound_enabled:
            SoundBank.get().play(name)

    def vibrate(self, milliseconds=40):
        """Hace vibrar el teléfono un instante (solo Android, y si Vibración está activada)."""
        if platform != "android" or not self.storage.get_setting("vibration", True):
            return
        try:
            from jnius import autoclass

            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            context = autoclass("android.content.Context")
            activity.getSystemService(context.VIBRATOR_SERVICE).vibrate(int(milliseconds))
        except Exception:  # noqa: BLE001 - vibrar es un extra: si falla, no pasa nada
            pass

    def touch_pos(self, touch):
        """Posición de un toque en las coordenadas del juego (0, 0 = esquina inferior izquierda).

        Úsala en lugar de touch.x / touch.y, que son coordenadas de toda la ventana.
        """
        return self.to_local(touch.x, touch.y)

    def add_score(self, points=1):
        """Suma puntos a la puntuación actual (solo si se está jugando)."""
        if self.state == "playing":
            self.score += points

    def game_over(self, title="Fin del juego"):
        """Termina la partida: guarda el récord y muestra el menú de fin."""
        if self.state != "playing":
            return
        self._stop_loop()
        self.state = "over"
        new_record = self.storage.submit_score(self.info.id, self.score)
        self.best = self.storage.best(self.info.id)
        subtitle = f"Puntos: {int(self.score)}   ·   Mejor: {int(self.best)}"
        if new_record:
            subtitle += "\n¡Nuevo récord!"
        self._open_overlay(
            title,
            subtitle,
            [
                ("Jugar otra vez", self.restart, theme.ACCENT),
                ("Salir", self.exit_game, theme.SURFACE2),
            ],
        )
        self._safe(self.on_game_finished, self.score, new_record)

    # ------------------------------------------------------------------ control de la partida
    def start_game(self):
        """Empieza una partida desde cero."""
        SoundBank.get().warm_up()
        self._close_overlay()
        self._stop_loop()
        self.score = 0
        self.best = self.storage.best(self.info.id)
        try:
            self.new_game()
        except Exception as exc:  # noqa: BLE001
            self.fail(exc)
            return
        self.state = "playing"
        self._loop = Clock.schedule_interval(self._tick, 1.0 / self.FPS)

    def restart(self):
        self.start_game()

    def pause(self):
        if self.state != "playing":
            return
        self._stop_loop()
        self.state = "paused"
        self._safe(self.on_game_paused)
        self._open_overlay(
            "Pausa",
            "",
            [
                ("Continuar", self.resume, theme.ACCENT),
                ("Reiniciar", self.restart, theme.SURFACE2),
                ("Salir", self.exit_game, theme.SURFACE2),
            ],
        )

    def resume(self):
        if self.state != "paused":
            return
        self._close_overlay()
        self.state = "playing"
        self._loop = Clock.schedule_interval(self._tick, 1.0 / self.FPS)
        self._safe(self.on_game_resumed)

    def exit_game(self):
        """Pide a la app que salga de este juego."""
        self.dispatch("on_exit_game")

    def handle_back(self):
        """Botón «atrás» de Android / tecla Esc: pausa, reanuda o sale según el estado."""
        if self.state == "playing":
            self.pause()
        elif self.state == "paused":
            self.resume()
        else:
            self.exit_game()

    def fail(self, exc):
        """El juego lanzó un error: lo mostramos aquí sin tumbar toda la app."""
        Logger.error(
            "Game: error en '%s':\n%s",
            self.info.id,
            "".join(traceback.format_exception(exc)),
        )
        self._stop_loop()
        self.state = "error"
        self._open_overlay(
            "El juego tuvo un error",
            f"{type(exc).__name__}: {exc}",
            [("Salir", self.exit_game, theme.DANGER)],
        )

    # ------------------------------------------------------------------ eventos de Screen
    def on_enter(self, *args):
        if self._sized:
            self.start_game()
        else:
            # Aún no tenemos el tamaño real (pasa en el modo solo, al ser la primera pantalla):
            # esperamos a que Kivy lo asigne y entonces arrancamos.
            self._start_pending = True

    def _on_size_changed(self, *_args):
        self._sized = True
        if self._start_pending:
            self._start_pending = False
            self.start_game()

    def on_leave(self, *args):
        self._start_pending = False
        self._stop_loop()
        self._close_overlay()
        self.state = "idle"

    # ------------------------------------------------------------------ internos
    def _tick(self, dt):
        if self.state != "playing":
            return
        try:
            self.update(min(dt, self.MAX_DT))
        except Exception as exc:  # noqa: BLE001
            self.fail(exc)

    def _safe(self, func, *args):
        """Ejecuta un gancho del alumno; si falla, muestra el error en pantalla."""
        try:
            func(*args)
        except Exception as exc:  # noqa: BLE001
            self.fail(exc)

    def _stop_loop(self):
        if self._loop is not None:
            self._loop.cancel()
            self._loop = None

    def _open_overlay(self, title, subtitle, buttons):
        self._close_overlay()
        overlay = Overlay(title=title, subtitle=subtitle)
        overlay.set_buttons(buttons)
        self._overlay = overlay
        self.add_widget(overlay)

    def _close_overlay(self):
        if self._overlay is not None:
            self.remove_widget(self._overlay)
            self._overlay = None


class GameErrorHandler(ExceptionHandler):
    """Captura errores que ocurran dentro de un juego (toques, temporizadores...).

    Si el juego que está en pantalla lanza una excepción, en vez de cerrar toda la app
    se le muestra el error a ese juego. Si no hay juego en pantalla, se deja pasar el error.
    """

    def __init__(self, get_screen):
        super().__init__()
        self._get_screen = get_screen

    def handle_exception(self, inst):
        screen = self._get_screen()
        if screen is None:
            return ExceptionManager.RAISE
        if screen.state != "error":
            screen.fail(inst)
        return ExceptionManager.PASS


Builder.load_string(
    """
#:import theme arcade.theme
#:import dp kivy.metrics.dp

<GameScreen>:
    canvas.before:
        Color:
            rgba: self.background
        Rectangle:
            pos: self.pos
            size: self.size

<GameHUD>:
    BoxLayout:
        size_hint_y: None
        height: dp(56)
        pos_hint: {"top": 1}
        padding: dp(8)
        spacing: dp(8)
        RoundedButton:
            text: "II"
            size_hint_x: None
            width: dp(44)
            bg: 0, 0, 0, 0.35
            on_release: root.dispatch("on_pause_pressed")
        Label:
            text: str(int(root.score))
            opacity: 1 if root.show_score else 0
            font_size: "30sp"
            bold: True
            color: theme.TEXT
            outline_width: dp(2)
            outline_color: 0.04, 0.05, 0.14, 0.95
        Label:
            text: "Mejor " + str(int(root.best))
            size_hint_x: None
            width: dp(96)
            font_size: "14sp"
            bold: True
            color: theme.TEXT
            outline_width: dp(2)
            outline_color: 0.04, 0.05, 0.14, 0.95
            halign: "right"
            valign: "middle"
            text_size: self.size

<Overlay>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.7
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: "vertical"
        size_hint: None, None
        width: min(root.width - dp(48), dp(340))
        height: self.minimum_height
        pos_hint: {"center_x": .5, "center_y": .5}
        padding: dp(20)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: theme.SURFACE
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(22)]
        Label:
            text: root.title
            size_hint_y: None
            height: dp(40)
            font_size: "24sp"
            bold: True
            color: theme.TEXT
            text_size: self.width, None
            halign: "center"
        Label:
            text: root.subtitle
            size_hint_y: None
            height: dp(52) if root.subtitle else 0
            font_size: "15sp"
            color: theme.MUTED
            text_size: self.width, None
            halign: "center"
            valign: "middle"
        BoxLayout:
            id: buttons
            orientation: "vertical"
            size_hint_y: None
            height: self.minimum_height
            spacing: dp(10)
"""
)
