"""Pruebas del descubrimiento de juegos, incluido el aislamiento de juegos rotos."""

import sys
import textwrap

import pytest

from arcade.registry import discover, load_game


def test_discovers_the_three_course_games():
    entries = discover()
    ids = [e.folder for e in entries]
    assert {"flappy", "snake", "mario"} <= set(ids)
    assert all(e.ok for e in entries), [e.error for e in entries if not e.ok]


def test_template_is_not_listed_but_can_be_loaded():
    assert "_template" not in [e.folder for e in discover()]
    assert load_game("_template").ok


def _make_games_package(tmp_path, name, games):
    """Crea un paquete de juegos falso en disco: {carpeta: código de su __init__.py}."""
    pkg = tmp_path / name
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for folder, code in games.items():
        sub = pkg / folder
        sub.mkdir()
        (sub / "__init__.py").write_text(textwrap.dedent(code), encoding="utf-8")


@pytest.fixture
def fake_package(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(tmp_path))
    yield tmp_path
    for key in [k for k in sys.modules if k.startswith("fakegames")]:
        del sys.modules[key]


def test_broken_game_is_reported_but_does_not_break_others(fake_package):
    _make_games_package(
        fake_package,
        "fakegames",
        {
            "good": """
                from arcade.game_base import GameInfo, GameScreen
                class G(GameScreen):
                    pass
                GAME = GameInfo(id="good", title="Good", description="d", author="a",
                                color="#112233", screen_class=G)
            """,
            "crashes": "raise RuntimeError('boom al importar')",
            "no_game_var": "x = 1",
            "wrong_id": """
                from arcade.game_base import GameInfo, GameScreen
                class G(GameScreen):
                    pass
                GAME = GameInfo(id="otro", title="T", description="d", author="a",
                                color="#112233", screen_class=G)
            """,
        },
    )
    entries = {e.folder: e for e in discover("fakegames")}
    assert entries["good"].ok
    assert "boom" in entries["crashes"].error
    assert "GAME" in entries["no_game_var"].error
    assert "no coincide" in entries["wrong_id"].error
    # Los que cargaron bien van primero en la lista.
    assert discover("fakegames")[0].folder == "good"
