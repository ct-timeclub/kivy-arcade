"""Ejecuta UN solo juego, sin la app completa. Es para desarrollar y probar tu juego.

    python run_game.py snake

Es lo mismo que:  python -m games.snake
"""

import sys

if __name__ == "__main__":
    # Leemos el nombre del juego y lo quitamos de sys.argv ANTES de importar Kivy,
    # porque Kivy también lee los argumentos de la línea de comandos.
    if len(sys.argv) < 2:
        raise SystemExit("Uso: python run_game.py <id_del_juego>   (ej.: python run_game.py snake)")
    game_id = sys.argv.pop(1)

    from arcade.dev import run_single

    run_single(game_id)
