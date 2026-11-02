# Guía del alumno: cómo hacer tu juego para Kivy Arcade

Tu trabajo es **un juego** que se integra en la app. No tienes que tocar el menú ni los juegos de
tus compañeros: tu juego vive en **tu carpeta** dentro de `games/`.

## 1. Preparar el entorno

Sigue el README (Python 3.13 + entorno virtual + `pip install -r requirements-dev.txt`).
Comprueba que funciona:

```powershell
python main.py            # debe abrirse la app con el menú
python run_game.py snake  # debe abrirse un juego provisional
```

## 2. Crear tu rama de git

Trabajas en una **rama propia**, nunca directamente en `main`:

```powershell
git switch main
git pull
git switch -c juego/snake        # usa el nombre de tu juego
```

## 3. Tu carpeta de juego

Tu carpeta ya existe (`games/flappy`, `games/snake` o `games/mario`). Dentro tienes:

```
games/snake/
├── __init__.py   ← los DATOS del juego (título, color, autor). Aquí pones tu nombre.
├── game.py       ← el CÓDIGO de tu juego. Aquí trabajas casi todo el tiempo.
├── __main__.py   ← permite ejecutar solo tu juego (no lo toques)
├── README.md     ← hitos sugeridos para tu juego
└── assets/       ← tus imágenes y sonidos (créala si no existe)
```

Si quieres **añadir un juego extra** que no estaba previsto: copia `games/_template` a
`games/<nombre_nuevo>` (minúsculas, sin espacios). La app lo detecta sola.

### Cambia tu nombre como autor

En `games/<tu_juego>/__init__.py`, edita `author="Por asignar"`.

## 4. Probar tu juego SOLO

```powershell
python run_game.py snake
```

Se abre una ventana con **solo tu juego**, con pausa, puntuación y pantalla de fin incluidas.
Así trabajas sin depender de nadie. Al salir del juego se cierra la ventana.

Cuando quieras ver cómo queda dentro de la app completa: `python main.py` → *Jugar*.

## 5. Cómo funciona un juego

Tu clase hereda de `GameScreen`. La app y la clase base se encargan de lo común; tú rellenas los
«ganchos» (funciones que Kivy llamará en el momento justo):

```python
from arcade.game_base import GameScreen

class SnakeGame(GameScreen):

    def build_game(self, layer):      # 1 vez: crea tus widgets dentro de `layer`
        ...

    def new_game(self):               # al empezar y al reiniciar: estado inicial
        ...

    def update(self, dt):             # ~60 veces por segundo: mueve cosas
        ...
```

### Lo que puedes usar

| Herramienta | Para qué sirve |
|---|---|
| `self.layer` | Contenedor donde pones tus widgets (`self.layer.add_widget(...)`) |
| `self.width`, `self.height` | Tamaño del área de juego |
| `self.add_score(n)` | Suma puntos (por defecto 1) |
| `self.score`, `self.best` | Puntuación actual y mejor guardada |
| `self.game_over()` | Termina la partida: guarda el récord y muestra el menú de fin |
| `self.asset("bird.png")` | Ruta a un archivo de `games/<tu_juego>/assets/` |
| `self.touch_pos(touch)` | Posición del toque dentro de tu juego |
| `self.sound_enabled` | `False` si el jugador desactivó el sonido en Ajustes |
| `self.state` | `"playing"`, `"paused"`, `"over"`, `"error"` |

Ganchos opcionales: `on_game_paused()`, `on_game_resumed()`, `on_game_finished(score, new_record)`.

### Recibir toques

```python
def on_touch_down(self, touch):
    if super().on_touch_down(touch):   # ¡siempre primero! el botón de pausa o un menú lo usó
        return True
    if self.state != "playing":
        return False
    x, y = self.touch_pos(touch)
    ...                                # tu lógica
    return True
```

### Modelo para copiar

Abre **`games/_template/game.py`**: es un juego completo y pequeño («Toca el círculo»), con cada
parte comentada. Léelo antes de empezar tu juego.

## 6. Reglas para que tu juego encaje

