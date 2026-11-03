# La demo: juegos terminados

El repositorio tiene **dos versiones del mismo proyecto**, en dos ramas:

| Rama | Contenido | Para qué sirve |
|---|---|---|
| `main` | La app con menús y **juegos vacíos** (pantallas provisionales con botones de prueba) | Punto de partida de los alumnos: cada uno programa su juego |
| `demo/completa` | La misma app con **Flappy Bird, Snake y Mario 2D terminados** | Mostrar el resultado final y tener una solución de referencia |

Los alumnos **no deberían ver esta rama** hasta que terminen (si ven la solución, pierden el
ejercicio). Mientras tanto, puedes mantener el repositorio privado y no compartir la rama, o
trabajar con una copia aparte.

## Cambiar de versión

```powershell
git switch main              # esqueletos para los alumnos
git switch demo/completa     # juegos terminados
```

## Qué diferencia hay entre las ramas

La demo añade **código nuevo**, no modifica el diseño de la app:

| Archivo | Qué es |
|---|---|
| `games/flappy/`, `games/snake/`, `games/mario/` | Los tres juegos completos |
| `arcade/gfx.py` | Degradados y partículas (herramientas comunes) |
| `arcade/pixelart.py` | Convierte dibujos hechos con letras en texturas |
| `arcade/sound.py` | Efectos de sonido sintetizados |
| `arcade/game_base.py` | `play_sound()`, `vibrate()` y `hud_score` añadidos a `GameScreen` |
| `tests/test_flappy.py`, `test_snake.py`, `test_mario.py` | Pruebas, con bots que juegan |
| `buildozer.spec` | Permiso `VIBRATE` |

Las herramientas nuevas de `arcade/` (`gfx`, `pixelart`, `sound`) son **opcionales** y pueden
llevarse también a `main` si quieres que los alumnos las usen:

```powershell
git switch main
git checkout demo/completa -- arcade/gfx.py arcade/pixelart.py arcade/sound.py
```

(Y las dos pequeñas adiciones de `arcade/game_base.py`.)

## Controles

| | Android / iOS | PC |
|---|---|---|
| **Flappy Bird** | Tocar la pantalla | Espacio o flecha arriba |
| **Snake** | Deslizar el dedo | Flechas o WASD |
| **Mario 2D** | Botones ‹ › y ▲ en pantalla (se pueden usar varios dedos a la vez) | Flechas o A/D para moverse, espacio o W para saltar |
| **Todos** | Botón `II` = pausa. Botón «atrás» del teléfono = pausa / volver | Esc |

## Cómo se hizo: técnicas que muestra cada juego

Sirve de guía para explicar en clase cada concepto con un ejemplo real:

| Concepto | Dónde verlo |
|---|---|
| Bucle de juego con `dt` | `update(dt)` en los tres juegos |
| Gravedad e impulso | `FlappyGame._update_play`, `MarioGame._player_step` |
| Colisión círculo-rectángulo | `_circle_hits_rect` en `flappy/game.py` |
| Colisión con un mapa de azulejos (AABB) | `_move_x` y `_move_y` en `mario/game.py` |
| Subpasos de física (evitar atravesar el suelo) | `MarioGame.update` |
| Parallax con texturas en mosaico | `FlappyGame._scroll` |
| Movimiento en cuadrícula con dibujo suave (interpolación) | `SnakeGame._draw_snake` |
| Cola de giros / gestos de deslizamiento | `SnakeGame.on_touch_move`, `turn()` |
| Multitáctil (varios dedos) | `MarioGame.on_touch_down/move/up` |
| Arte de píxeles con letras | `mario/sprites.py`, `arcade/pixelart.py` |
| Cámara que sigue al jugador | `MarioGame._camera_target`, `cam_tr` |
| Dibujar solo lo visible | `MarioGame._draw_visible_columns` |
| Máquina de estados (jugando / muriendo / ganando) | `MarioGame.phase` |
| Partículas reutilizables (sin crear objetos) | `arcade/gfx.py` |
| Sonido sintetizado | `arcade/sound.py` |
| Pruebas con un bot que juega | `tests/test_mario.py` (`drive`) |

## Créditos y uso

- Todos los gráficos y sonidos se **generan por código** y son originales del proyecto.
- Mario 2D está **inspirado** en los juegos de plataformas clásicos; el personaje y el enemigo son
  dibujos propios hechos para esta demo. Es un proyecto **educativo** y no debe distribuirse
  comercialmente.
