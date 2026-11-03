"""Arte de píxeles de Mario 2D, dibujado con letras (sin archivos de imagen).

Cada dibujo es una lista de cadenas: una letra = un píxel. La paleta dice qué color es cada
letra (ver arcade/pixelart.py). Puedes cambiar los dibujos y se actualizan solos.
Los azulejos (tiles) miden 16x16 píxeles; el personaje 12x16.
"""

from arcade.pixelart import texture_from_rows

# ====================================================================== personaje
PLAYER_PALETTE = {
    "R": "#E52521", "r": "#A8141A",     # rojo (gorra, camiseta) y su sombra
    "S": "#FFC08A", "s": "#D9915C",     # piel y su sombra
    "H": "#5A2D0C",                     # pelo / bigote
    "B": "#2F5DFF", "b": "#1E3CA8",     # overol azul y su sombra
    "Y": "#FFE14D",                     # botones
    "K": "#1A1A1A",                     # ojo
    "O": "#6B3A12",                     # zapatos
}

# Parte de arriba (cabeza y torso): igual en todos los cuadros menos al saltar.
_UPPER = [
    "....RRRRR...",
    "...RRRRRRRR.",
    "...HHHSSSSS.",
    "..HSHSSSKSSS",
    "..HSHHSSKSSS",
    "..HHSSSSHHHS",
    "....SSSSSSSs",
    "...RRRRRRR..",
    "..RRBRRRBRR.",
    ".RRRBBYBBBRR",
]

# Los últimos 6 renglones cambian en cada cuadro: manos, piernas y zapatos.
_LOWER = {
    "idle": [
        ".SSRBBBBBRSS",
        ".SSSBBBBBSSS",
        "..SBBBBBBBS.",
        "...BBB.BBB..",
        "..OOOO.OOOO.",
        ".OOOOO.OOOOO",
    ],
    "run1": [
        ".SSRBBBBBRSS",
        "..SSBBBBBBS.",
        "...BBBBBBB..",
        "..BBBB..BBB.",
        ".OOO.....OOO",
        ".OOO......OO",
    ],
    "run2": [
        "..SRBBBBBRS.",
        "..SBBBBBBBS.",
        "...BBBBBB...",
        "....BBBBB...",
        "...OOOOOO...",
        "...OOOOOO...",
    ],
    "jump": [
        "SSSRBBBBBRSS",
        "SSSBBBBBBBS.",
        "...BBBBBBB..",
        "..BBB..BBBB.",
        ".OOOO...OOOO",
        ".OOO.....OOO",
    ],
}


def _player_rows(name):
    rows = _UPPER + _LOWER[name]
    return rows


# ====================================================================== enemigo
ENEMY_PALETTE = {
    "b": "#8B4A1F", "d": "#5C2E10", "w": "#FFFFFF", "k": "#1A1A1A",
    "s": "#F3CF9A", "t": "#D6A96A", "f": "#3A1D0A",
}

ENEMY_A = [
    "....dddddd....",
    "..dbbbbbbbbd..",
    ".dbbbbbbbbbbd.",
    "dbbbbbbbbbbbbd",
    "dbbwwwbbwwwbbd",
    "dbbwkkbbkkwbbd",
    "dbbbbbbbbbbbbd",
    ".dbbbbbbbbbbd.",
    "..ssssssssss..",
    "..sttssssstt..",
    "..ssssssssss..",
    ".fffff..fffff.",
    "ffffff..ffffff",
    "fffff....fffff",
]
ENEMY_B = ENEMY_A[:11] + [
    "..fffff.fffff.",
    "..ffffff.ffff.",
    "...fff....fff.",
]
ENEMY_SQUASHED = [
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..............",
    "..dbbbbbbbbd..",
    ".dbbwwbbwwbbd.",
    "dbbbkkbbkkbbbd",
    ".dssssssssssd.",
    "..ffffffffff..",
    "..............",
]


