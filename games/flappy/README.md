# Flappy Bird

**Alumno:** por asignar  ·  **Rama:** `juego/flappy`  ·  **Probar solo:** `python run_game.py flappy`

Un pájaro que cae por gravedad; cada toque lo hace saltar. Hay que pasar entre tubos.
Lee primero `games/_template/game.py` y `docs/GUIA_ALUMNO.md`.

## Hitos sugeridos (de menos a más difícil)

1. **El pájaro cae.** Dibuja un cuadrado o círculo (canvas) y súbele la velocidad vertical con la
   gravedad en `update(dt)`: `vy -= GRAVEDAD * dt` y `y += vy * dt`.
2. **Salta al tocar.** En `on_touch_down`, pon `vy` en un valor positivo (impulso).
3. **Pierde al tocar el suelo o el techo** → `self.game_over()`.
4. **Un tubo que se mueve.** Dos rectángulos (arriba y abajo) con un hueco, que avanzan hacia la
   izquierda `x -= velocidad * dt`.
5. **Colisión.** Comprueba si el rectángulo del pájaro se solapa con los de los tubos.
6. **Puntuación.** Suma `self.add_score()` cuando el pájaro pasa un tubo.
7. **Varios tubos.** Crea tubos nuevos a cierta distancia y elimina los que salen de la pantalla.
8. **Dificultad.** Hueco más pequeño o tubos más rápidos conforme sube el puntaje.

## Conceptos de Kivy que vas a usar

`canvas` (`Color`, `Rectangle`, `Ellipse`), `update(dt)`, `on_touch_down`, colisiones entre
rectángulos, listas de objetos, `random`.

## Ideas extra

Imagen del pájaro con `self.asset("bird.png")`, animación de aleteo, fondo con parallax,
medallas por puntaje.

## Para que encaje en la app

Cambia `PlaceholderGame` por `GameScreen` en `game.py` cuando empieces. Antes de entregar,
revisa la lista de verificación de `docs/GUIA_ALUMNO.md`.
