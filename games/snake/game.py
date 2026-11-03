"""Snake: desliza el dedo para girar, come manzanas y no choques.

Ideas que muestra este juego:

  * Lógica en una CUADRÍCULA que avanza a «pasos» (cada `interval` segundos), pero dibujada
    con movimiento SUAVE: entre un paso y el siguiente se interpola la posición.
  * Control por deslizamiento (swipe) con on_touch_down / on_touch_move, y teclado en el PC.
  * Cola de giros: si deslizas dos veces rápido, no se pierde ninguno.
  * Manzana dorada temporal (más puntos) con un anillo que se va vaciando.
  * Textura de damero que se repite para dibujar todo el tablero con UN solo rectángulo.
"""

import math
import random

from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, PopMatrix, PushMatrix, Rectangle, Translate
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as hx

from arcade.game_base import GameScreen
from arcade.gfx import ParticleBurst
from arcade.pixelart import texture_from_rows

COLS = 15                      # columnas del tablero (las filas dependen del alto de pantalla)
START_INTERVAL = 0.17          # segundos por paso al inicio...
MIN_INTERVAL = 0.075           # ...y lo más rápido que llega a ser
GOLDEN_EVERY = 5               # cada cuántas manzanas aparece la dorada
GOLDEN_TIME = 6.5              # segundos que dura la manzana dorada
KEYS = {
    273: (0, 1), 119: (0, 1),      # flecha arriba, W
    274: (0, -1), 115: (0, -1),    # flecha abajo, S
    276: (-1, 0), 97: (-1, 0),     # flecha izquierda, A
    275: (1, 0), 100: (1, 0),      # flecha derecha, D
}


def _checker_texture():
    """Textura de 2x2 píxeles (dos tonos de verde) que se repite para formar el damero."""
    palette = {"a": "#17372F", "b": "#1C4538"}
    return texture_from_rows(["ab", "ba"], palette, repeat=True)


def _lerp(a, b, t):
    return a + (b - a) * t


