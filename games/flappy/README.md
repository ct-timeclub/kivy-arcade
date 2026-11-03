# Flappy Bird (versión terminada)

`python run_game.py flappy`

Toca para aletear y pasa entre los tubos. Cada 1 punto el juego se acelera un poco y el hueco
se cierra, hasta un límite.

## Archivos

| Archivo | Qué contiene |
|---|---|
| `game.py` | Toda la lógica: fases, física, tubos, colisiones, dibujo del pájaro |
| `art.py` | Texturas generadas por código: tubos, suelo y ciudad lejana |
| `__init__.py` | Los datos del juego (`GAME`) |

## Cómo funciona

- **Tres fases propias**: `ready` (el pájaro flota esperando el primer toque), `play` y `dead`
  (cae girando y, al llegar al suelo, se llama a `game_over()`).
- **Unidades relativas**: todas las medidas están en «unidades» (`u = alto / 640`), así el juego es
  igual en pantallas distintas.
- **Física**: `vy -= GRAVITY * dt` y `y += vy * dt`; aletear fija `vy` hacia arriba.
- **Tubos**: 4 pares que se reciclan al salir por la izquierda. La altura del hueco cambia como
  máximo ±190 unidades respecto al anterior para que nunca sea imposible.
- **Parallax**: el suelo y la ciudad son texturas que se repiten; moverlas es cambiar `tex_coords`.
- **Pájaro**: elipses dentro de un `Translate` + `Rotate` + `Scale`; se inclina según su velocidad.

## Retos para mejorarlo

1. Añade **medallas** (bronce a los 10, plata a los 20, oro a los 30) en la pantalla de fin.
2. Cambia de día a noche cada 10 puntos (otro degradado en `vertical_gradient`).
3. Haz que aparezcan **monedas** en el hueco de algunos tubos.
4. Prueba tubos que **se mueven** arriba y abajo después de 15 puntos.
5. Cambia las constantes (`GRAVITY`, `FLAP_SPEED`, `GAP_START`) y observa cómo cambia la sensación.
