# Mario 2D (versión simple)

**Alumno:** por asignar  ·  **Rama:** `juego/mario`  ·  **Probar solo:** `python run_game.py mario`

Un juego de plataformas muy simplificado: el personaje corre, salta, esquiva o pisa enemigos y
llega a la meta. Es el más largo de los tres: avanza por hitos y entrega funcionando en cada uno.
Lee primero `games/_template/game.py` y `docs/GUIA_ALUMNO.md`.

## Hitos sugeridos (de menos a más difícil)

1. **Personaje y suelo.** Un rectángulo para el personaje y una plataforma de suelo (otro rectángulo).
2. **Gravedad.** `vy -= GRAVEDAD * dt`; al tocar el suelo, `vy = 0` y marca `en_suelo = True`.
3. **Controles táctiles.** Botones en pantalla: izquierda, derecha y saltar (widgets en `self.layer`).
   Solo puede saltar si está en el suelo.
4. **Plataformas.** Varios rectángulos. La colisión de «aterrizar» solo cuenta si el personaje
   **cae** y sus pies estaban por encima de la plataforma.
5. **Cámara que sigue.** Un mundo más ancho que la pantalla: desplaza todo con un `offset_x`.
6. **Monedas.** Rectángulos o círculos que, al tocarlos, hacen `add_score()` y desaparecen.
7. **Enemigos.** Patrullan de lado a lado. Tocarlos de lado → `game_over()`; pisarlos desde arriba → los eliminas.
8. **Meta y niveles.** Una bandera al final; al llegar, se suma una bonificación y empieza el siguiente nivel.

## Consejos

- **Deja un nivel simple primero.** Un solo nivel jugable vale más que mil ideas a medias.
- Separa tu código en funciones pequeñas (`_mover_jugador`, `_colisiones`, `_mover_enemigos`).
- Puedes dividir `game.py` en varios archivos dentro de tu carpeta (por ejemplo `player.py`,
  `level.py`). Impórtalos con `from .player import Player`.
- La app es vertical por ahora: diseña el nivel pensando en una pantalla estrecha.

## Conceptos de Kivy que vas a usar

`canvas`, listas de objetos, colisiones AABB (rectángulos), botones táctiles, `update(dt)`,
desplazamiento de cámara, clases propias para jugador/enemigo/moneda.

## Ideas extra

Sprites con `self.asset(...)`, animación de caminar (cambiar de imagen cada cierto tiempo),
bloques con sorpresa, vidas.

## Para que encaje en la app

Cambia `PlaceholderGame` por `GameScreen` en `game.py` cuando empieces. Antes de entregar,
revisa la lista de verificación de `docs/GUIA_ALUMNO.md`.
