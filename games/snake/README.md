# Snake (versión terminada)

`python run_game.py snake`

Desliza el dedo para girar y come manzanas. Cada 5 manzanas aparece una **dorada** que da 5 puntos
y dura 6.5 segundos (un anillo muestra el tiempo que queda). Cada manzana acelera un poco el juego.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `game.py` | Toda la lógica y el dibujo |
| `__init__.py` | Los datos del juego (`GAME`) |

## Cómo funciona

- **Lógica en cuadrícula, dibujo suave**: la serpiente avanza una celda cada `interval` segundos
  (`_step`), pero entre un paso y otro la cabeza y la cola se **interpolan** (`_draw_snake`) y el
  cuerpo se dibuja como una línea gruesa redondeada.
- **Tablero**: una textura de damero de 2×2 píxeles que se repite (`tex_coords`); todo el tablero
  es **un solo rectángulo**.
- **Giros**: `turn()` ignora repetir la dirección y dar media vuelta, y guarda hasta 2 giros en
  una cola para no perder deslizamientos rápidos.
- **Deslizar**: `on_touch_down` guarda dónde empezó el dedo; `on_touch_move` decide el giro según
  el eje con más movimiento y vuelve a empezar desde ahí (permite encadenar giros sin levantar el dedo).
- **Choques**: contra la pared o contra el cuerpo. La celda de la cola cuenta como libre si se va
  a mover en ese mismo paso (como en el Snake clásico).

## Retos para mejorarlo

1. Añade **obstáculos** (rocas) en celdas fijas del tablero.
2. Un modo **sin paredes**: al salir por un lado, reaparece por el opuesto.
3. Una **manzana venenosa** que reduce el tamaño de la serpiente.
4. Cambia la velocidad: modifica `START_INTERVAL`, `MIN_INTERVAL` y cuánto baja por manzana.
5. Dibuja un **patrón** en el cuerpo (rayas) cambiando el color por segmento.
