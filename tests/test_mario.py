"""Pruebas de Mario 2D: física, bloques, enemigos, vidas y que el nivel SE PUEDE GANAR.

La prueba principal pone un «bot» a jugar el nivel entero en tiempo acelerado (sin esperar a que
pase el tiempo real). Si alguien cambia el nivel y lo vuelve imposible, esta prueba lo detecta.
"""

import math

import pytest

from arcade.registry import load_game
from arcade.storage import Storage
from games.mario.game import JUMP_BUFFER, PLAYER_H
from games.mario.level import ROWS, SURFACE_Y, build_level

DT = 1 / 60


@pytest.fixture
def game(tmp_path):
    entry = load_game("mario")
    assert entry.ok, entry.error
    screen = entry.info.screen_class(info=entry.info, storage=Storage(tmp_path / "data.json"))
    screen.size = (360, 640)
    screen.start_game()
    assert screen.state == "playing"
    return screen


def drive(game):
    """El «bot»: corre a la derecha y salta ante paredes, pozos y enemigos."""
    p, lvl = game.player, game.level
    if getattr(game, "_bot_hold", 0) > 0:
        game._bot_hold -= 1
        if game._bot_hold == 0:
            game.keys.discard(32)
    if game.phase != "play":
        return
    if not p.on_ground:
        # En el aire se suelta la flecha si hay una pared adelante: así se cae sobre el escalón
        # en vez de chocar de lado (control aéreo, como haría una persona).
        wall = math.floor(p.x + p.w + 0.35)
        blocked = any(
            lvl.is_solid(wall, cy) for cy in range(math.floor(p.y), math.floor(p.y + 0.9) + 1)
        )
        (game.keys.discard if blocked else game.keys.add)(275)
        return
    game.keys.add(275)                           # en el suelo: siempre hacia la derecha
    ahead = math.floor(p.x + p.w + 0.5)
    hold = 22                                    # fotogramas con el salto sostenido (salto largo)
    jump = False
    low = math.floor(p.y)
    if any(lvl.is_solid(ahead, cy) for cy in range(low, math.floor(p.y + 0.9) + 1)):
        jump = True
        top = low                                # ¿de qué altura es el obstáculo?
        while lvl.is_solid(ahead, top):
            top += 1
        if top - p.y <= 1.4:
            hold = 9                             # un escalón: salto cortito, como un toque rápido
    # ¿Se acaba el suelo justo adelante? Se salta EN el borde (como haría una persona), no antes.
    edge = math.floor(p.x + p.w + 0.2)
    if not any(lvl.is_solid(edge, cy) for cy in range(0, math.floor(p.y) + 1)):
        jump, hold = True, 22
    for e in game.enemies:                       # ¿un enemigo cerca?
        if e.state == "alive" and 0 < e.x - p.x < 2.4 and abs(e.y - p.y) < 1.2:
            jump, hold = True, 18
    if jump:
        game.keys.add(32)                        # espacio
        game.jump_buffer = JUMP_BUFFER
        game._bot_hold = hold


def test_level_has_expected_pieces():
    level = build_level()
    assert level.cols > 100
    assert len(level.enemies) >= 8 and len(level.coins) >= 40
    flat = "".join("".join(row) for row in level.tiles)
    for letter in "GDB?Xabcd":
        assert letter in flat
    # El suelo de la salida y de la meta existen (nada de caerse al empezar o al final).
    assert level.is_solid(int(level.start_x), SURFACE_Y - 1)
    assert level.is_solid(level.flag_col, SURFACE_Y - 1)


def test_player_stands_on_ground_and_does_not_fall_through(game):
    for _ in range(120):
        game.update(DT)
    assert game.player.on_ground
    assert game.player.y == pytest.approx(SURFACE_Y, abs=0.01)


def test_jump_rises_about_three_and_a_half_tiles_then_lands(game):
    for _ in range(30):
        game.update(DT)
    game.keys.add(32)
    game.jump_buffer = JUMP_BUFFER
    peak = 0.0
    for _ in range(90):
        game.update(DT)
        peak = max(peak, game.player.y - SURFACE_Y)
    assert 3.2 < peak < 4.2
    game.keys.discard(32)
    for _ in range(60):
        game.update(DT)
    assert game.player.on_ground


def test_hitting_a_question_block_gives_a_coin_once(game):
    lvl = game.level
    col, cy = 19, ROWS - 1 - 8                      # el bloque «?» del primer tramo
    assert lvl.tile(col, cy) == "?"
    game.player.x, game.player.y = col + 0.2, cy - PLAYER_H - 0.05
    game.player.vy = 8.0                            # va subiendo y golpea con la cabeza
    coins_before = game.coins
    for _ in range(10):
        game.update(DT)
    assert lvl.tile(col, cy) == "U"
    assert game.coins == coins_before + 1


def test_stomping_an_enemy_kills_it_and_scores(game):
    enemy = game.enemies[0]
    enemy.active = True
    game.player.x, game.player.y = enemy.x, enemy.y + 1.2
    game.player.vy = -3.0
    game.invincible = 0
    score_before = game.score
    for _ in range(12):
        game.update(DT)
    assert enemy.state in ("squashed", "dead")
    assert game.score >= score_before + 25
    assert game.lives == 3


def test_touching_an_enemy_from_the_side_costs_a_life(game):
    enemy = game.enemies[0]
    enemy.active = True
    game.player.x, game.player.y = enemy.x - 0.3, enemy.y
    game.player.vy = 0
    game.invincible = 0
    for _ in range(5):
        game.update(DT)
    assert game.phase == "dying"
    assert game.lives == 2


def test_falling_in_a_pit_costs_a_life_and_respawns(game):
    game.player.x, game.player.y = 31.0, SURFACE_Y + 1     # sobre el primer pozo
    for _ in range(300):
        game.update(DT)
        if game.phase == "play" and game.lives == 2:
            break
    assert game.lives == 2
    assert game.phase == "play"
    assert game.player.x == pytest.approx(game.respawn_x, abs=0.1)
    assert game.invincible > 0


def test_losing_all_lives_ends_the_game(game):
    game.lives = 1
    game.player.x, game.player.y = 31.0, SURFACE_Y + 1
    for _ in range(400):
        game.update(DT)
        if game.state == "over":
            break
    assert game.state == "over"
    assert game.storage.plays("mario") == 1


def test_the_level_can_be_beaten(game):
    """Un bot completa el nivel: recorre todo, llega a la meta y se muestra «Nivel completado»."""
    won = False
    for _ in range(60 * 150):                       # hasta 150 s de juego simulado
        if game.state != "playing":
            break
        drive(game)
        game.update(DT)
        if game.phase.startswith("win"):
            won = True
    assert won, f"el bot no llegó a la meta (x={game.player.x:.1f}, vidas={game.lives})"
    assert game.score >= 200
    assert game.state == "over"                     # el menú de fin se mostró tras ganar
    assert game.storage.best("mario") == game.score
