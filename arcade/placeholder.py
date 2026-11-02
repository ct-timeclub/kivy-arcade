"""Juego «en construcción»: pantalla provisional para los juegos que aún no se programan.

Sirve para probar que el menú, las puntuaciones y el modo solo funcionan antes de que
el alumno escriba su juego. Cuando el alumno programe el suyo, simplemente deja de usar
esta clase y hereda directamente de GameScreen.
"""

from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from arcade import theme
from arcade.game_base import GameScreen
from arcade.widgets import RoundedButton


class PlaceholderGame(GameScreen):
    """Pantalla con dos botones de prueba para comprobar la puntuación y el fin de partida."""

    headline = "Juego"

    def build_game(self, layer):
        box = BoxLayout(
            orientation="vertical",
            size_hint=(0.86, None),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            spacing=dp(12),
        )
        box.bind(minimum_height=box.setter("height"))

        box.add_widget(self._label(self.headline, "30sp", theme.TEXT, dp(48), bold=True))
        box.add_widget(
            self._label("En construcción: aquí irá el juego.", "15sp", theme.MUTED, dp(30))
        )
        box.add_widget(self._label("", "15sp", theme.MUTED, dp(12)))

        plus = RoundedButton(text="+10 puntos (prueba)", bg=theme.ACCENT, size_hint_y=None)
        plus.height = dp(56)
        plus.bind(on_release=lambda *_: self.add_score(10))
        box.add_widget(plus)

        end = RoundedButton(text="Terminar partida (prueba)", size_hint_y=None)
        end.height = dp(56)
        end.bind(on_release=lambda *_: self.game_over())
        box.add_widget(end)

        layer.add_widget(box)

    @staticmethod
    def _label(text, size, color, height, bold=False):
        label = Label(text=text, font_size=size, color=color, bold=bold, size_hint_y=None)
        label.height = height
        return label
