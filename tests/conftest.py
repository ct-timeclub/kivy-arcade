"""Configuración de las pruebas.

Kivy lee sys.argv al importarse (y pytest usa argumentos propios), así que lo desactivamos.
Estas pruebas necesitan una ventana: en tu PC se abre brevemente; en GitHub Actions se usa
xvfb (una pantalla virtual).
"""

import os
import sys
from pathlib import Path

os.environ["KIVY_NO_ARGS"] = "1"
os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")

# Permite hacer `import arcade` y `import games` desde las pruebas.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
