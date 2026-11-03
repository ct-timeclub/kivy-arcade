# Mario 2D (versión terminada)

`python run_game.py mario`

Juego de plataformas: corre, salta, junta monedas, golpea bloques, pisa enemigos y llega a la
bandera. Tienes 3 vidas y un punto de control a mitad del nivel.

**Puntos:** moneda 10 · enemigo pisado 25 · llegar a la meta 200 + 50 por cada vida que te sobre.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `game.py` | Física, controles, enemigos, cámara y dibujo |
| `level.py` | El mapa del nivel, construido con funciones (`pipe`, `stairs`, `coin_line`) |
| `sprites.py` | El arte de píxeles: personaje (4 poses), enemigo, azulejos y monedas |
| `__init__.py` | Los datos del juego (`GAME`) |

## Cómo funciona

- **Mapa de azulejos**: cada letra de `level.py` es un azulejo (`G` pasto, `B` ladrillo, `?` bloque
  sorpresa...). `Level.is_solid(col, cy)` responde si se puede pisar.
- **Colisiones en dos pasos**: primero se mueve en X y se corrige; después en Y. Así se sabe si
  chocó de lado, con la cabeza (golpea el bloque) o con los pies (aterriza).
- **Subpasos de 1/120 s**: la física se divide en pasos pequeños para que, al caer rápido, nada
  atraviese el suelo.
- **Sensación de salto**: altura variable (soltar el botón corta el salto), *coyote time* (se puede
  saltar un instante después de dejar el borde) y *jump buffer* (se recuerda un toque adelantado).
- **Cámara**: sigue al jugador con suavizado; el mundo se mueve con un `Translate`.
- **Solo lo visible**: los azulejos están agrupados por columna y solo se dibujan las que caben en
  pantalla.
- **Arte de píxeles**: cada sprite es una lista de cadenas; ver `arcade/pixelart.py`.
- **Estados**: `phase` es `play`, `dying`, `win_slide`, `win_walk` o `win_done`.
- **Controles táctiles**: botones dibujados en el canvas; se siguen varios dedos a la vez con
  `touch.uid` (puedes correr y saltar a la vez).

## Cambiar el nivel

Abre `level.py` y edita `build_level()`: agrega `pipe(col, alto)`, `stairs(col, [alturas])`,
`coin_line(desde, hasta, altura)` o `enemies.append((col, altura))`. Después ejecuta
`python -m pytest tests/test_mario.py`: la prueba `test_the_level_can_be_beaten` pone un bot a
jugar y avisa si el nivel se volvió **imposible**.

## Retos para mejorarlo

1. Un **hongo** en los bloques sorpresa que haga crecer al personaje.
2. Un **segundo tipo de enemigo** (uno con caparazón o que vuela).
3. Un **cronómetro** de 200 segundos con bonus por el tiempo que sobre.
4. Un segundo **nivel** (crea `build_level_2()` y pasa al siguiente al llegar a la meta).
5. **Moneda de 100** que da una vida extra.
