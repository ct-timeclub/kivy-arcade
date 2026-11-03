"""Mario 2D: un juego de plataformas con scroll, enemigos, monedas y una meta.

Es el juego más grande de la demo. Está dividido en tres archivos:

    sprites.py  los dibujos en arte de píxeles (letras -> texturas).
    level.py    el mapa del nivel (azulejos, pozos, enemigos, monedas).
    game.py     este archivo: física, controles, cámara y dibujo.

Ideas que muestra:

  * Mapa de azulejos (tiles) y colisiones AABB (cajas alineadas a los ejes) resueltas en
    dos pasos: primero el movimiento horizontal y después el vertical.
  * Pasos de física pequeños (subpasos de 1/120 s) para que nada atraviese el suelo al caer.
  * Salto con detalles de «sensación»: altura variable, tiempo de gracia al borde (coyote
    time) y memoria del botón (jump buffer).
  * Cámara que sigue al jugador, fondo con parallax y dibujo solo de lo que se ve.
  * Controles táctiles con varios dedos a la vez, y teclado en el PC.
  * Estados del juego: jugando, muriendo, ganando (deslizarse por el mástil y caminar).

Medidas: la física está en «azulejos» (1 azulejo = T píxeles en pantalla, T = ancho / 10).
"""

import math

from kivy.core.window import Window
from kivy.graphics import (
    Color,
    Ellipse,
    InstructionGroup,
    PopMatrix,
    PushMatrix,
    Rectangle,
    RoundedRectangle,
    Translate,
    Triangle,
)
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.utils import get_color_from_hex as hx

from arcade.game_base import GameScreen
from arcade.gfx import ParticleBurst, vertical_gradient

from .level import ROWS, SURFACE_Y, build_level
from .sprites import build_textures

# ---- Física (unidades: azulejos y segundos) ------------------------------------------------
EPS = 1e-4
STEP = 1 / 120                 # tamaño máximo de cada subpaso de física
MAX_SPEED = 6.4                # velocidad horizontal máxima
GROUND_ACC, AIR_ACC = 46.0, 26.0
FRICTION = 40.0
GRAVITY = 42.0
JUMP_SPEED = 17.6              # da una altura de salto de ~3.7 azulejos
MAX_FALL = 22.0
COYOTE = 0.09                  # segundos para poder saltar justo después de dejar el borde
JUMP_BUFFER = 0.11             # segundos que se «recuerda» un toque de salto adelantado
STOMP_BOUNCE = 11.5
ENEMY_SPEED = 1.5
PLAYER_W, PLAYER_H = 0.62, 0.92
ENEMY_W, ENEMY_H = 0.72, 0.74
START_LIVES = 3
SKY = ["#4FB3FF", "#9ADBFF", "#E2F5FF"]

KEYS_LEFT, KEYS_RIGHT = {276, 97}, {275, 100}          # flecha izquierda/A, flecha derecha/D
KEYS_JUMP = {32, 273, 119}                              # espacio, flecha arriba, W

TILE_TEXTURES = {
    "G": "grass", "D": "dirt", "B": "brick", "?": "question", "U": "used", "X": "hard",
    "a": "pipe_tl", "b": "pipe_tr", "c": "pipe_bl", "d": "pipe_br",
}


