"""Paleta de colores de la app (formato RGBA de Kivy: 4 números de 0 a 1).

Se usa desde Python (`theme.ACCENT`) y desde los archivos .kv (`#:import theme arcade.theme`).
Los juegos pueden importarla para verse coherentes con el resto de la app.
"""

from kivy.utils import get_color_from_hex as hx

BG = hx("#0F1226")        # fondo general
SURFACE = hx("#1B1F3B")   # tarjetas y paneles
SURFACE2 = hx("#2A3060")  # botones secundarios
TEXT = hx("#F2F4FF")      # texto principal
MUTED = hx("#9AA3C7")     # texto secundario
ACCENT = hx("#7C5CFF")    # color de la marca
SUCCESS = hx("#2EC4B6")
WARNING = hx("#FFB703")
DANGER = hx("#E5484D")
