"""Herramientas gráficas comunes: degradados y partículas.

Los juegos las usan para verse bien con poco código. Todo se dibuja con instrucciones del
canvas de Kivy (sin imágenes), así funciona igual en el PC, Android e iOS.
"""

import math
import random

from kivy.graphics import Color, Ellipse
from kivy.graphics.texture import Texture
from kivy.utils import get_color_from_hex


def vertical_gradient(colors, steps=64):
    """Textura de degradado vertical. `colors` va de ARRIBA a ABAJO, p. ej. ["#3AA7FF", "#D6F3FF"].

    Se usa estirándola sobre un Rectangle del tamaño que quieras:
        Rectangle(texture=vertical_gradient(["#3AA7FF", "#D6F3FF"]), pos=(0, 0), size=pantalla)
    """
    stops = [get_color_from_hex(c) for c in colors]
    data = bytearray()
    for row in range(steps - 1, -1, -1):  # OpenGL empieza por abajo
        t = row / (steps - 1)               # 0 = arriba, 1 = abajo
        position = t * (len(stops) - 1)
        index = min(int(position), len(stops) - 2)
        local = position - index
        for channel in range(4):
            value = stops[index][channel] * (1 - local) + stops[index + 1][channel] * local
            data.append(round(value * 255))
    texture = Texture.create(size=(1, steps), colorfmt="rgba")
    texture.blit_buffer(bytes(data), colorfmt="rgba", bufferfmt="ubyte")
    texture.mag_filter = "linear"
    return texture


class ParticleBurst:
    """Pequeñas explosiones de partículas (plumas, chispas, polvo...).

    Reserva de una vez un grupo de círculos en el canvas que se reutilizan, así que no crea ni
    destruye objetos mientras se juega (importante para que el móvil no se trabe).

        self.particles = ParticleBurst(layer.canvas.after)          # al construir el juego
        self.particles.emit(x, y, (1, 0.8, 0, 1), count=14)         # cuando pase algo
        self.particles.update(dt)                                    # en update(dt)
    """

    def __init__(self, canvas, capacity=96):
        self._free = list(range(capacity))
        self._alive = {}
        self._items = []
        for _ in range(capacity):
            color = Color(1, 1, 1, 0)
            dot = Ellipse(pos=(0, 0), size=(0, 0))
            canvas.add(color)
            canvas.add(dot)
            self._items.append((color, dot))

    def emit(self, x, y, color, count=12, speed=180, size=7, life=0.6, gravity=-420, up=0):
        """Lanza `count` partículas desde (x, y) en todas direcciones.

        speed    velocidad inicial (píxeles/s).   size  diámetro inicial.
        life     segundos que viven.              gravity  aceleración vertical (negativa = cae).
        up       impulso extra hacia arriba (para que salten en lugar de abrirse en círculo).
        """
        for _ in range(count):
            if not self._free:
                return
            index = self._free.pop()
            angle = random.uniform(0, math.tau)
            power = random.uniform(0.35, 1.0) * speed
            self._alive[index] = {
                "x": x,
                "y": y,
                "vx": math.cos(angle) * power,
                "vy": math.sin(angle) * power + up,
                "t": 0.0,
                "life": life * random.uniform(0.7, 1.15),
                "size": size * random.uniform(0.6, 1.2),
                "gravity": gravity,
                "color": color,
            }

    def update(self, dt):
        """Mueve y desvanece las partículas vivas."""
        for index in list(self._alive):
            p = self._alive[index]
            p["t"] += dt
            color, dot = self._items[index]
            if p["t"] >= p["life"]:
                del self._alive[index]
                self._free.append(index)
                color.a = 0
                dot.size = (0, 0)
                continue
            p["vy"] += p["gravity"] * dt
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            fade = 1 - p["t"] / p["life"]
            size = p["size"] * (0.4 + 0.6 * fade)
            r, g, b, a = p["color"]
            color.rgba = (r, g, b, a * fade)
            dot.size = (size, size)
            dot.pos = (p["x"] - size / 2, p["y"] - size / 2)

    def clear(self):
        """Apaga todas las partículas (al reiniciar la partida)."""
        for index in list(self._alive):
            color, dot = self._items[index]
            color.a = 0
            dot.size = (0, 0)
            self._free.append(index)
        self._alive.clear()
