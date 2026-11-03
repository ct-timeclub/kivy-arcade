"""Gráficos de Flappy Bird generados por código (sin archivos de imagen).

Cada función devuelve una textura lista para usar en un Rectangle.
"""

import random

from arcade.pixelart import texture_from_rows

# ---------------------------------------------------------------- tubos
_PIPE = {
    "o": "#2A5E1E",   # contorno
    "l": "#C5F27A",   # brillo
    "L": "#9BE04C",
    "g": "#6BBF2A",   # verde principal
    "G": "#4E9A20",
    "d": "#3C7A18",   # sombra
}


def pipe_body_texture():
    """Franja de 16x1 píxeles: estirada hacia arriba/abajo forma el cuerpo del tubo."""
    return texture_from_rows(["olLLLgggggGGGddo"], _PIPE, smooth=True)


def pipe_cap_texture():
    """Boca del tubo (18x8) con borde oscuro arriba y abajo."""
    edge = "o" * 18
    middle = "olLLLLggggggGGGGdo"
    return texture_from_rows([edge] + [middle] * 6 + [edge], _PIPE, smooth=True)


# ---------------------------------------------------------------- suelo
def ground_texture():
    """Suelo de 64x32: pasto arriba y arena con rayas diagonales (se repite en mosaico)."""
    palette = {
        "o": "#3A8A2B", "g": "#7ED957", "h": "#A8EE74",
        "s": "#E8D9A0", "t": "#D6C27C", "b": "#B8A25E",
    }
    rows = []
    for y in range(32):
        row = []
        for x in range(64):
            if y == 0:
                row.append("o")
            elif y == 1:
                row.append("h")
            elif y < 5:
                row.append("g")
            elif y == 5:
                row.append("o")
            elif y == 6:
                row.append("b")
            else:
                # Rayas diagonales: el periodo (16) divide a 64, así el mosaico encaja.
                row.append("t" if (x + y) % 16 < 5 else "s")
        rows.append("".join(row))
    return texture_from_rows(rows, palette, repeat=True)


# ---------------------------------------------------------------- ciudad lejana
def skyline_texture(seed=7):
    """Siluetas de edificios lejanos (256x64), pensadas para repetirse sin cortes."""
    rng = random.Random(seed)
    width, height = 256, 64
    grid = [["."] * width for _ in range(height)]
    x = 0
    shade = 0
    while x < width:
        w = min(rng.randint(14, 30), width - x)
        if width - x - w < 12:      # no dejar un hueco pequeño al final
            w = width - x
        h = rng.randint(14, 46)
        letter = "ab"[shade % 2]
        shade += 1
        for yy in range(h):
            row = height - 1 - yy
            for xx in range(x, x + w):
                grid[row][xx] = letter
        # ventanitas claras
        for wy in range(4, h - 3, 7):
            for wx in range(x + 3, x + w - 3, 6):
                grid[height - 1 - wy][wx] = "w"
        x += w
    rows = ["".join(r) for r in grid]
    palette = {"a": "#A9DDF3", "b": "#97D1EC", "w": "#C9EBFA"}
    return texture_from_rows(rows, palette, repeat=True)
