"""Pantallas del menú: inicio, lista de juegos, puntuaciones, ajustes y acerca de.

Cada pantalla es una clase `Screen` de Kivy. Su aspecto se declara en el bloque KV del
final de este archivo y su lógica (llenar listas, reaccionar a botones) está en Python.
Todas se comunican con la app mediante `App.get_running_app()` (la variable `app` en KV).
"""

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from arcade import theme
from arcade.config import APP_NAME, APP_VERSION
from arcade.widgets import Chip, GameCard, ScoreRow

MAX_CHIPS = 4  # cuántos juegos se muestran como etiquetas en el menú de inicio


class MenuScreen(Screen):
    """Pantalla de inicio con los botones principales."""

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        row = self.ids.chips
        row.clear_widgets()
        ok_games = [e.info for e in app.entries if e.ok]
        row.add_widget(Widget())  # espaciador izquierdo: centra las etiquetas
        for info in ok_games[:MAX_CHIPS]:
            row.add_widget(Chip(text=info.title, bg=info.color))
        if len(ok_games) > MAX_CHIPS:
            row.add_widget(Chip(text=f"+{len(ok_games) - MAX_CHIPS}", bg=theme.SURFACE2))
        row.add_widget(Widget())  # espaciador derecho
        self.ids.footer.text = f"{APP_NAME}  ·  v{APP_VERSION}"


class GamesScreen(Screen):
    """Lista de juegos instalados (uno por tarjeta)."""

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        box = self.ids.list
        box.clear_widgets()
        if not app.entries:
            self.ids.empty.opacity = 1
            return
        self.ids.empty.opacity = 0
        for entry in app.entries:
            if entry.ok:
                info = entry.info
                card = GameCard(
                    title=info.title,
                    description=info.description,
                    author=f"Autor: {info.author}",
                    initial=info.title[:1].upper(),
                    best_text=str(app.storage.best(info.id)),
                    accent=_hex(info.color),
                )
                card.bind(on_release=lambda _w, game_id=info.id: app.play(game_id))
            else:
                # El juego tiene un error: lo mostramos igual para que el alumno lo vea.
                card = GameCard(
                    title=entry.folder,
                    description=entry.error or "Error desconocido",
                    author="No se pudo cargar",
                    initial="!",
                    best_text="-",
                    accent=theme.DANGER,
                )
                card.bind(on_release=lambda _w, e=entry: app.toast(f"{e.folder}: {e.error}"))
            box.add_widget(card)


class ScoresScreen(Screen):
    """Mejores puntuaciones de cada juego."""

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        box = self.ids.list
        box.clear_widgets()
        total = 0
        for entry in app.entries:
            if not entry.ok:
                continue
            info = entry.info
            plays = app.storage.plays(info.id)
            total += plays
            box.add_widget(
                ScoreRow(
                    title=info.title,
                    plays_text=f"{plays} partida{'s' if plays != 1 else ''}",
                    best_text=str(app.storage.best(info.id)),
                    accent=_hex(info.color),
                )
            )
        self.ids.summary.text = f"Partidas jugadas en total: {total}"


class SettingsScreen(Screen):
    """Ajustes: sonido, vibración y borrar puntuaciones."""

    _confirming = False
    _revert_event = None

    def on_pre_enter(self, *args):
        self._refresh_toggles()
        self._cancel_confirm()

    def on_leave(self, *args):
        self._cancel_confirm()

    def toggle(self, key):
        """Invierte un ajuste (True/False) y actualiza los botones."""
        storage = App.get_running_app().storage
        storage.set_setting(key, not storage.get_setting(key, True))
        self._refresh_toggles()

    def _refresh_toggles(self):
        storage = App.get_running_app().storage
        for key, button in (("sound", self.ids.sound_btn), ("vibration", self.ids.vibration_btn)):
            on = bool(storage.get_setting(key, True))
            button.text = "SÍ" if on else "NO"
            button.bg = theme.SUCCESS if on else theme.SURFACE2

    def reset_scores(self):
        """Borra las puntuaciones; pide confirmación tocando dos veces."""
        app = App.get_running_app()
        if self._confirming:
            app.storage.reset_scores()
            self._cancel_confirm()
            app.toast("Puntuaciones borradas")
        else:
            self._confirming = True
            self.ids.reset_btn.text = "¿Seguro? Toca otra vez"
            self._revert_event = Clock.schedule_once(lambda _dt: self._cancel_confirm(), 3)

    def _cancel_confirm(self):
        self._confirming = False
        if self._revert_event is not None:
            self._revert_event.cancel()
            self._revert_event = None
        self.ids.reset_btn.text = "Borrar puntuaciones"


class AboutScreen(Screen):
    """Información de la app y de los juegos instalados."""

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        games = "\n".join(
            f"  •  [b]{e.info.title}[/b]  —  {e.info.author}" for e in app.entries if e.ok
        ) or "  (todavía no hay juegos)"
        self.ids.about_text.text = (
            f"[b]{APP_NAME}[/b]  v{APP_VERSION}\n"
            "Una app móvil hecha con Kivy. Cada alumno aporta un juego.\n\n"
            "[b]Juegos instalados[/b]\n"
            f"{games}\n\n"
            "[b]¿Cómo se añade un juego?[/b]\n"
            "  1. Copia la carpeta games/_template a games/<tu_juego>.\n"
            "  2. Edita su __init__.py (nombre, color, autor).\n"
            "  3. Programa tu juego en game.py.\n"
            "  4. Pruébalo solo:  python run_game.py <tu_juego>\n"
            "  5. Abre la app completa:  python main.py\n"
        )


