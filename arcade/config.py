"""Constantes generales de la app. No importa Kivy: se puede usar desde cualquier lado."""

APP_NAME = "Kivy Arcade"
APP_VERSION = "0.1.0"

# Paquete de Python donde viven los juegos (la carpeta games/).
GAMES_PACKAGE = "games"

# Tamaños de ventana (en píxeles) que se usan SOLO al probar en el PC,
# para imitar un teléfono vertical u horizontal. En el móvil no se usan.
# Formato 9:16. Es pequeño a propósito: en pantallas con escala del 150 % una ventana más alta
# no cabe en un monitor de 1080p.
DEV_WINDOW_PORTRAIT = (360, 640)
DEV_WINDOW_LANDSCAPE = (640, 360)
