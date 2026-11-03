"""Pruebas de Flappy Bird: espera al primer toque, física, colisiones y puntuación."""

import random

import pytest

from arcade.registry import load_game
from arcade.storage import Storage

DT = 1 / 60


@pytest.fixture
def game(tmp_path):
    random.seed(1234)                       # tubos «al azar» pero repetibles
    entry = load_game("flappy")
    assert entry.ok, entry.error
    screen = entry.info.screen_class(info=entry.info, storage=Storage(tmp_path / "data.json"))
    screen.size = (360, 640)
    screen.start_game()
    return screen


def autopilot(game):
    """Aletea cuando el pájaro está por debajo del centro del hueco del próximo tubo."""
    u = game.u
    target = game.height * 0.5
    for pipe in sorted(game.pipes, key=lambda p: p["x"]):
        if pipe["x"] + 40 * u > game.bird_x:
            target = pipe["gap_y"] - 26 * u
            break
    if game.phase == "ready" or (game.bird_y < target and game.bird_vy <= 0):
        game._flap()


def test_waits_for_the_first_tap(game):
    first_pipe_x = [p["x"] for p in game.pipes]
    for _ in range(120):
        game.update(DT)
    assert game.phase == "ready"
    assert [p["x"] for p in game.pipes] == first_pipe_x       # nada se mueve todavía
    assert game.score == 0


def test_flap_starts_the_game_and_lifts_the_bird(game):
    start_y = game.bird_y
    game._flap()
    assert game.phase == "play"
    for _ in range(10):
        game.update(DT)
    assert game.bird_y > start_y


def test_falling_to_the_ground_ends_the_game(game):
    game._flap()
    for _ in range(60 * 8):                  # sin volver a aletear: cae y choca
        game.update(DT)
        if game.state == "over":
            break
    assert game.state == "over"
    assert game.phase == "dead"
    assert game.storage.plays("flappy") == 1


def test_bird_cannot_leave_through_the_ceiling(game):
    game._flap()
    for _ in range(120):
        game.bird_vy = 900 * game.u         # empuje enorme hacia arriba
        game.update(DT)
        if game.phase == "dead":
            break
    assert game.bird_y <= game.top_limit + 0.01


def test_autopilot_passes_pipes_and_scores(game):
    for _ in range(60 * 90):
        if game.state != "playing":
            break
        autopilot(game)
        game.update(DT)
    assert game.score >= 3, f"el piloto automático solo logró {game.score} puntos"


def test_difficulty_increases_with_score(game):
    game._flap()
    game.score = 30
    for _ in range(3):
        game.bird_y = game.height * 0.6
        game.bird_vy = 0
        game.update(DT)
    assert game.speed > 138
    assert game.gap < 170


def test_pipes_are_recycled_and_never_more_than_four(game):
    for _ in range(60 * 40):
        if game.state != "playing":
            break
        autopilot(game)
        game.update(DT)
    assert len(game.pipes) == 4