def _hex(color):
    """Convierte '#RRGGBB' al formato RGBA de Kivy."""
    return get_color_from_hex(color)


Builder.load_string(
    """
#:import theme arcade.theme
#:import dp kivy.metrics.dp

# Fondo del color del tema para todas las pantallas del menú.
<MenuScreen,GamesScreen,ScoresScreen,SettingsScreen,AboutScreen>:
    canvas.before:
        Color:
            rgba: theme.BG
        Rectangle:
            pos: self.pos
            size: self.size

<MenuScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(28), dp(24)
        spacing: dp(12)
        Widget:
            size_hint_y: 0.30
        Label:
            text: "KIVY"
            size_hint_y: None
            height: dp(72)
            font_size: "62sp"
            bold: True
            color: theme.ACCENT
        Label:
            text: "ARCADE"
            size_hint_y: None
            height: dp(52)
            font_size: "42sp"
            bold: True
            color: theme.TEXT
        Label:
            text: "Proyecto final de clase"
            size_hint_y: None
            height: dp(28)
            font_size: "14sp"
            color: theme.MUTED
        BoxLayout:
            id: chips
            size_hint_y: None
            height: dp(34)
            spacing: dp(8)
        Widget:
            size_hint_y: 0.30
        RoundedButton:
            text: "JUGAR"
            bg: theme.ACCENT
            size_hint_y: None
            height: dp(68)
            font_size: "22sp"
            on_release: app.go("games")
        RoundedButton:
            text: "Puntuaciones"
            size_hint_y: None
            height: dp(56)
            on_release: app.go("scores")
        RoundedButton:
            text: "Ajustes"
            size_hint_y: None
            height: dp(56)
            on_release: app.go("settings")
        RoundedButton:
            text: "Acerca de"
            size_hint_y: None
            height: dp(56)
            on_release: app.go("about")
        Widget:
            size_hint_y: 0.10
        Label:
            id: footer
            size_hint_y: None
            height: dp(24)
            font_size: "12sp"
            color: theme.MUTED

<GamesScreen>:
    BoxLayout:
        orientation: "vertical"
        Header:
            title: "Elige un juego"
        FloatLayout:
            ScrollView:
                do_scroll_x: False
                bar_width: dp(3)
                GridLayout:
                    id: list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(16)
                    spacing: dp(12)
            Label:
                id: empty
                opacity: 0
                text: "Todavía no hay juegos instalados.\\nCrea uno en la carpeta games/"
                halign: "center"
                color: theme.MUTED

<ScoresScreen>:
    BoxLayout:
        orientation: "vertical"
        Header:
            title: "Puntuaciones"
        ScrollView:
            do_scroll_x: False
            bar_width: dp(3)
            GridLayout:
                id: list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                padding: dp(16)
                spacing: dp(10)
        Label:
            id: summary
            size_hint_y: None
            height: dp(44)
            font_size: "14sp"
            color: theme.MUTED

<SettingsScreen>:
    BoxLayout:
        orientation: "vertical"
        Header:
            title: "Ajustes"
        BoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(12)
            BoxLayout:
                size_hint_y: None
                height: dp(64)
                padding: dp(18), 0, dp(10), 0
                canvas.before:
                    Color:
                        rgba: theme.SURFACE
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(16)]
                Label:
                    text: "Sonido"
                    font_size: "18sp"
                    color: theme.TEXT
                    halign: "left"
                    valign: "middle"
                    text_size: self.size
                RoundedButton:
                    id: sound_btn
                    size_hint: None, None
                    size: dp(76), dp(44)
                    pos_hint: {"center_y": .5}
                    on_release: root.toggle("sound")
            BoxLayout:
                size_hint_y: None
                height: dp(64)
                padding: dp(18), 0, dp(10), 0
                canvas.before:
                    Color:
                        rgba: theme.SURFACE
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(16)]
                Label:
                    text: "Vibración"
                    font_size: "18sp"
                    color: theme.TEXT
                    halign: "left"
                    valign: "middle"
                    text_size: self.size
                RoundedButton:
                    id: vibration_btn
                    size_hint: None, None
                    size: dp(76), dp(44)
                    pos_hint: {"center_y": .5}
                    on_release: root.toggle("vibration")
            Widget:
            RoundedButton:
                id: reset_btn
                text: "Borrar puntuaciones"
                bg: theme.DANGER
                size_hint_y: None
                height: dp(56)
                on_release: root.reset_scores()
            Label:
                text: "Los ajustes de sonido y vibración los pueden leer los juegos."
                size_hint_y: None
                height: dp(36)
                font_size: "12sp"
                color: theme.MUTED

<AboutScreen>:
    BoxLayout:
        orientation: "vertical"
        Header:
            title: "Acerca de"
        ScrollView:
            do_scroll_x: False
            bar_width: dp(3)
            BoxLayout:
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20)
                Label:
                    id: about_text
                    markup: True
                    size_hint_y: None
                    height: self.texture_size[1]
                    text_size: self.width, None
                    halign: "left"
                    valign: "top"
                    font_size: "15sp"
                    color: theme.TEXT
"""
)
