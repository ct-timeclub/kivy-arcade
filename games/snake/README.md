# Snake

**Alumno:** por asignar  ·  **Rama:** `juego/snake`  ·  **Probar solo:** `python run_game.py snake`

Una serpiente que avanza por una cuadrícula, come manzanas y crece. Pierde si choca con una pared
o con su propio cuerpo. Lee primero `games/_template/game.py` y `docs/GUIA_ALUMNO.md`.

## Hitos sugeridos (de menos a más difícil)

1. **La cuadrícula.** Decide el tamaño de celda (por ejemplo, 18 columnas) y calcula las filas con
   `self.height`. Dibuja una celda para comprobar tus coordenadas.
2. **Una serpiente de una celda que avanza.** Guarda su cuerpo como lista de `(columna, fila)`.
   No muevas cada cuadro: usa un **temporizador de pasos** (`self.acumulado += dt` y avanza cuando
   pasa, por ejemplo, 0.15 s).
3. **Dirección.** Controla con deslizamientos (`on_touch_down` guarda dónde empezó el dedo y
   `on_touch_up` calcula hacia dónde fue) o con 4 botones. La serpiente no puede girar 180°.
4. **Comida.** Una manzana en una celda aleatoria. Si la cabeza llega, `add_score()` y crece.
5. **Crecer.** Al avanzar, añade la nueva cabeza y quita la cola, salvo si comió.
6. **Perder.** Choca con la pared o contigo misma → `self.game_over()`.
7. **Dificultad.** Reduce el tiempo entre pasos conforme sube la puntuación.
8. **Pulido.** Colores distintos para cabeza y cuerpo, la manzana no aparece sobre la serpiente.

## Conceptos de Kivy que vas a usar

Listas de tuplas, `canvas` (se puede borrar y redibujar con `canvas.clear()`), temporizador acumulado
con `dt`, detección de gestos con `on_touch_down`/`on_touch_up`, `random.randint`.

## Ideas extra

Obstáculos, manzana especial que da más puntos, modo sin paredes (la serpiente reaparece por el
lado opuesto), sonido al comer (respeta `self.sound_enabled`).

## Para que encaje en la app

Cambia `PlaceholderGame` por `GameScreen` en `game.py` cuando empieces. Antes de entregar,
revisa la lista de verificación de `docs/GUIA_ALUMNO.md`.