1. **No edites `arcade/`** ni las carpetas de otros juegos. Si necesitas un cambio ahí, avisa al docente.
2. **No importes código de otros juegos.** Cada juego es independiente.
3. **Usa `dp()` y `sp()`** para tamaños (`from kivy.metrics import dp`), no píxeles fijos. Así se ve
   igual en un móvil de alta resolución que en el PC. Llama a `dp()` **dentro de funciones**, no al
   escribir la clase.
4. **Toda la lógica de movimiento usa `dt`**: `x += velocidad * dt`. Así no va más rápido o lento
   según el dispositivo.
5. **Usa el tamaño real** (`self.width`, `self.height`) en `new_game()` y `update()`, no números fijos.
6. **Evita emojis y símbolos raros en los textos**: la fuente de Kivy no los dibuja. Usa formas
   (`canvas`) o imágenes.
7. **Tus archivos van en `assets/`** y se leen con `self.asset(...)`. No uses rutas como `C:\...`.
8. **Si necesitas una librería nueva** (por ejemplo `pillow`), avisa: hay que añadirla en
   `requirements.txt` y en `buildozer.spec`, y no todas funcionan en móvil.
9. **No abras ventanas ni cambies `Window.size`** dentro de tu juego.

## 7. Lista de verificación antes de entregar

- [ ] `python run_game.py <tu_juego>` funciona y se puede jugar de principio a fin.
- [ ] El juego **termina** con `self.game_over()` y suma puntos con `add_score()`.
- [ ] Al reiniciar (`Jugar otra vez`) todo vuelve a empezar limpio (`new_game()` lo reinicia todo).
- [ ] La pausa funciona (botón `II` arriba a la izquierda).
- [ ] Probaste en **otro tamaño de ventana**: `python main.py -m screen:phone_iphone_6,portrait,scale=.6`.
- [ ] `python -m pytest` pasa (incluye pruebas automáticas de tu juego).
- [ ] `python -m ruff check .` pasa.
- [ ] Tu nombre está como `author` en `__init__.py`.
- [ ] El código tiene comentarios que explican qué hace cada parte.

## 8. Entregar con git

```powershell
git status                          # revisa qué cambiaste
git add games/snake                 # añade SOLO tu carpeta
git commit -m "Snake: movimiento y comida"
git push -u origin juego/snake      # la primera vez; después basta con `git push`
```

Luego, en GitHub, abre un **Pull Request** de tu rama hacia `main`. Las pruebas corren solas;
si fallan, haz clic en *Details* para ver el error, arréglalo y vuelve a hacer `git push`.

Haz **commits pequeños y frecuentes** (cada vez que algo nuevo funciona). Si algo se rompe, es más
fácil volver atrás.

### Mantener tu rama al día

Si el docente actualiza `main` (menú, correcciones):

```powershell
git fetch origin
git merge origin/main
```

Como tú solo tocas tu carpeta, casi nunca habrá conflictos. Si aparece uno, **no borres nada a ciegas**:
pide ayuda.

## 9. Ideas para ir más allá (opcional)

- Pantalla de inicio propia de tu juego («Toca para empezar»).
- Niveles o dificultad que sube con el tiempo.
- Imágenes propias (sprites) en lugar de formas dibujadas.
- Animaciones con `kivy.animation.Animation`.
- Sonidos con `SoundLoader` (respeta `self.sound_enabled`).
- Efectos al perder (parpadeo, sacudida).

## 10. Problemas frecuentes

| Problema | Qué hacer |
|---|---|
| Mi juego sale en rojo con «no se pudo cargar» en la lista | Hay un error al importarlo. Toca la tarjeta para ver el mensaje o corre `python run_game.py <juego>` y lee la terminal. |
| El juego muestra «El juego tuvo un error» | Un error durante la partida. La terminal muestra el detalle (`Traceback`). La app **no** se cae por esto. |
| `ModuleNotFoundError: No module named 'arcade'` | Ejecuta los comandos desde la **raíz** del repositorio (donde está `main.py`). |
| `ModuleNotFoundError: No module named 'kivy'` | No activaste el entorno virtual o usas Python 3.14. Ver README. |
| El texto se ve con cuadritos | Usaste emojis o caracteres que la fuente no tiene. |
| Los toques no responden | ¿Llamaste primero a `super().on_touch_down(touch)`? ¿Devuelves `True/False`? |
