"""Widgets reutilizables de la app (botón redondeado, tarjetas, avisos...).

Aquí cada widget tiene dos partes:
  * la clase de Python (sus propiedades y su lógica), y
  * una regla en lenguaje KV (su aspecto), cargada con Builder.load_string al final.

Nota: NO se usa dp() al definir las clases (a nivel de módulo) porque la ventana aún
no existe y la densidad de pantalla no se conoce. Los tamaños en dp van en el KV.
"""

from kivy.lang import Builder
from kivy.properties import ColorProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from arcade import theme


class RoundedButton(ButtonBehavior, Label):
    """Botón con esquinas redondeadas. Se usa igual que un Button (on_release, text...)."""

    bg = ColorProperty(theme.SURFACE2)   # color de fondo
    radius = NumericProperty(16)         # redondez de las esquinas


class Header(BoxLayout):
    """Barra superior de las pantallas secundarias: botón «<» y título."""

    title = StringProperty("")


class Chip(Label):
    """Etiqueta pequeña con fondo de color (para mostrar los juegos en el menú)."""

    bg = ColorProperty(theme.ACCENT)


class GameCard(ButtonBehavior, BoxLayout):
    """Tarjeta de la lista de juegos: color, título, descripción, autor y mejor puntuación."""

    title = StringProperty("")
    description = StringProperty("")
    author = StringProperty("")
    initial = StringProperty("?")
    best_text = StringProperty("0")
    accent = ColorProperty(theme.ACCENT)


class ScoreRow(BoxLayout):
    """Fila de la pantalla de puntuaciones."""

    title = StringProperty("")
    plays_text = StringProperty("")
    best_text = StringProperty("0")
    accent = ColorProperty(theme.ACCENT)


class Toast(Label):
    """Aviso corto flotante (se usa con ArcadeApp.toast("mensaje"))."""


Builder.load_string(
    """
#:import theme arcade.theme
#:import dp kivy.metrics.dp

<RoundedButton>:
    color: theme.TEXT
    bold: True
    font_size: "18sp"
    radius: dp(16)
    canvas.before:
        Color:
            rgba: self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]
        # Capa negra translúcida: oscurece el botón mientras se mantiene presionado.
        Color:
            rgba: (0, 0, 0, 0.25) if self.state == "down" else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [self.radius]

<Header>:
    size_hint_y: None
    height: dp(64)
    padding: dp(12), dp(8)
    spacing: dp(12)
    RoundedButton:
        text: "<"
        size_hint_x: None
        width: dp(48)
        on_release: app.go_back()
    Label:
        text: root.title
        font_size: "22sp"
        bold: True
        color: theme.TEXT
        halign: "left"
        valign: "middle"
        text_size: self.size

<Chip>:
    size_hint: None, None
    height: dp(30)
    width: self.texture_size[0] + dp(26)
    font_size: "13sp"
    bold: True
    color: 1, 1, 1, 1
    canvas.before:
        Color:
            rgba: self.bg
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15)]

<GameCard>:
    size_hint_y: None
    height: dp(112)
    padding: dp(12)
    spacing: dp(14)
    canvas.before:
        Color:
            rgba: theme.SURFACE
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]
        Color:
            rgba: (0, 0, 0, 0.25) if self.state == "down" else (0, 0, 0, 0)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(18)]
    # Cuadro de color con la inicial del juego
    FloatLayout:
        size_hint_x: None
        width: dp(88)
        canvas.before:
            Color:
                rgba: root.accent
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(14)]
        Label:
            text: root.initial
            font_size: "44sp"
            bold: True
            color: 1, 1, 1, 1
            pos_hint: {"center_x": .5, "center_y": .5}
    # Título, descripción y autor
    BoxLayout:
        orientation: "vertical"
        Label:
            size_hint_y: 0.36
            text: root.title
            font_size: "20sp"
            bold: True
            color: theme.TEXT
            halign: "left"
            valign: "bottom"
            text_size: self.size
        Label:
            size_hint_y: 0.40
            text: root.description
            font_size: "13sp"
            color: theme.MUTED
            halign: "left"
            valign: "middle"
            text_size: self.size
            max_lines: 2
        Label:
            size_hint_y: 0.24
            text: root.author
            font_size: "12sp"
            color: theme.MUTED
            halign: "left"
            valign: "top"
            text_size: self.size
    # Mejor puntuación
    BoxLayout:
        orientation: "vertical"
        size_hint_x: None
        width: dp(64)
        Label:
            text: "MEJOR"
            font_size: "11sp"
            color: theme.MUTED
            valign: "bottom"
            text_size: self.size
            halign: "center"
        Label:
            text: root.best_text
            font_size: "26sp"
            bold: True
            color: root.accent

<ScoreRow>:
    size_hint_y: None
    height: dp(68)
    padding: dp(22), dp(8), dp(16), dp(8)
    spacing: dp(12)
    canvas.before:
        Color:
            rgba: theme.SURFACE
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(16)]
        Color:
            rgba: root.accent
        RoundedRectangle:
            pos: self.pos
            size: dp(8), self.height
            radius: [dp(16), 0, 0, dp(16)]
    BoxLayout:
        orientation: "vertical"
        Label:
            text: root.title
            font_size: "18sp"
            bold: True
            color: theme.TEXT
            halign: "left"
            valign: "bottom"
            text_size: self.size
        Label:
            text: root.plays_text
            font_size: "12sp"
            color: theme.MUTED
            halign: "left"
            valign: "top"
            text_size: self.size
    Label:
        text: root.best_text
        size_hint_x: None
        width: dp(80)
        font_size: "28sp"
        bold: True
        color: root.accent
        halign: "right"
        valign: "middle"
        text_size: self.size

<Toast>:
    size_hint: None, None
    size: self.texture_size[0] + dp(32), self.texture_size[1] + dp(22)
    text_size: dp(300), None
    halign: "center"
    font_size: "14sp"
    color: theme.TEXT
    opacity: 0
    pos_hint: {"center_x": .5, "y": .05}
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0.85
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
"""
)