class Body:
    """Una caja con posición (esquina inferior izquierda), tamaño y velocidad, en azulejos."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.hit_wall = False
        self.hit_head = None          # (col, cy) del bloque golpeado con la cabeza


class Enemy(Body):
    def __init__(self, x, y, rect):
        super().__init__(x, y, ENEMY_W, ENEMY_H)
        self.dir = -1
        self.state = "alive"          # "alive" | "squashed" | "dead"
        self.active = False           # no se mueve hasta que se acerca la cámara
        self.t = 0.0
        self.anim = 0.0
        self.rect = rect


class MarioGame(GameScreen):

    # ------------------------------------------------------------------ construcción
    def build_game(self, layer):
        self.tex = build_textures()
        self.level = None
        self.T = 36.0
        self.ctrl_h = 100.0
        self.cam = 0.0
        self.time = 0.0
        self.phase = "play"
        self.lives = START_LIVES
        self.coins = 0
        self.shake = 0.0
        self.flash = 0.0
        self.facing = 1
        self.coyote = 0.0
        self.jump_buffer = 0.0
        self.invincible = 0.0
        self.dying_t = 0.0
        self.end_t = 0.0
        self.respawn_x = 3.0
        self.checkpoint_hit = False
        self.flag_y = 0.0
        self.keys = set()
        self.touch_btn = {}
        self.held = {"left": False, "right": False, "jump": False}
        self.enemies = []
        self.coin_cells = {}
        self.tile_rects = {}
        self.col_groups = []
        self.visible_cols = set()
        self.bumps = {}
        self.pops = []
        self.player = Body(3.0, SURFACE_Y, PLAYER_W, PLAYER_H)
        self._keys_bound = False

        # --- Fondo (pantalla completa) y parallax -------------------------------------
        with layer.canvas.before:
            Color(1, 1, 1, 1)
            self.sky = Rectangle(texture=vertical_gradient(SKY), size=(10, 10))
            self.far_hills = self._make_ellipses("#8ED58A", 4)
            self.near_hills = self._make_ellipses("#63BC5F", 4)
            self.clouds = []
            for _ in range(4):
                Color(1, 1, 1, 0.92)
                self.clouds.append([Ellipse(size=(1, 1)) for _ in range(3)])
            PushMatrix()
            self.cam_tr = Translate(0, 0)          # la cámara: mueve TODO el mundo

        # --- Mundo (se mueve con la cámara) --------------------------------------------
        self.tile_group = InstructionGroup()
        self.deco_group = InstructionGroup()
        self.coin_group = InstructionGroup()
        self.enemy_group = InstructionGroup()
        self.pop_group = InstructionGroup()
        with layer.canvas:
            layer.canvas.add(self.deco_group)
            layer.canvas.add(self.tile_group)
            layer.canvas.add(self.coin_group)
            layer.canvas.add(self.enemy_group)
            layer.canvas.add(self.pop_group)
            self.player_color = Color(1, 1, 1, 1)
            self.player_rect = Rectangle(texture=self.tex["player_idle_r"], size=(1, 1))

        with layer.canvas.after:
            self.particles = ParticleBurst(layer.canvas.after, capacity=90)
            PopMatrix()
            self._build_controls()
            self.flash_color = Color(1, 1, 1, 0)
            self.flash_rect = Rectangle(size=(10, 10))

        self.coin_label = Label(
            text="x 0", font_size="17sp", bold=True, color=(1, 1, 1, 1),
            outline_width=3, outline_color=(0.1, 0.1, 0.15, 1), halign="left", valign="middle",
            size_hint=(None, None),
        )
        # Va en la pantalla (no en `layer`): `layer` queda dentro de la cámara y se movería.
        self.add_widget(self.coin_label)
        self.bind(size=lambda *_: self._layout())

    @staticmethod
    def _make_ellipses(color, count):
        Color(*hx(color))
        return [Ellipse(size=(1, 1)) for _ in range(count)]

    def _build_controls(self):
        """Barra inferior con los botones táctiles ‹ › y saltar, y los corazones de vidas."""
        Color(*hx("#10142A"))
        self.ctrl_bar = Rectangle(size=(10, 10))
        self.ctrl_line_c = Color(*hx("#2EC4B6"))
        self.ctrl_line_c.a = 0.7
        self.ctrl_line = Rectangle(size=(10, 2))
        self.btn = {}
        for name in ("left", "right"):
            bg = Color(1, 1, 1, 0.16)
            shape = RoundedRectangle(size=(1, 1), radius=[dp(18)])
            Color(1, 1, 1, 0.9)
            arrow = Triangle(points=[0, 0, 0, 0, 0, 0])
            self.btn[name] = {"bg": bg, "shape": shape, "arrow": arrow, "rect": (0, 0, 1, 1)}
        bg = Color(0.95, 0.3, 0.3, 0.30)
        shape = Ellipse(size=(1, 1))
        Color(1, 1, 1, 0.92)
        arrow = Triangle(points=[0, 0, 0, 0, 0, 0])
        self.btn["jump"] = {"bg": bg, "shape": shape, "arrow": arrow, "rect": (0, 0, 1, 1)}
        # Corazones
        self.hearts = []
        for _ in range(START_LIVES):
            color = Color(1, 0.3, 0.4, 1)
            parts = (Ellipse(size=(1, 1)), Ellipse(size=(1, 1)), Triangle(points=[0] * 6))
            self.hearts.append((color, parts))
        Color(1, 1, 1, 1)
        self.coin_icon = Rectangle(texture=self.tex["coin_0"], size=(1, 1))

    # ------------------------------------------------------------------ geometría
    def _layout(self):
        w, h = self.width, self.height
        self.ctrl_h = dp(104)
        self.T = min(w / 10.0, (h - self.ctrl_h) / ROWS)
        self.sky.size = (w, h)
        self.flash_rect.size = (w, h)
        self.ctrl_bar.size = (w, self.ctrl_h)
        self.ctrl_line.pos = (0, self.ctrl_h - 2)
        self.ctrl_line.size = (w, 2)

        size, gap, margin = dp(76), dp(12), dp(14)
        y = (self.ctrl_h - size) / 2
        left = (margin, y, size, size)
        right = (margin + size + gap, y, size, size)
        jump_d = dp(92)
        jump = (w - margin - jump_d, (self.ctrl_h - jump_d) / 2, jump_d, jump_d)
        for name, rect in (("left", left), ("right", right), ("jump", jump)):
            item = self.btn[name]
            item["rect"] = rect
            item["shape"].pos = (rect[0], rect[1])
            item["shape"].size = (rect[2], rect[3])
            cx, cy = rect[0] + rect[2] / 2, rect[1] + rect[3] / 2
            s = rect[2] * 0.27
            if name == "left":
                pts = [cx + s, cy + s * 1.15, cx + s, cy - s * 1.15, cx - s, cy]
            elif name == "right":
                pts = [cx - s, cy + s * 1.15, cx - s, cy - s * 1.15, cx + s, cy]
            else:
                pts = [cx - s * 1.15, cy - s, cx + s * 1.15, cy - s, cx, cy + s]
            item["arrow"].points = pts

        # Corazones (arriba a la derecha, bajo la barra) y contador de monedas (arriba izq.)
        row_y = h - dp(56) - dp(30)
        heart = dp(21)
        for i, (_color, (left_lobe, right_lobe, tip)) in enumerate(self.hearts):
            x = w - margin - (START_LIVES - i) * (heart + dp(5))
            left_lobe.pos = (x, row_y + heart * 0.35)
            left_lobe.size = (heart * 0.56, heart * 0.56)
            right_lobe.pos = (x + heart * 0.44, row_y + heart * 0.35)
            right_lobe.size = (heart * 0.56, heart * 0.56)
            tip.points = [x + heart * 0.03, row_y + heart * 0.5, x + heart * 0.97,
                          row_y + heart * 0.5, x + heart * 0.5, row_y]
        self.coin_icon.pos = (margin, row_y)
        self.coin_icon.size = (dp(13), dp(19))
        self.coin_label.size = (dp(90), dp(26))
        self.coin_label.text_size = self.coin_label.size
        self.coin_label.pos = (margin + dp(18), row_y - dp(3))

        if self.level is not None:
            self._position_tiles()

    # ------------------------------------------------------------------ mundo
    def _build_world(self):
        """Crea los azulejos, monedas, enemigos y decorados del nivel (cada partida)."""
        self.level = build_level()
        lvl, T = self.level, self.T

        # Azulejos: un grupo de instrucciones por COLUMNA, para dibujar solo las visibles.
        self.tile_group.clear()
        self.visible_cols = set()
        self.col_groups = []
        self.tile_rects = {}
        for col in range(lvl.cols):
            group = InstructionGroup()
            group.add(Color(1, 1, 1, 1))
            for row in range(ROWS):
                name = TILE_TEXTURES.get(lvl.tiles[row][col])
                if name:
                    rect = Rectangle(texture=self.tex[name], size=(T, T))
                    group.add(rect)
                    self.tile_rects[(col, row)] = rect
            self.col_groups.append(group)

        # Monedas
        self.coin_group.clear()
        self.coin_group.add(Color(1, 1, 1, 1))
        self.coin_cells = {}
        for cell in lvl.coins:
            rect = Rectangle(
                texture=self.tex["coin_0"], size=(T * 0.62, T * 0.87),
                pos=(cell[0] * T + T * 0.19, cell[1] * T + T * 0.06),
            )
            self.coin_group.add(rect)
            self.coin_cells[cell] = rect

        # Enemigos
        self.enemy_group.clear()
        self.enemy_group.add(Color(1, 1, 1, 1))
        self.enemies = []
        for col, y in lvl.enemies:
            rect = Rectangle(texture=self.tex["enemy_a"], size=(T * 0.875, T * 0.875))
            self.enemy_group.add(rect)
            self.enemies.append(Enemy(col + 0.14, y, rect))

        # Monedas que salen de los bloques sorpresa (se reutilizan 4)
        self.pop_group.clear()
        self.pop_group.add(Color(1, 1, 1, 1))
        self.pops = []
        for _ in range(4):
            rect = Rectangle(texture=self.tex["coin_0"], size=(0, 0))
            self.pop_group.add(rect)
            self.pops.append({"rect": rect, "t": 99.0, "x": 0.0, "y": 0.0})

        self._build_deco()
        self._position_tiles()

    def _position_tiles(self):
        """Coloca cada azulejo según el tamaño actual T."""
        T = self.T
        for (col, row), rect in self.tile_rects.items():
            rect.pos = (col * T, (ROWS - 1 - row) * T)
            rect.size = (T, T)

    def _build_deco(self):
        """Arbustos, la meta (mástil y bandera), el castillo y la bandera de control."""
        T, lvl = self.T, self.level
        g = self.deco_group
        g.clear()
        surface = SURFACE_Y * T
        # Arbustos
        for col, scale in ((5, 1.0), (22, 1.3), (50, 1.0), (75, 1.2), (82, 1.0), (118, 1.1)):
            g.add(Color(*hx("#3FA83A")))
            g.add(Ellipse(pos=(col * T, surface - T * 0.05), size=(T * 1.5 * scale, T * 0.85)))
            g.add(Ellipse(pos=((col + 0.9 * scale) * T, surface - T * 0.05),
                          size=(T * 1.9 * scale, T * 1.1 * scale)))
            g.add(Color(*hx("#58C94F")))
            g.add(Ellipse(pos=((col + 0.4) * T, surface + T * 0.25), size=(T * 0.7, T * 0.3)))
        # Bandera de control (checkpoint)
        cx = lvl.checkpoint_col * T + T * 0.45
        g.add(Color(*hx("#E8EEF4")))
        g.add(Rectangle(pos=(cx, surface), size=(T * 0.1, T * 1.9)))
        self.check_color = Color(*hx("#E5484D"))
        g.add(self.check_color)
        self.check_flag = Triangle(points=[
            cx + T * 0.1, surface + T * 1.85, cx + T * 0.1, surface + T * 1.25,
            cx + T * 0.85, surface + T * 1.55,
        ])
        g.add(self.check_flag)
        # Meta
        px = lvl.flag_col * T + T * 0.45
        g.add(Color(*hx("#DCE6EE")))
        g.add(Rectangle(pos=(px, surface), size=(T * 0.1, T * 9.2)))
        g.add(Color(*hx("#FFC933")))
        g.add(Ellipse(pos=(px - T * 0.12, surface + T * 9.1), size=(T * 0.34, T * 0.34)))
        self.goal_color = Color(*hx("#2EC4B6"))
        g.add(self.goal_color)
        self.goal_flag = Triangle(points=[0, 0, 0, 0, 0, 0])
        g.add(self.goal_flag)
        self.flag_y = surface + T * 8.6
        # Castillo
        base = (lvl.flag_col + 4) * T
        g.add(Color(*hx("#B5603A")))
        g.add(Rectangle(pos=(base, surface), size=(T * 4, T * 3)))
        g.add(Color(*hx("#8E4426")))
        for i in range(4):
            g.add(Rectangle(pos=(base + i * T * 1.05, surface + T * 3), size=(T * 0.7, T * 0.55)))
        g.add(Color(*hx("#2B1608")))
        g.add(Rectangle(pos=(base + T * 1.5, surface), size=(T * 1.0, T * 1.5)))
        g.add(Ellipse(pos=(base + T * 1.5, surface + T * 1.0), size=(T * 1.0, T * 1.0)))
        self._update_goal_flag()

    def _update_goal_flag(self):
        T, lvl = self.T, self.level
        px = lvl.flag_col * T + T * 0.45
        y = self.flag_y
        self.goal_flag.points = [px, y, px, y - T * 0.75, px - T * 0.9, y - T * 0.38]

    # ------------------------------------------------------------------ partida
    def new_game(self):
        self._layout()
        self._build_world()
        self.lives = START_LIVES
        self.coins = 0
        self.phase = "play"
        self.time = 0.0
        self.shake = self.flash = 0.0
        self.invincible = 0.0
        self.checkpoint_hit = False
        self.respawn_x = self.level.start_x
        self.bumps = {}
        self.jump_buffer = self.coyote = 0.0
        self._release_all()
        self.particles.clear()
        self.coin_label.text = "x 0"
        self._set_hearts()
        self._spawn_player()
        self._snap_camera()
        self._draw()

    def _spawn_player(self):
        p = self.player
        p.x, p.y = self.respawn_x, float(SURFACE_Y)
        p.vx = p.vy = 0.0
        p.on_ground = False
        self.facing = 1

    def _set_hearts(self):
        for i, (color, _parts) in enumerate(self.hearts):
            color.a = 1.0 if i < self.lives else 0.18

    # ------------------------------------------------------------------ entrada
    def on_enter(self, *args):
        super().on_enter(*args)
        if not self._keys_bound:
            Window.bind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            self._keys_bound = True

    def on_leave(self, *args):
        super().on_leave(*args)
        self._release_all()
        if self._keys_bound:
            Window.unbind(on_key_down=self._on_key_down, on_key_up=self._on_key_up)
            self._keys_bound = False

    def on_game_paused(self):
        self._release_all()

    def _release_all(self):
        self.keys.clear()
        self.touch_btn.clear()
        self.held = {"left": False, "right": False, "jump": False}
        self._refresh_buttons()

    def _on_key_down(self, _window, key, *_args):
        if self.state != "playing":
            return False
        self.keys.add(key)
        if key in KEYS_JUMP:
            self.jump_buffer = JUMP_BUFFER
        return key in KEYS_LEFT | KEYS_RIGHT | KEYS_JUMP

    def _on_key_up(self, _window, key, *_args):
        self.keys.discard(key)
        return False

    def _button_at(self, pos):
        """¿Sobre qué botón táctil está este punto? (con un margen generoso para los dedos)."""
        margin = dp(16)
        for name, item in self.btn.items():
            x, y, w, h = item["rect"]
            if x - margin <= pos[0] <= x + w + margin and pos[1] <= y + h + margin * 2:
                if y - margin <= pos[1]:
                    return name
        return None

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.state != "playing":
            return False
        name = self._button_at(touch.pos)
        if name is None:
            return False
        self.touch_btn[touch.uid] = name
        if name == "jump":
            self.jump_buffer = JUMP_BUFFER
        self._refresh_buttons()
        return True

    def on_touch_move(self, touch):
        if touch.uid in self.touch_btn:
            name = self._button_at(touch.pos)
            if name is None:
                del self.touch_btn[touch.uid]
            else:
                if name == "jump" and self.touch_btn[touch.uid] != "jump":
                    self.jump_buffer = JUMP_BUFFER
                self.touch_btn[touch.uid] = name
            self._refresh_buttons()
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.uid in self.touch_btn:
            del self.touch_btn[touch.uid]
            self._refresh_buttons()
            return True
        return super().on_touch_up(touch)

    def _refresh_buttons(self):
        pressed = set(self.touch_btn.values())
        self.held = {name: name in pressed for name in ("left", "right", "jump")}
        for name, item in self.btn.items():
            base = 0.30 if name == "jump" else 0.16
            item["bg"].a = base + (0.30 if self.held[name] else 0.0)

    def _direction(self):
        left = self.held["left"] or bool(self.keys & KEYS_LEFT)
        right = self.held["right"] or bool(self.keys & KEYS_RIGHT)
        return (1 if right else 0) - (1 if left else 0)

    def _jump_held(self):
        return self.held["jump"] or bool(self.keys & KEYS_JUMP)

    # ------------------------------------------------------------------ bucle principal
    def update(self, dt):
        self.time += dt
        self.invincible = max(0.0, self.invincible - dt)
        steps = max(1, math.ceil(dt / STEP))
        h = dt / steps
        for _ in range(steps):
            if self.state != "playing":
                break
            self._physics(h)
        self._update_effects(dt)
        self._draw()

    def _physics(self, h):
        if self.phase == "play":
            self._player_step(h)
            self._enemies_step(h)
            self._enemy_contacts()
        elif self.phase == "dying":
            self._dying_step(h)
        elif self.phase in ("win_slide", "win_walk", "win_done"):
            self._win_step(h)
            self._enemies_step(h)

    # ------------------------------------------------------------------ colisiones con el mapa
    def _move_x(self, b, dx):
        b.x += dx
        b.hit_wall = False
        if dx == 0:
            return
        lvl = self.level
        y0 = math.floor(b.y + EPS)
        y1 = math.floor(b.y + b.h - EPS)
        if dx > 0:
            col = math.floor(b.x + b.w)
            if any(lvl.is_solid(col, cy) for cy in range(y0, y1 + 1)):
                b.x, b.vx, b.hit_wall = col - b.w - EPS, 0.0, True
        else:
            col = math.floor(b.x)
            if any(lvl.is_solid(col, cy) for cy in range(y0, y1 + 1)):
                b.x, b.vx, b.hit_wall = col + 1 + EPS, 0.0, True

    def _move_y(self, b, dy):
        b.y += dy
        b.on_ground = False
        b.hit_head = None
        lvl = self.level
        x0 = math.floor(b.x + EPS)
        x1 = math.floor(b.x + b.w - EPS)
        if dy <= 0:
            cy = math.floor(b.y)
            if any(lvl.is_solid(col, cy) for col in range(x0, x1 + 1)):
                b.y, b.vy, b.on_ground = cy + 1.0, 0.0, True
        else:
            cy = math.floor(b.y + b.h)
            hits = [col for col in range(x0, x1 + 1) if lvl.is_solid(col, cy)]
            if hits:
                centre = b.x + b.w / 2
                col = min(hits, key=lambda c: abs(c + 0.5 - centre))   # el bloque más centrado
                b.y, b.vy, b.hit_head = cy - b.h - EPS, 0.0, (col, cy)

    # ------------------------------------------------------------------ jugador
    def _player_step(self, h):
        p = self.player
        direction = self._direction()
        if direction:
            accel = (GROUND_ACC if p.on_ground else AIR_ACC) * h
            target = direction * MAX_SPEED
            p.vx += max(-accel, min(accel, target - p.vx))
            self.facing = direction
        else:
            drop = FRICTION * h
            p.vx = 0.0 if abs(p.vx) <= drop else p.vx - math.copysign(drop, p.vx)

        # Salto: se permite un instante después de dejar el suelo y si se tocó un poco antes.
        self.coyote = COYOTE if p.on_ground else max(0.0, self.coyote - h)
        self.jump_buffer = max(0.0, self.jump_buffer - h)
        if self.jump_buffer > 0 and self.coyote > 0:
            p.vy = JUMP_SPEED
            self.coyote = self.jump_buffer = 0.0
            self.play_sound("jump")
        p.vy -= GRAVITY * h
        if p.vy > 5 and not self._jump_held():      # soltar el botón corta el salto
            p.vy -= 70 * h
        p.vy = max(p.vy, -MAX_FALL)

        was_air = not p.on_ground
        self._move_x(p, p.vx * h)
        self._move_y(p, p.vy * h)
        if p.hit_head:
            self._hit_block(*p.hit_head)
        if was_air and p.on_ground:               # polvito al aterrizar
            self.particles.emit((p.x + p.w / 2) * self.T, p.y * self.T, (1, 1, 1, 0.7),
                                count=3, speed=self.T * 1.6, size=self.T * 0.25, life=0.3,
                                gravity=-self.T * 4)

        if p.y < -1.0:
            self._die(fell=True)
            return
        self._collect_coins()
        self._check_checkpoint()
        if p.x + p.w > self.level.flag_col + 0.35 and p.y < SURFACE_Y + 9.5:
            self._start_win()

    def _collect_coins(self):
        p = self.player
        for col in range(math.floor(p.x), math.floor(p.x + p.w) + 1):
            for cy in range(math.floor(p.y), math.floor(p.y + p.h) + 1):
                rect = self.coin_cells.pop((col, cy), None)
                if rect is not None:
                    rect.size = (0, 0)
                    self._add_coin(col + 0.5, cy + 0.5)

    def _add_coin(self, x, y):
        self.coins += 1
        self.add_score(10)
        self.coin_label.text = f"x {self.coins}"
        self.play_sound("coin")
        self.particles.emit(x * self.T, y * self.T, (1, 0.85, 0.2, 1), count=6,
                            speed=self.T * 3, size=self.T * 0.22, life=0.45, gravity=-self.T * 7)

    def _check_checkpoint(self):
        if not self.checkpoint_hit and self.player.x > self.level.checkpoint_col:
            self.checkpoint_hit = True
            self.respawn_x = self.level.checkpoint_col + 0.5
            self.check_color.rgba = hx("#2EC4B6")
            self.play_sound("point")
            self.particles.emit((self.level.checkpoint_col + 0.9) * self.T,
                                (SURFACE_Y + 1.5) * self.T, (0.5, 1, 0.9, 1), count=10,
                                speed=self.T * 3, size=self.T * 0.25, life=0.6,
                                gravity=-self.T * 5)

    # ------------------------------------------------------------------ bloques
    def _hit_block(self, col, cy):
        lvl = self.level
        letter = lvl.tile(col, cy)
        if letter not in ("?", "B"):
            return
        row = ROWS - 1 - cy
        self.bumps[(col, row)] = 0.0
        if letter == "?":
            lvl.set_tile(col, cy, "U")
            self.tile_rects[(col, row)].texture = self.tex["used"]
            self._add_coin(col + 0.5, cy + 1.2)
            for pop in self.pops:                       # moneda que sale volando del bloque
                if pop["t"] > 0.6:
                    pop.update(t=0.0, x=col + 0.5, y=cy + 1.0)
                    break
        else:
            self.play_sound("bump")
            self.particles.emit((col + 0.5) * self.T, (cy + 0.5) * self.T, hx("#D9722B"),
                                count=5, speed=self.T * 2.4, size=self.T * 0.22, life=0.4,
                                gravity=-self.T * 9)
        # Un enemigo parado encima del bloque cae derrotado.
        for e in self.enemies:
            if e.state == "alive" and abs(e.x + e.w / 2 - (col + 0.5)) < 0.8 \
                    and abs(e.y - (cy + 1)) < 0.35:
                self._squash(e)

    # ------------------------------------------------------------------ enemigos
    def _enemies_step(self, h):
        for e in self.enemies:
            if e.state == "dead":
                continue
            if e.state == "squashed":
                e.t += h
                if e.t > 0.5:
                    e.state = "dead"
                    e.rect.size = (0, 0)
                continue
            if not e.active:
                if e.x * self.T < self.cam + self.width + self.T * 2:
                    e.active = True
                else:
                    continue
            e.vy = max(e.vy - GRAVITY * h, -MAX_FALL)
            self._move_x(e, e.dir * ENEMY_SPEED * h)
            if e.hit_wall:
                e.dir = -e.dir
            self._move_y(e, e.vy * h)
            if e.on_ground:       # en un borde, dan media vuelta en vez de caerse
                ahead = e.x + e.w / 2 + e.dir * (e.w / 2 + 0.08)
                if not self.level.is_solid(math.floor(ahead), math.floor(e.y - 0.05)):
                    e.dir = -e.dir
            e.anim += h
            if e.y < -2:
                e.state = "dead"
                e.rect.size = (0, 0)

    def _enemy_contacts(self):
        p = self.player
        for e in self.enemies:
            if e.state != "alive" or not e.active:
                continue
            if (p.x < e.x + e.w and p.x + p.w > e.x
                    and p.y < e.y + e.h and p.y + p.h > e.y):
                if p.vy < 0 and p.y > e.y + e.h * 0.45:      # lo pisó desde arriba
                    self._squash(e)
                    p.vy = STOMP_BOUNCE + (3 if self._jump_held() else 0)
                    p.y = e.y + e.h
                else:
                    self._die()
                    return

    def _squash(self, e):
        e.state = "squashed"
        e.t = 0.0
        self.add_score(25)
        self.play_sound("stomp")
        self.particles.emit((e.x + e.w / 2) * self.T, (e.y + 0.2) * self.T, hx("#8B4A1F"),
                            count=7, speed=self.T * 3, size=self.T * 0.25, life=0.5,
                            gravity=-self.T * 8)

    # ------------------------------------------------------------------ vidas
    def _die(self, fell=False):
        if self.phase != "play" or (self.invincible > 0 and not fell):
            return
        self.phase = "dying"
        self.dying_t = 0.0
        self.lives -= 1
        self._set_hearts()
        p = self.player
        p.vx, p.vy = 0.0, 13.0
        self.shake = 0.6
        self.play_sound("die")
        self.vibrate(80)

    def _dying_step(self, h):
        """Animación de derrota: el personaje salta y cae atravesando el suelo."""
        p = self.player
        self.dying_t += h
        p.vy -= GRAVITY * h
        p.y += p.vy * h
        if p.y < -3 or self.dying_t > 2.5:
            if self.lives <= 0:
                self.game_over("Sin vidas")
            else:
                self._spawn_player()
                self.phase = "play"
                self.invincible = 1.8
                self._snap_camera()

    # ------------------------------------------------------------------ meta
    def _start_win(self):
        self.phase = "win_slide"
        p = self.player
        p.vx = p.vy = 0.0
        p.x = self.level.flag_col + 0.45 - p.w
        self.add_score(200 + 50 * self.lives)
        self.play_sound("win")
        self.end_t = 0.0
        for color in ((1, 0.85, 0.2, 1), (0.3, 0.9, 0.8, 1), (1, 0.4, 0.5, 1)):
            self.particles.emit((self.level.flag_col + 0.5) * self.T, (SURFACE_Y + 8) * self.T,
                                color, count=10, speed=self.T * 5, size=self.T * 0.3, life=1.2,
                                gravity=-self.T * 6)

    def _win_step(self, h):
        p = self.player
        T = self.T
        if self.phase == "win_slide":
            p.y = max(p.y - 5.0 * h, SURFACE_Y)
            self.flag_y = max(self.flag_y - 5.0 * T * h, (SURFACE_Y + 1.0) * T)
            self._update_goal_flag()
            if p.y <= SURFACE_Y:
                self.phase = "win_walk"
        elif self.phase == "win_walk":
            p.vy = max(p.vy - GRAVITY * h, -MAX_FALL)
            self._move_x(p, 3.2 * h)
            self._move_y(p, p.vy * h)
            self.facing = 1
            if p.x > self.level.flag_col + 4.6:
                self.phase = "win_done"
                self.end_t = 0.0
        else:
            self.end_t += h
            if self.end_t > 0.7:
                self.game_over("¡Nivel completado!")

    # ------------------------------------------------------------------ cámara y efectos
    def _camera_target(self):
        p, T = self.player, self.T
        target = (p.x + p.w / 2) * T - self.width * 0.42
        return max(0.0, min(target, self.level.cols * T - self.width))

    def _snap_camera(self):
        self.cam = self._camera_target()

    def _update_effects(self, dt):
        self.cam += (self._camera_target() - self.cam) * min(1.0, dt * 9)
        self.particles.update(dt)
        self.shake = max(0.0, self.shake - dt * 3)
        self.flash = max(0.0, self.flash - dt * 2.5)
        self.flash_color.a = self.flash
        for key in list(self.bumps):                     # animación de rebote de los bloques
            self.bumps[key] += dt
            if self.bumps[key] > 0.2:
                del self.bumps[key]
                self.tile_rects[key].pos = (key[0] * self.T, (ROWS - 1 - key[1]) * self.T)
        for pop in self.pops:
            pop["t"] += dt

    # ------------------------------------------------------------------ dibujo
    def _draw(self):
        T, W = self.T, self.width
        shake_x = shake_y = 0.0
        if self.shake > 0.05:
            amp = self.shake * T * 0.18
            shake_x, shake_y = (math.sin(self.time * 70) * amp, math.cos(self.time * 83) * amp)
        self.cam_tr.xy = (-self.cam + shake_x, self.ctrl_h + shake_y)

        self._draw_background()
        self._draw_visible_columns()
        for (col, row), t in self.bumps.items():          # los bloques golpeados suben un poco
            self.tile_rects[(col, row)].pos = (
                col * T, (ROWS - 1 - row) * T + math.sin(t / 0.2 * math.pi) * T * 0.3)

        frame = (0, 1, 2, 1)[int(self.time * 8) % 4]
        left, right = self.cam - T, self.cam + W + T
        for (col, cy), rect in self.coin_cells.items():
            if left <= col * T <= right:
                rect.texture = self.tex[f"coin_{frame}"]

        for e in self.enemies:
            if e.state == "dead":
                continue
            if e.state == "squashed":
                rect_tex, size = self.tex["enemy_squashed"], (T * 0.875, T * 0.875)
            else:
                name = "enemy_a" if int(e.anim * 5) % 2 == 0 else "enemy_b"
                rect_tex, size = self.tex[name], (T * 0.875, T * 0.875)
            e.rect.texture = rect_tex
            e.rect.size = size
            e.rect.pos = ((e.x - (0.875 - e.w) / 2) * T, e.y * T)

        for pop in self.pops:                            # moneda que sale del bloque
            rect = pop["rect"]
            if pop["t"] < 0.6:
                rise = math.sin(min(pop["t"] / 0.6, 1.0) * math.pi) * 1.6
                rect.texture = self.tex[f"coin_{(0, 1, 2, 1)[int(pop['t'] * 14) % 4]}"]
                rect.size = (T * 0.5, T * 0.8)
                rect.pos = ((pop["x"] - 0.25) * T, (pop["y"] + rise) * T)
            else:
                rect.size = (0, 0)

        self._draw_player()

    def _draw_player(self):
        p, T = self.player, self.T
        if self.phase == "dying":
            name = "jump"
        elif not p.on_ground:
            name = "jump"
        elif abs(p.vx) > 0.5:
            name = "run1" if int(self.time * 11) % 2 == 0 else "run2"
        else:
            name = "idle"
        side = "r" if self.facing >= 0 else "l"
        self.player_rect.texture = self.tex[f"player_{name}_{side}"]
        self.player_rect.size = (T * 0.75, T)
        self.player_rect.pos = ((p.x + p.w / 2 - 0.375) * T, p.y * T)
        blink = self.invincible > 0 and int(self.time * 14) % 2 == 0
        self.player_color.a = 0.35 if blink else 1.0

    def _draw_visible_columns(self):
        """Solo se dibujan las columnas de azulejos que caben en pantalla."""
        T, cols = self.T, self.level.cols
        first = max(0, int(self.cam // T) - 1)
        last = min(cols - 1, int((self.cam + self.width) // T) + 1)
        wanted = set(range(first, last + 1))
        for col in self.visible_cols - wanted:
            self.tile_group.remove(self.col_groups[col])
        for col in wanted - self.visible_cols:
            self.tile_group.add(self.col_groups[col])
        self.visible_cols = wanted

    def _draw_background(self):
        """Colinas y nubes que se mueven más lento que el nivel (parallax)."""
        T, base = self.T, self.ctrl_h
        for hills, speed, period, widths, offsets, scale in (
            (self.far_hills, 0.22, 34 * T, (9, 7, 10, 8), (0, 9, 17, 26), 3.4),
            (self.near_hills, 0.45, 26 * T, (7, 5, 8, 6), (2, 9, 15, 21), 2.3),
        ):
            for hill, width, offset in zip(hills, widths, offsets):
                x = (offset * T - self.cam * speed) % period - width * T
                hill.size = (width * T, scale * T * (0.7 + width / 24))
                hill.pos = (x, base - hill.size[1] * 0.42)
        shapes = ((0, 0, 2.2, 0.8), (0.7, 0.35, 1.5, 0.9), (1.6, 0.1, 1.5, 0.75))
        for i, cloud in enumerate(self.clouds):
            x = (i * 7.5 * T + 2 * T - self.cam * 0.12) % (30 * T) - 3 * T
            y = base + (9.2 + (i % 2) * 2.2 + (i % 3) * 0.6) * T
            for part, (ox, oy, cw, ch) in zip(cloud, shapes):
                part.pos = (x + ox * T, y + oy * T)
                part.size = (cw * T, ch * T)
