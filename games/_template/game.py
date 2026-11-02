"""Juego de ejemplo «Toca el círculo». Sirve de modelo para escribir el tuyo.

Idea del juego: un círculo rebota por la pantalla. Cada vez que lo tocas ganas un punto
y se mueve más rápido. Tienes 20 segundos.

Qué enseña este ejemplo (todo lo que necesita un juego sencillo):
  * build_game()   crear los widgets una sola vez.
  * new_game()     dejar todo listo al empezar (o reiniciar).
  * update(dt)     mover cosas cada cuadro, usando dt para que la velocidad sea la misma
                   en cualquier dispositivo.
  * on_touch_down  reaccionar a los toques.
  * add_score() y game_over()  la puntuación y el final de la partida.
  * canvas         dibujar formas (Color + Ellipse) y moverlas cambiando su pos/size.
"""

import math
import random

from kivy.graphics import Color, Ellipse
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex

from arcade import theme
from arcade.game_base import GameScreen


class TemplateGame(GameScreen):
    TIME_LIMIT = 20.0  # segundos que dura una partida

    # ------------------------------------------------------------------ construcción
    def build_game(self, layer):
        """Se ejecuta UNA vez. `layer` es el contenedor donde ponemos todo lo del juego."""
        # Dibujamos el círculo en el canvas del layer. Guardamos la referencia (self.circle)
        # para poder moverlo después sin volver a crearlo.
        with layer.canvas:
            Color(*get_color_from_hex(self.info.color))
            self.circle = Ellipse(pos=(0, 0), size=(0, 0))

        # Un texto con el tiempo restante, abajo en el centro.
        self.timer_label = Label(
            font_size="18sp",
            color=theme.MUTED,
            size_hint=(None, None),
            size=(dp(220), dp(30)),
            pos_hint={"center_x": 0.5, "y": 0.02},
        )
        layer.add_widget(self.timer_label)

    # ------------------------------------------------------------------ partida
    def new_game(self):
        """Se ejecuta al empezar y al reiniciar: estado inicial de la partida."""
        self.radius = dp(36)
        self.time_left = self.TIME_LIMIT
        speed = dp(170)  # píxeles por segundo
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        # Empezamos en el centro. (Aquí self.width/height ya tienen el tamaño real.)
        self.cx = self.width / 2
        self.cy = self.height / 2
        self._redraw()

    def update(self, dt):
        """Se ejecuta ~60 veces por segundo. `dt` son los segundos desde el cuadro anterior."""
        self.time_left -= dt

        # Movimiento: distancia = velocidad × tiempo.
        self.cx += self.vx * dt
        self.cy += self.vy * dt

        # Rebote en las paredes. Arriba dejamos espacio para la barra de puntuación (56 dp).
        top = self.height - dp(56) - self.radius
        if self.cx < self.radius:
            self.cx, self.vx = self.radius, abs(self.vx)
        elif self.cx > self.width - self.radius:
            self.cx, self.vx = self.width - self.radius, -abs(self.vx)
        if self.cy < self.radius:
            self.cy, self.vy = self.radius, abs(self.vy)
        elif self.cy > top:
            self.cy, self.vy = top, -abs(self.vy)

        self._redraw()
        if self.time_left <= 0:
            self.game_over("¡Se acabó el tiempo!")

    # ------------------------------------------------------------------ toques
    def on_touch_down(self, touch):
        # 1) Dejamos que la barra de pausa / los menús vean el toque primero.
        if super().on_touch_down(touch):
            return True
        if self.state != "playing":
            return False
        # 2) touch_pos() da el toque en las coordenadas del juego.
        x, y = self.touch_pos(touch)
        # 3) ¿El toque cayó dentro del círculo? (distancia al centro <= radio, con margen)
        if math.hypot(x - self.cx, y - self.cy) <= self.radius * 1.3:
            self.add_score(1)
            self.vx *= 1.08   # cada acierto, un 8 % más rápido
            self.vy *= 1.08
            return True
        return False

    # ------------------------------------------------------------------ auxiliares
    def _redraw(self):
        """Actualiza el dibujo según la posición actual."""
        self.circle.pos = (self.cx - self.radius, self.cy - self.radius)
        self.circle.size = (self.radius * 2, self.radius * 2)
        self.timer_label.text = f"Tiempo: {max(self.time_left, 0):.1f} s"
