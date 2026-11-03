"""Arte de píxeles SIN archivos de imagen: dibujas el sprite con letras y se convierte en textura.

Es una forma cómoda de tener gráficos retro sin necesidad de Photoshop ni de empaquetar PNG:

    PALETA = {"r": "#E52521", "b": "#2E5BFF"}      # cada letra es un color
    FILAS = [
        "..rr..",
        ".rrrr.",
        "rrbbrr",
        "rrbbrr",
    ]
    textura = texture_from_rows(FILAS, PALETA)
    Rectangle(texture=textura, pos=(x, y), size=(6 * 8, 4 * 8))   # 8 píxeles de pantalla por píxel

Las letras que no estén en la paleta (por ejemplo "." o " ") son transparentes.
"""

from kivy.graphics.texture import Texture
from kivy.utils import get_color_from_hex


def _to_bytes(color: str):
    """'#RRGGBB' o '#RRGGBBAA' -> (r, g, b, a) como enteros de 0 a 255."""
    r, g, b, a = get_color_from_hex(color)
    return bytes((round(r * 255), round(g * 255), round(b * 255), round(a * 255)))


def texture_from_rows(rows, palette, mirror=False, repeat=False, smooth=False):
    """Convierte una lista de cadenas (una por fila) en una textura de Kivy.

    rows     lista de cadenas del mismo largo. La primera es la fila de ARRIBA del dibujo.
    palette  diccionario {letra: "#RRGGBB"}. Lo que no esté, es transparente.
    mirror   True para invertir el dibujo de izquierda a derecha (personaje mirando al otro lado).
    repeat   True si la textura se va a repetir en mosaico (tamaño potencia de 2 recomendado).
    smooth   True para suavizar al agrandar (degradados); False para píxeles nítidos (retro).
    """
    height = len(rows)
    width = len(rows[0])
    for index, row in enumerate(rows):
        if len(row) != width:
            raise ValueError(f"La fila {index} mide {len(row)} y debería medir {width}: {row!r}")

    colors = {letter: _to_bytes(value) for letter, value in palette.items()}
    clear = bytes((0, 0, 0, 0))
    data = bytearray()
    # OpenGL empieza por la fila de ABAJO, así que recorremos al revés.
    for row in reversed(rows):
        if mirror:
            row = row[::-1]
        for letter in row:
            data += colors.get(letter, clear)

    texture = Texture.create(size=(width, height), colorfmt="rgba")
    texture.blit_buffer(bytes(data), colorfmt="rgba", bufferfmt="ubyte")
    # «nearest» mantiene los píxeles nítidos al agrandar (en vez de verse borrosos).
    mode = "linear" if smooth else "nearest"
    texture.mag_filter = mode
    texture.min_filter = mode
    if repeat:
        texture.wrap = "repeat"
    return texture