# ====================================================================== azulejos 16x16
TILE_PALETTE = {
    # pasto y tierra
    "g": "#5DD13C", "G": "#3FA02B", "h": "#8BE864",
    "d": "#C8863E", "D": "#9B5F26", "e": "#E2A458",
    # ladrillo
    "m": "#5E2A0E", "b": "#D9722B", "l": "#F29C52", "n": "#B25A1E",
    # bloque de pregunta
    "o": "#7A3B00", "y": "#F9A61A", "p": "#FFD35C", "q": "#7A3B00", "z": "#C77212",
    # bloque duro / usado
    "k": "#3B2A1A", "x": "#B88A55", "X": "#D8B27A", "Z": "#8A6238",
    # tubería
    "P": "#2A5E1E", "Q": "#C5F27A", "U": "#9BE04C", "V": "#6BBF2A", "W": "#4E9A20",
    "T": "#3C7A18",
}

GRASS = (
    ["hhhhhhhhhhhhhhhh"]
    + ["gggggggggggggggg"] * 2
    + ["GGGgGGGGgGGGGgGG",
       "dGdddGdddddGddGd"]
    + [
        "dddddddddddddddd",
        "ddeddddddDddddeD",
        "dddddDdddddddddd",
        "ddddddddedddddDd",
        "dDddddddddddeddd",
        "dddddedddDddddDd",
        "dddddddddddddddd",
        "deddDddddddedddd",
        "dddddddddeddDddd",
        "dDdddddedddddddd",
        "dddddddddddddedd",
    ]
)
DIRT = [
    "dddddddddddddddd",
    "ddeddddddDddddeD",
    "dddddDdddddddddd",
    "ddddddddedddddDd",
    "dDddddddddddeddd",
    "dddddedddDddddDd",
    "dddddddddddddddd",
    "deddDddddddedddd",
    "dddddddddeddDddd",
    "dDdddddedddddddd",
    "dddddddddddddedd",
    "ddeddddddDddddeD",
    "dddddDdddddddddd",
    "ddddddddedddddDd",
    "dDddddddddddeddd",
    "dddddddddddddddd",
]

_BRICK_A = "lbbbbbbmlbbbbbbm"
_BRICK_B = "bbbmlbbbbbbmlbbb"
BRICK = (
    ["mmmmmmmmmmmmmmmm"] + [_BRICK_A] * 3
    + ["mmmmmmmmmmmmmmmm"] + [_BRICK_B] * 3
    + ["mmmmmmmmmmmmmmmm"] + [_BRICK_A] * 3
    + ["mmmmmmmmmmmmmmmm"] + [_BRICK_B] * 3
)

_QUESTION_BASE = (
    ["oooooooooooooooo"]
    + ["opppppppppppppzo"]
    + ["opyyyyyyyyyyyyzo"] * 12
    + ["ozzzzzzzzzzzzzzo"]
    + ["oooooooooooooooo"]
)
_QUESTION_MARK = {
    3: ".....qqqqqq.....",
    4: "....qq....qq....",
    5: "....qq....qq....",
    6: "..........qq....",
    7: ".........qq.....",
    8: "........qq......",
    9: "........qq......",
    11: "........qq......",
    12: "........qq......",
}


def _question_rows():
    rows = []
    for index, base in enumerate(_QUESTION_BASE):
        overlay = _QUESTION_MARK.get(index)
        if overlay:
            base = "".join(o if o != "." else b for o, b in zip(overlay, base))
        rows.append(base)
    # remaches en las cuatro esquinas
    for r, c in ((1, 1), (1, 14), (14, 1), (14, 14)):
        row = list(rows[r])
        row[c] = "q"
        rows[r] = "".join(row)
    return rows


QUESTION = _question_rows()

USED = (
    ["kkkkkkkkkkkkkkkk"]
    + ["kXXXXXXXXXXXXXZk"]
    + ["kXxxxxxxxxxxxxZk"] * 12
    + ["kZZZZZZZZZZZZZZk"]
    + ["kkkkkkkkkkkkkkkk"]
)
HARD = (
    ["kkkkkkkkkkkkkkkk"]
    + ["kXXXXXXXXXXXXXZk"]
    + ["kXxxxxxxxxxxxxZk"] * 12
    + ["kZZZZZZZZZZZZZZk"]
    + ["kkkkkkkkkkkkkkkk"]
)
# Las esquinas del bloque duro llevan remaches, como los de un bloque de escalera.
HARD = [
    "kkkkkkkkkkkkkkkk",
    "kXXXXXXXXXXXXXZk",
    "kXkxxxxxxxxxxkZk",
    *["kXxxxxxxxxxxxxZk"] * 11,
    "kXkxxxxxxxxxxkZk",
    "kZZZZZZZZZZZZZZk",
    "kkkkkkkkkkkkkkkk",
]


