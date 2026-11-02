"""Prueba de humo de la app completa: construye todo y navega por cada pantalla."""

import pytest

from arcade.app import ArcadeApp


@pytest.fixture
def app(tmp_path):
    application = ArcadeApp(storage_path=tmp_path / "data.json")
    application.build()
    return application


def test_all_menu_screens_exist_and_open(app):
    for name in ("games", "scores", "settings", "about"):
        app.manager.current = name
        screen = app.manager.current_screen
        screen.dispatch("on_pre_enter")        # llena las listas igual que al navegar de verdad
        assert screen.name == name


def test_game_list_has_one_card_per_game(app):
    app.manager.current = "games"
    app.manager.current_screen.dispatch("on_pre_enter")
    cards = app.manager.current_screen.ids.list.children
    assert len(cards) == len(app.entries) >= 3


def test_play_opens_game_and_exit_returns(app):
    app.play("snake")
    game = app.current_game()
    assert game is not None and game.name == "snake"
    game.exit_game()
    assert app.manager.current == "games" or app.manager.current == "menu"


def test_unknown_game_shows_message_instead_of_crashing(app):
    app.play("no_existe")      # no debe lanzar excepción
    assert app.current_game() is None


def test_settings_toggle_is_saved(app):
    settings = app.manager.get_screen("settings")
    settings.dispatch("on_pre_enter")
    assert app.storage.get_setting("sound", True) is True
    settings.toggle("sound")
    assert app.storage.get_setting("sound", True) is False
