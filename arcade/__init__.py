"""Kivy Arcade: la app principal (menús, ajustes, puntuaciones) que aloja los juegos.

Estructura del paquete:
    config.py     constantes generales (nombre, versión, tamaño de ventana de pruebas).
    theme.py      paleta de colores compartida por toda la app.
    storage.py    guardado local (JSON) de puntuaciones y ajustes.
    game_base.py  GameInfo y GameScreen: el "contrato" que cumple cada juego.
    registry.py   descubre automáticamente los juegos de la carpeta games/.
    widgets.py    widgets reutilizables (botón redondeado, tarjetas, avisos...).
    screens.py    pantallas del menú: inicio, juegos, puntuaciones, ajustes, acerca de.
    app.py        la App principal que une todo.
    dev.py        arranca UN solo juego de forma aislada (para desarrollar).
"""