class SnakeGame(GameScreen):

    # ------------------------------------------------------------------ construcción
    def build_game(self, layer):
        self.phase = "ready"            # "ready" (esperando) | "play" | "dead"
        self.time = 0.0
        self.step_t = 0.0
        self.interval = START_INTERVAL
        self.body = []
        self.queue = []
        self.direction = (1, 0)
        self.prev_tail = None
        self.grow = 0
        self.eaten = 0
        self.apple = (0, 0)
        self.golden = None              # (x, y, tiempo_restante) o None
        self.dead_timer = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.cell = 24.0
        self.cols, self.rows = COLS, 20
        self.bx = self.by = 0.0
        self._touch_start = {}
        self._keys_bound = False

        with layer.canvas.before:
            PushMatrix()
            self.shake_tr = Translate(0, 0)

        with layer.canvas:
            # Tablero: UN rectángulo con la textura de damero repetida.
            Color(1, 1, 1, 1)
            self.board = Rectangle(texture=_checker_texture(), size=(10, 10))
            self.border_color = Color(*hx("#2EC4B6"))
            self.border_color.a = 0.55
            self.border = Line(rectangle=(0, 0, 10, 10), width=2)

            # Manzana normal: sombra, cuerpo, brillo, hoja y tallo.
            self.apple_shadow_c = Color(0, 0, 0, 0.25)
            self.apple_shadow = Ellipse(size=(1, 1))
            self.apple_c = Color(*hx("#E5484D"))
            self.apple_body = Ellipse(size=(1, 1))
            Color(1, 1, 1, 0.55)
            self.apple_shine = Ellipse(size=(1, 1))
            Color(*hx("#58C93D"))
            self.apple_leaf = Ellipse(size=(1, 1))

            # Manzana dorada con anillo de tiempo.
            self.gold_glow_c = Color(1, 0.85, 0.2, 0.0)
            self.gold_glow = Ellipse(size=(1, 1))
            self.gold_c = Color(*hx("#FFC933"))
            self.gold_c.a = 0
            self.gold_body = Ellipse(size=(1, 1))
            self.gold_shine_c = Color(1, 1, 1, 0)
            self.gold_shine = Ellipse(size=(1, 1))
            self.gold_ring_c = Color(1, 0.93, 0.5, 0)
            self.gold_ring = Line(circle=(0, 0, 1, 0, 360), width=2.2)

            # Serpiente: contorno oscuro, cuerpo, franja de brillo; luego cabeza y ojos.
            self.snake_edge_c = Color(*hx("#0E5C4E"))
            self.snake_edge = Line(points=[0, 0, 1, 1], width=2, cap="round", joint="round")
            self.snake_c = Color(*hx("#2EC4B6"))
            self.snake_line = Line(points=[0, 0, 1, 1], width=2, cap="round", joint="round")
            self.snake_shine_c = Color(*hx("#7FE8DC"))
            self.snake_shine = Line(points=[0, 0, 1, 1], width=1, cap="round", joint="round")
            self.head_edge_c = Color(*hx("#0E5C4E"))
            self.head_edge = Ellipse(size=(1, 1))
            self.head_c = Color(*hx("#34D6C6"))
            self.head = Ellipse(size=(1, 1))
            Color(1, 1, 1, 1)
            self.eyes = [Ellipse(size=(1, 1)), Ellipse(size=(1, 1))]
            Color(0.05, 0.08, 0.1, 1)
            self.pupils = [Ellipse(size=(1, 1)), Ellipse(size=(1, 1))]

        with layer.canvas.after:
            self.particles = ParticleBurst(layer.canvas.after, capacity=80)
            PopMatrix()
            self.flash_color = Color(1, 0.2, 0.2, 0)
            self.flash_rect = Rectangle(size=(10, 10))

        self.hint_label = Label(
            text="DESLIZA PARA EMPEZAR", font_size="22sp", bold=True, color=(1, 1, 1, 1),
            outline_width=4, outline_color=(0.05, 0.1, 0.12, 1),
            size_hint=(None, None), size=(360, 50), pos_hint={"center_x": 0.5, "center_y": 0.30},
        )
        layer.add_widget(self.hint_label)
        self.bind(size=lambda *_: self._layout())

    # ------------------------------------------------------------------ geometría
    def _layout(self):
        w, h = self.width, self.height
        self.cell = w / COLS
        top_margin, bottom_margin = dp(66), dp(14)
        available = h - top_margin - bottom_margin
        self.cols = COLS
        self.rows = max(10, int(available // self.cell))
        self.bx = 0.0
        self.by = bottom_margin + (available - self.rows * self.cell) / 2
        self.board.pos = (self.bx, self.by)
        self.board.size = (self.cols * self.cell, self.rows * self.cell)
        # tex_coords > 1 repite la textura: cols/2 veces a lo ancho, rows/2 a lo alto.
        sx, sy = self.cols / 2, self.rows / 2
        self.board.tex_coords = (0, 0, sx, 0, sx, sy, 0, sy)
        self.border.rectangle = (self.bx, self.by, self.cols * self.cell, self.rows * self.cell)
        self.flash_rect.size = (w, h)
        self.hint_label.size = (dp(360), dp(50))

    def _pos(self, gx, gy):
        """Centro (en píxeles) de la celda (gx, gy)."""
        return self.bx + (gx + 0.5) * self.cell, self.by + (gy + 0.5) * self.cell

    # ------------------------------------------------------------------ partida
    def new_game(self):
        self._layout()
        mid_x, mid_y = self.cols // 2, self.rows // 2
        self.body = [(mid_x, mid_y), (mid_x - 1, mid_y), (mid_x - 2, mid_y)]
        self.direction = (1, 0)
        self.queue = []
        self.prev_tail = None
        self.grow = 0
        self.eaten = 0
        self.golden = None
        self.interval = START_INTERVAL
        self.step_t = 0.0
        self.phase = "ready"
        self.time = 0.0
        self.dead_timer = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.particles.clear()
        self.hint_label.opacity = 1
        self._place_apple()
        self._draw()

    def _free_cell(self):
        taken = set(self.body)
        taken.add(self.apple)
        if self.golden:
            taken.add(self.golden[:2])
        free = [
            (x, y) for x in range(self.cols) for y in range(self.rows) if (x, y) not in taken
        ]
        return random.choice(free) if free else None

    def _place_apple(self):
        self.apple = (-1, -1)             # para que _free_cell no la considere ocupada
        cell = self._free_cell()
        self.apple = cell if cell else (-1, -1)
        return cell is not None

    # ------------------------------------------------------------------ entrada
    def on_enter(self, *args):
        super().on_enter(*args)
        if not self._keys_bound:
            Window.bind(on_key_down=self._on_key_down)
            self._keys_bound = True

    def on_leave(self, *args):
        super().on_leave(*args)
        if self._keys_bound:
            Window.unbind(on_key_down=self._on_key_down)
            self._keys_bound = False

    def _on_key_down(self, _window, key, *_args):
        if key in KEYS and self.state == "playing":
            self.turn(KEYS[key])
            return True
        return False

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.state != "playing":
            return False
        self._touch_start[touch.uid] = touch.pos
        return True

    def on_touch_move(self, touch):
        start = self._touch_start.get(touch.uid)
        if start is None or self.state != "playing":
            return super().on_touch_move(touch)
        dx, dy = touch.x - start[0], touch.y - start[1]
        if max(abs(dx), abs(dy)) >= dp(20):
            # El eje con más movimiento decide la dirección del giro.
            if abs(dx) > abs(dy):
                self.turn((1 if dx > 0 else -1, 0))
            else:
                self.turn((0, 1 if dy > 0 else -1))
            self._touch_start[touch.uid] = touch.pos   # permite encadenar varios giros
        return True

    def on_touch_up(self, touch):
        self._touch_start.pop(touch.uid, None)
        return super().on_touch_up(touch)

    def turn(self, new_dir):
        """Pide girar hacia `new_dir`. Ignora repetir la dirección o dar media vuelta."""
        last = self.queue[-1] if self.queue else self.direction
        if new_dir == last or new_dir == (-last[0], -last[1]):
            return
        if len(self.queue) < 2:
            self.queue.append(new_dir)
        if self.phase == "ready":
            self.phase = "play"
            self.hint_label.opacity = 0

    # ------------------------------------------------------------------ bucle
    def update(self, dt):
        self.time += dt
        self.particles.update(dt)
        self.shake = max(0.0, self.shake - dt * 3.0)
        amplitude = self.shake * dp(7)
        self.shake_tr.xy = (
            random.uniform(-amplitude, amplitude), random.uniform(-amplitude, amplitude)
        ) if amplitude > 0.05 else (0, 0)
        self.flash = max(0.0, self.flash - dt * 2.2)
        self.flash_color.a = self.flash

        if self.phase == "play":
            self._update_golden(dt)
            self.step_t += dt
            while self.step_t >= self.interval and self.phase == "play":
                self.step_t -= self.interval
                self._step()
        elif self.phase == "dead":
            self.dead_timer += dt
            if self.dead_timer > 0.85:
                self.game_over("¡Auch!")
        self._draw()

    def _update_golden(self, dt):
        if self.golden:
            x, y, left = self.golden
            left -= dt
            self.golden = (x, y, left) if left > 0 else None

    def _step(self):
        """Avanza la serpiente UNA celda."""
        if self.queue:
            self.direction = self.queue.pop(0)
        head = self.body[0]
        new = (head[0] + self.direction[0], head[1] + self.direction[1])

        eats_apple = new == self.apple
        eats_gold = bool(self.golden) and new == self.golden[:2]
        will_pop = not (eats_apple or eats_gold or self.grow > 0)

        # Muro, o cuerpo (la cola cuenta como libre si se va a mover en este paso).
        solid = self.body[:-1] if will_pop else self.body
        if not (0 <= new[0] < self.cols and 0 <= new[1] < self.rows) or new in solid:
            self._die()
            return

        self.body.insert(0, new)
        self.prev_tail = None
        if eats_apple:
            self._eat(new, golden=False)
        elif eats_gold:
            self._eat(new, golden=True)
        elif self.grow > 0:
            self.grow -= 1
        else:
            self.prev_tail = self.body.pop()

    def _eat(self, cell, golden):
        x, y = self._pos(*cell)
        self.eaten += 1
        self.interval = max(MIN_INTERVAL, START_INTERVAL - self.eaten * 0.0032)
        if golden:
            self.add_score(5)
            self.grow += 2
            self.golden = None
            self.play_sound("golden")
            colors = ((1, 0.85, 0.25, 1), (1, 1, 0.7, 1))
        else:
            self.add_score(1)
            self.play_sound("eat")
            colors = ((0.9, 0.28, 0.3, 1), (1, 0.6, 0.6, 1))
            if not self._place_apple():            # tablero lleno: ¡ganaste!
                self.game_over("¡Tablero completo!")
                return
            if self.eaten % GOLDEN_EVERY == 0:
                spot = self._free_cell()
                if spot:
                    self.golden = (spot[0], spot[1], GOLDEN_TIME)
        for color in colors:
            self.particles.emit(x, y, color, count=8, speed=self.cell * 7, size=self.cell * 0.32,
                                life=0.55, gravity=-self.cell * 12)

    def _die(self):
        self.phase = "dead"
        self.shake = 1.0
        self.flash = 0.45
        self.play_sound("hit")
        self.vibrate(70)
        x, y = self._pos(*self.body[0])
        for color in ((0.18, 0.77, 0.71, 1), (0.5, 0.9, 0.86, 1)):
            self.particles.emit(x, y, color, count=10, speed=self.cell * 9, size=self.cell * 0.4,
                                life=0.8, gravity=-self.cell * 14)

    # ------------------------------------------------------------------ dibujo
    def _draw(self):
        c = self.cell
        # --- manzana normal (late un poquito) ---
        if self.apple[0] >= 0:
            ax, ay = self._pos(*self.apple)
            pulse = 1 + 0.07 * math.sin(self.time * 6)
            r = c * 0.40 * pulse
            self.apple_shadow.pos = (ax - r, ay - r * 1.05)
            self.apple_shadow.size = (r * 2, r * 1.9)
            self.apple_body.pos = (ax - r, ay - r * 0.9)
            self.apple_body.size = (r * 2, r * 1.9)
            self.apple_shine.pos = (ax - r * 0.55, ay + r * 0.25)
            self.apple_shine.size = (r * 0.5, r * 0.6)
            self.apple_leaf.pos = (ax + r * 0.05, ay + r * 0.9)
            self.apple_leaf.size = (r * 0.8, r * 0.45)
        else:
            for part in (self.apple_shadow, self.apple_body, self.apple_shine, self.apple_leaf):
                part.size = (0, 0)

        # --- manzana dorada ---
        if self.golden:
            gx, gy, left = self.golden
            px, py = self._pos(gx, gy)
            pulse = 1 + 0.12 * math.sin(self.time * 9)
            r = c * 0.42 * pulse
            blinking = left < 1.8 and int(self.time * 8) % 2 == 0
            alpha = 0.25 if blinking else 1.0
            self.gold_glow_c.a = 0.25 * alpha
            self.gold_glow.pos = (px - r * 1.6, py - r * 1.6)
            self.gold_glow.size = (r * 3.2, r * 3.2)
            self.gold_c.a = alpha
            self.gold_body.pos = (px - r, py - r)
            self.gold_body.size = (r * 2, r * 2)
            self.gold_shine_c.a = 0.7 * alpha
            self.gold_shine.pos = (px - r * 0.55, py + r * 0.15)
            self.gold_shine.size = (r * 0.55, r * 0.65)
            self.gold_ring_c.a = 0.9 * alpha
            self.gold_ring.circle = (px, py, c * 0.72, 0, 360 * left / GOLDEN_TIME)
        else:
            self.gold_glow_c.a = self.gold_c.a = self.gold_shine_c.a = self.gold_ring_c.a = 0

        self._draw_snake()

    def _draw_snake(self):
        c = self.cell
        p = min(1.0, self.step_t / self.interval) if self.phase == "play" else 1.0
        cells = [self._pos(*cell) for cell in self.body]

        # Cabeza interpolada entre la celda anterior (cells[1]) y la nueva (cells[0]).
        if len(cells) > 1 and self.phase != "dead":
            head = (_lerp(cells[1][0], cells[0][0], p), _lerp(cells[1][1], cells[0][1], p))
        else:
            head = cells[0]
        path = [head] + cells[1:]
        # Cola interpolada: se acerca a su celda desde donde estaba antes del paso.
        if self.prev_tail is not None and self.phase != "dead":
            old = self._pos(*self.prev_tail)
            path.append((_lerp(old[0], cells[-1][0], p), _lerp(old[1], cells[-1][1], p)))
        else:
            path.append(cells[-1])

        # Quitamos puntos repetidos (Kivy dibuja mal los segmentos de largo 0).
        points = []
        last = None
        for x, y in path:
            if last is None or abs(x - last[0]) > 0.5 or abs(y - last[1]) > 0.5:
                points += [x, y]
                last = (x, y)
        if len(points) < 4:
            points += [points[0] + 0.6, points[1]]

        self.snake_edge.points = points
        self.snake_edge.width = c * 0.86
        self.snake_line.points = points
        self.snake_line.width = c * 0.72
        self.snake_shine.points = points
        self.snake_shine.width = c * 0.22

        # Cabeza (círculo con contorno) y ojos que miran hacia donde va.
        hx_, hy_ = head
        r = c * 0.47
        self.head_edge.pos = (hx_ - r - 2, hy_ - r - 2)
        self.head_edge.size = (r * 2 + 4, r * 2 + 4)
        self.head.pos = (hx_ - r, hy_ - r)
        self.head.size = (r * 2, r * 2)
        fx, fy = self.direction
        sx, sy = -fy, fx                          # perpendicular
        for i, side in enumerate((1, -1)):
            ex = hx_ + fx * c * 0.16 + sx * side * c * 0.21
            ey = hy_ + fy * c * 0.16 + sy * side * c * 0.21
            er = c * 0.17
            self.eyes[i].pos = (ex - er, ey - er)
            self.eyes[i].size = (er * 2, er * 2)
            pr = c * 0.085
            px = ex + fx * c * 0.05
            py = ey + fy * c * 0.05
            self.pupils[i].pos = (px - pr, py - pr)
            self.pupils[i].size = (pr * 2, pr * 2)
        # Al morir, el cuerpo se pone rojizo.
        if self.phase == "dead":
            self.snake_c.rgba = hx("#E5484D")
            self.head_c.rgba = hx("#F26B6F")
        else:
            self.snake_c.rgba = hx("#2EC4B6")
            self.head_c.rgba = hx("#34D6C6")
