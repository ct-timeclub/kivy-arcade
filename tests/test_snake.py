"""Pruebas de Snake: giros, comida, crecimiento, choques y manzana dorada."""

import random

import pytest

from arcade.registry import load_game
from arcade.storage import Storage

DT = 1 / 60


@pytest.fixture
def game(tmp_path):
    random.seed(99)
    entry = load_game("snake")
    assert entry.ok, entry.error
    screen = entry.info.screen_class(info=entry.info, storage=Storage(tmp_path / "data.json"))
    screen.size = (360, 640)
    screen.start_game()
    return screen


def step_until(game, condition, limit=600):
    for _ in range(limit):
        if condition():
            return True
        game.update(DT)
    return condition()


def test_starts_waiting_with_three_segments(game):
    assert game.phase == "ready"
    assert len(game.body) == 3
    head = game.body[0]
    for _ in range(60):
        game.update(DT)
    assert game.body[0] == head                   # no se mueve hasta que el jugador gira


def test_cannot_reverse_or_repeat_direction(game):
    game.turn((-1, 0))                             # media vuelta: se ignora
    assert game.queue == [] and game.phase == "ready"
    game.turn((1, 0))                              # misma dirección: se ignora
    assert game.queue == []
    game.turn((0, 1))
    assert game.queue == [(0, 1)] and game.phase == "play"


def test_turn_queue_keeps_two_quick_swipes(game):
    game.turn((0, 1))
    game.turn((-1, 0))
    game.turn((0, -1))
    assert game.queue == [(0, 1), (-1, 0)]         # el tercero ya no cabe


def test_moving_changes_the_head_position(game):
    head = game.body[0]
    game.turn((0, 1))
    assert step_until(game, lambda: game.body[0] != head)
    assert game.body[0] == (head[0], head[1] + 1)


def test_eating_an_apple_scores_and_grows(game):
    game.turn((0, 1))
    game._step()
    head = game.body[0]
    game.apple = (head[0], head[1] + 1)            # manzana justo delante
    length = len(game.body)
    game._step()
    assert game.score == 1
    assert len(game.body) == length + 1
    assert game.apple != (head[0], head[1] + 1)    # apareció una manzana nueva


def test_hitting_the_wall_ends_the_game(game):
    game.turn((0, 1))
    assert step_until(game, lambda: game.state == "over", limit=60 * 30)
    assert game.phase == "dead"
    assert game.storage.plays("snake") == 1


def test_biting_itself_ends_the_game(game):
    game.body = [(5, 5), (5, 4), (6, 4), (6, 5), (6, 6)]    # la cabeza va a entrar a (6, 5)
    game.direction = (1, 0)
    game.phase = "play"
    game._step()
    assert game.phase == "dead"


def test_the_tail_cell_is_free_to_enter_when_it_moves(game):
    # Cuadrado de 4 celdas: la cabeza entra donde estaba la cola, que ya se está yendo.
    game.body = [(5, 5), (5, 4), (6, 4), (6, 5)]
    game.direction = (1, 0)
    game.phase = "play"
    game._step()
    assert game.phase == "play"


def test_golden_apple_appears_every_five_apples(game):
    game.turn((0, 1))
    game._step()
    for _ in range(5):
        head = game.body[0]
        game.apple = (head[0], head[1] + 1)
        game._step()
    assert game.eaten == 5
    assert game.golden is not None
    assert game.golden[2] > 0


def test_golden_apple_gives_five_points_and_two_extra_segments(game):
    game.turn((0, 1))
    game._step()
    head = game.body[0]
    game.golden = (head[0], head[1] + 1, 6.0)
    length = len(game.body)
    game._step()
    assert game.score == 5
    assert game.grow == 2
    assert len(game.body) == length + 1
    game._step()
    game._step()
    assert len(game.body) == length + 3


def test_game_speeds_up_as_you_eat(game):
    game.turn((0, 1))
    game._step()
    slow = game.interval
    for _ in range(8):
        head = game.body[0]
        game.apple = (head[0], head[1] + 1)
        game._step()
    assert game.interval < slow


def test_greedy_bot_collects_apples(game):
    """Un bot sencillo (va hacia la manzana sin chocar) debe lograr varios puntos."""
    def pilot():
        hx, hy = game.body[0]
        ax, ay = game.golden[:2] if game.golden else game.apple
        dx, dy = game.direction
        best = None
        for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if d == (-dx, -dy):
                continue
            nx, ny = hx + d[0], hy + d[1]
            if not (0 <= nx < game.cols and 0 <= ny < game.rows) or (nx, ny) in game.body[:-1]:
                continue
            dist = abs(nx - ax) + abs(ny - ay)
            if best is None or dist < best[0]:
                best = (dist, d)
        if best and not game.queue:
            game.turn(best[1])

    game.turn((0, 1))
    for _ in range(60 * 60):
        if game.state != "playing":
            break
        pilot()
        game.update(DT)
    assert game.score >= 8, f"el bot solo logró {game.score} puntos"