def _pipe_rows():
    """Tubería de 2x2 azulejos (32x32 píxeles), partida en 4 trozos de 16x16."""
    edge = "P" * 32
    cap_middle = "P" + "Q" * 4 + "U" * 8 + "V" * 10 + "W" * 6 + "T" * 3 + "P"
    cap_middle = cap_middle[:32]
    cap = [edge] + [cap_middle] * 14 + [edge]
    body_core = "P" + "Q" * 3 + "U" * 7 + "V" * 8 + "W" * 6 + "T" * 2 + "P"
    body_core = body_core[:28]
    body_row = ".." + body_core + ".."
    body = [body_row] * 16
    return cap, body


def _split(rows, col):
    return [row[col:col + 16] for row in rows]


# ====================================================================== monedas
COIN_PALETTE = {"o": "#B86B00", "y": "#FFD21F", "h": "#FFF2A0", "d": "#E8A800"}


def _coin_rows(width):
    """Moneda de 10x14 con `width` píxeles de ancho (para animar que gira)."""
    rows = []
    for y in range(14):
        # contorno elíptico
        dy = (y - 6.5) / 7.0
        half = int(round(width / 2 * (1 - dy * dy) ** 0.5 + 0.0001))
        row = ["."] * 10
        left = 5 - half
        for x in range(left, left + half * 2):
            if 0 <= x < 10:
                edge = x in (left, left + half * 2 - 1) or y in (0, 13)
                row[x] = "o" if edge else "y"
        if width >= 6:                       # brillo
            for x in range(left + 1, left + 3):
                if 0 <= x < 10 and 2 <= y <= 8 and row[x] == "y":
                    row[x] = "h"
        rows.append("".join(row))
    return rows


def _coin_bar(width):
    """Moneda de canto (muy delgada)."""
    rows = []
    for y in range(14):
        row = ["."] * 10
        if 1 <= y <= 12:
            row[4] = "o"
            row[5] = "y" if 2 <= y <= 11 else "o"
        rows.append("".join(row))
    return rows


def build_textures():
    """Crea todas las texturas una sola vez. Devuelve un diccionario {nombre: Textura}."""
    t = {}
    for name in _LOWER:
        rows = _player_rows(name)
        t[f"player_{name}_r"] = texture_from_rows(rows, PLAYER_PALETTE)
        t[f"player_{name}_l"] = texture_from_rows(rows, PLAYER_PALETTE, mirror=True)
    for name, rows in (("a", ENEMY_A), ("b", ENEMY_B), ("squashed", ENEMY_SQUASHED)):
        t[f"enemy_{name}"] = texture_from_rows(rows, ENEMY_PALETTE)
    t["grass"] = texture_from_rows(GRASS, TILE_PALETTE)
    t["dirt"] = texture_from_rows(DIRT, TILE_PALETTE)
    t["brick"] = texture_from_rows(BRICK, TILE_PALETTE)
    t["question"] = texture_from_rows(QUESTION, TILE_PALETTE)
    t["used"] = texture_from_rows(USED, TILE_PALETTE)
    t["hard"] = texture_from_rows(HARD, TILE_PALETTE)
    cap, body = _pipe_rows()
    t["pipe_tl"] = texture_from_rows(_split(cap, 0), TILE_PALETTE)
    t["pipe_tr"] = texture_from_rows(_split(cap, 16), TILE_PALETTE)
    t["pipe_bl"] = texture_from_rows(_split(body, 0), TILE_PALETTE)
    t["pipe_br"] = texture_from_rows(_split(body, 16), TILE_PALETTE)
    t["coin_0"] = texture_from_rows(_coin_rows(8), COIN_PALETTE)
    t["coin_1"] = texture_from_rows(_coin_rows(5), COIN_PALETTE)
    t["coin_2"] = texture_from_rows(_coin_bar(2), COIN_PALETTE)
    return t
