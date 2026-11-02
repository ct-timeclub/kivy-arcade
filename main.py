"""Punto de entrada de la app completa.

    python main.py

Android (buildozer) e iOS (kivy-ios) buscan exactamente este archivo: main.py en la raíz.
En el PC la ventana imita un teléfono vertical para que se vea como en el móvil.
"""

from kivy.config import Config
from kivy.utils import platform

# Esta configuración debe ir ANTES de importar Window (o sea, antes de importar la app).
if platform not in ("android", "ios"):
    from arcade.config import DEV_WINDOW_PORTRAIT

    Config.set("graphics", "width", str(DEV_WINDOW_PORTRAIT[0]))
    Config.set("graphics", "height", str(DEV_WINDOW_PORTRAIT[1]))
    Config.set("graphics", "minimum_width", "300")
    Config.set("graphics", "minimum_height", "500")

from arcade.app import ArcadeApp  # noqa: E402

if __name__ == "__main__":
    ArcadeApp().run()
