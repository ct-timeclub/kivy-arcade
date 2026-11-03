"""El nivel de Mario 2D: un mapa de azulejos (tiles) construido con funciones sencillas.

Cada azulejo es una letra:

    .  vacío          G  pasto          D  tierra
    B  ladrillo       ?  bloque sorpresa (da una moneda)    U  bloque ya usado
    X  bloque duro    a b  parte de arriba de la tubería    c d  cuerpo de la tubería

Coordenadas: en las COLUMNAS `col` crece hacia la derecha; en las FILAS hay dos formas:
  * `row`: la fila contada desde ARRIBA (como en una lista de Python).
  * `cy`:  la altura contada desde ABAJO (como en matemáticas). La física usa `cy`.

Para cambiar el nivel solo hay que editar `build_level()` (agregar tubos, pozos, enemigos...).
"""

ROWS = 14               # alto del nivel en azulejos
GROUND_ROW = 12         # fila (desde arriba) del pasto; debajo hay una fila de tierra
SURFACE_Y = ROWS - GROUND_ROW     # altura (desde abajo) a la que se pisa el suelo = 2
SOLID = frozenset("GDB?UXabcd")   # azulejos que se pueden pisar y que bloquean el paso

PITS = [(30, 33), (53, 56), (70, 73), (90, 93)]   # pozos: columnas [inicio, fin)


class Level:
    """Datos del nivel + consultas sobre los azulejos."""

    def __init__(self, cols, tiles, enemies, coins, flag_col, start_x, checkpoint_col):
        self.cols = cols
        self.tiles = tiles                # lista de filas (cada una una lista de letras)
        self.enemies = enemies            # [(col, y)] donde aparece cada enemigo
        self.coins = coins                # [(col, cy)] celdas con una moneda
        self.flag_col = flag_col          # columna del mástil de la meta
        self.start_x = start_x            # columna donde empieza el jugador
        self.checkpoint_col = checkpoint_col

    def tile(self, col, cy):
        """Letra del azulejo en (col, cy). Los bordes izquierdo/derecho son paredes."""
        if col < 0 or col >= self.cols:
            return "X"
        row = ROWS - 1 - cy
        if row < 0 or row >= ROWS:
            return "."
        return self.tiles[row][col]

    def is_solid(self, col, cy):
        return self.tile(col, cy) in SOLID

    def set_tile(self, col, cy, letter):
        self.tiles[ROWS - 1 - cy][col] = letter


def build_level():
    """Crea un nivel NUEVO (se llama otra vez al reiniciar la partida)."""
    cols = 124
    tiles = [["."] * cols for _ in range(ROWS)]
    coins = []
    enemies = []

    def put(col, row, letter):
        if 0 <= col < cols and 0 <= row < ROWS:
            tiles[row][col] = letter

    def pipe(col, height):
        """Tubería de 2 azulejos de ancho y `height` de alto, parada sobre el suelo."""
        top = GROUND_ROW - height
        put(col, top, "a")
        put(col + 1, top, "b")
        for row in range(top + 1, GROUND_ROW):
            put(col, row, "c")
            put(col + 1, row, "d")

    def stairs(first_col, heights):
        """Escalera de bloques duros; `heights` es la altura de cada columna."""
        for offset, height in enumerate(heights):
            for step in range(height):
                put(first_col + offset, GROUND_ROW - 1 - step, "X")

    def coin_line(col_from, col_to, cy):
        for col in range(col_from, col_to + 1):
            coins.append((col, cy))

    # ---------- suelo con pozos
    for col in range(cols):
        if any(start <= col < end for start, end in PITS):
            continue
        put(col, GROUND_ROW, "G")
        put(col, GROUND_ROW + 1, "D")

    # ---------- tramo 1: calentamiento
    coin_line(8, 10, SURFACE_Y)
    pipe(15, 2)
    for col, letter in ((18, "B"), (19, "?"), (20, "B")):
        put(col, 8, letter)
    coin_line(18, 20, 6)
    enemies.append((24, SURFACE_Y))
    coin_line(26, 27, SURFACE_Y)

    # ---------- tramo 2: primer pozo y plataforma
    coins.extend([(30, 4), (31, 5), (32, 4)])
    for col in range(36, 41):
        put(col, 9, "B")
    coin_line(36, 40, 5)
    enemies.extend([(38, 5), (43, SURFACE_Y), (48, SURFACE_Y)])
    pipe(45, 3)
    coin_line(45, 46, 6)

    # ---------- tramo 3: bloques sorpresa
    coins.extend([(53, 4), (54, 5), (55, 4)])
    for col, letter in ((59, "B"), (60, "?"), (61, "B"), (62, "?"), (63, "B")):
        put(col, 8, letter)
    coin_line(59, 63, 6)
    enemies.extend([(61, SURFACE_Y), (65, SURFACE_Y)])

    # ---------- tramo 4: escaleras y salto grande
    stairs(66, [1, 2, 3, 4])
    stairs(73, [4, 3, 2, 1])
    coins.extend([(70, 7), (71, 8), (72, 7)])

    # ---------- tramo 5: enemigos y último pozo
    enemies.extend([(83, SURFACE_Y), (88, SURFACE_Y)])
    pipe(86, 2)
    coin_line(86, 87, 5)
    coin_line(82, 83, SURFACE_Y)
    coin_line(94, 95, SURFACE_Y)
    coins.extend([(90, 4), (91, 5), (92, 4)])
    for col, letter in ((96, "?"), (97, "B"), (98, "?")):
        put(col, 8, letter)
    coin_line(96, 98, 6)
    enemies.append((99, SURFACE_Y))

    # ---------- final: escalera grande y meta
    stairs(102, [1, 2, 3, 4, 5, 6, 7, 8])
    coin_line(111, 112, SURFACE_Y)
    coin_line(116, 117, SURFACE_Y)

    return Level(
        cols=cols,
        tiles=tiles,
        enemies=enemies,
        coins=coins,
        flag_col=114,
        start_x=3.0,
        checkpoint_col=58,
    )
