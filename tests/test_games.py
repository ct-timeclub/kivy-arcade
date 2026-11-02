"""Pruebas de que cada juego cumple el contrato (todos los de games/, incluida la plantilla).

Cuando un alumno añade su carpeta en games/, estas pruebas la recogen solas:
si su juego arranca, se actualiza y termina sin errores, pasa.
"""

import pytest

from arcade.game_base import GameScreen
from arcade.registry import discover, load_game
from arcade.storage import Storage

GAME_FOLDERS = sorted({e.folder for e in discover()} | {"_template"})


@pytest.fixture
def storage(tmp_path):
    return Storage(tmp_path / "data.json")


def make_screen(folder, storage):
    entry = load_game(folder)
    assert entry.ok, entry.error
    screen = entry.info.screen_class(info=entry.info, storage=storage)
    screen.size = (390, 760)   # tamaño de teléfono, para que los juegos tengan dimensiones
    return screen


@pytest.mark.parametrize("folder", GAME_FOLDERS)
def test_game_loads_and_inherits_gamescreen(folder, storage):
    screen = make_screen(folder, storage)
    assert isinstance(screen, GameScreen)
    assert screen.name == folder


@pytest.mark.parametrize("folder", GAME_FOLDERS)
def test_game_runs_a_full_session_without_errors(folder, storage):
    screen = make_screen(folder, storage)
    screen.start_game()
    assert screen.state == "playing", f"el juego falló al iniciar: {screen.state}"

    for _ in range(180):          # ~3 segundos de juego a 60 fps
        screen.update(1 / 60)
    assert screen.state in ("playing", "over"), screen.state

    screen.pause()
    assert screen.state in ("paused", "over")
    screen.resume()

    screen.add_score(3)
    screen.game_over()
    assert screen.state == "over"
    assert storage.plays(folder) >= 1


def test_game_error_is_contained_and_shown(storage):
    """Si el juego lanza una excepción, la pantalla pasa a estado 'error' (la app no se cae)."""
    entry = load_game("flappy")

    class Broken(entry.info.screen_class):
        def update(self, dt):
            raise ValueError("fallo de prueba")

    screen = Broken(info=entry.info, storage=storage)
    screen.size = (390, 760)
    screen.start_game()
    screen._tick(1 / 60)
    assert screen.state == "error"
