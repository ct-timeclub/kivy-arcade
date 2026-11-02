# Guía del docente

## Visión general del proyecto

1. **En clase:** el docente construye (o presenta) la app principal: menú, ajustes y puntuaciones.
   Ya está en este repositorio.
2. **Cada alumno** recibe acceso al repositorio y trabaja **su juego** en una rama propia.
3. **Integración:** cada juego entra a `main` mediante un *Pull Request* revisado por el docente.
   Las pruebas automáticas corren solas en cada push.
4. **Entrega:** se generan el APK (Android) y el IPA (iOS) con GitHub Actions.

## Preparar el repositorio de la clase

### Añadir a los alumnos como colaboradores

1. En GitHub, entra al repositorio → **Settings** → **Collaborators** → **Add people**.
2. Escribe el usuario de GitHub de cada alumno (necesitan una cuenta gratuita).
3. Cada alumno recibe una invitación por correo y debe aceptarla.

Con **permiso de escritura** los alumnos pueden crear ramas y abrir Pull Requests en el mismo
repositorio (no necesitan hacer *fork*).

### Convenciones de ramas

| Rama | Uso |
|---|---|
| `main` | Siempre funcional. Solo se mezcla con Pull Requests revisados. |
| `juego/flappy`, `juego/snake`, `juego/mario` | Una por alumno. |
| `docente/...` | Cambios del menú o de la infraestructura. |

### Proteger `main` (recomendado)

En **Settings → Branches** (o **Rules → Rulesets**) se puede exigir un Pull Request y que las
pruebas pasen antes de mezclar. La disponibilidad de estas reglas depende del plan de GitHub y de
si el repositorio es público o privado; si no están disponibles, el acuerdo de clase es: **nadie
sube directo a `main`**.

## Por qué los alumnos casi no tendrán conflictos

Cada alumno edita **solo su carpeta** `games/<su_juego>/`. La app encuentra los juegos
automáticamente, así que **nadie edita una lista compartida**. Los archivos que sí son compartidos
(`arcade/`, `requirements.txt`, `buildozer.spec`) los modifica solo el docente.

Si un alumno necesita una librería nueva, la añade el docente en `requirements.txt` y en
`buildozer.spec`, y se comprueba que funcione en Android e iOS antes de aceptarla.

## Revisar un Pull Request

Lista sugerida:

- [ ] Las pruebas de GitHub Actions pasan (marca verde).
- [ ] Solo cambia archivos dentro de `games/<su_juego>/` (en la pestaña *Files changed*).
- [ ] `author` está con el nombre del alumno.
- [ ] Probar la rama: `git fetch`, `git switch juego/snake`, `python main.py`.
- [ ] El juego termina, reinicia y pausa bien.
- [ ] El código está comentado y se entiende.

Después: **Merge** (se recomienda *Squash and merge* para dejar un historial limpio).

## Qué se ejecuta en GitHub Actions

| Workflow | Cuándo | Qué hace | Duración |
|---|---|---|---|
| **Pruebas** (`ci.yml`) | Cada push y Pull Request | Estilo (`ruff`) y pruebas (`pytest`) con Python 3.11 y 3.13 | 1-3 min |
| **Build Android** (`android.yml`) | Push a `main` y manual | Genera el APK de depuración | 25-40 min la 1.ª vez |
| **Build iOS** (`ios.yml`) | **Solo manual** o con etiqueta `v*` | Genera app de simulador e IPA sin firmar | 40-90 min la 1.ª vez |

### Coste de los minutos de Actions

En un repositorio **privado** con cuenta gratuita hay una cuota mensual de minutos, y **los de macOS
cuentan x10**. Por eso el build de iOS no corre solo en cada push. En un repositorio **público**
los minutos son gratuitos. Revisa la cuota actual en la documentación de facturación de GitHub.

Para ejecutar un build a mano: pestaña **Actions** → elige el workflow → **Run workflow**.
El resultado aparece abajo, en **Artifacts**, al terminar.

## Ritmo sugerido del proyecto

| Sesión | Qué se hace |
|---|---|
| 1 | Presentar la app y el contrato de `GameScreen`. Leer y ejecutar `_template`. |
| 2 | Cada alumno crea su rama y logra el primer hito de su juego (ver el README de su carpeta). |
| 3-5 | Desarrollo con revisión de código (Pull Requests pequeños). |
| 6 | Integración: todos los juegos en `main`; probar la app completa. |
| 7 | Build de Android (y de iOS si se dispone de Mac); demo en clase. |

## Si algo sale mal

- **Un juego rompe la app:** no debería (se aísla), pero si pasa, revisa los logs y la prueba
  `tests/test_games.py`; es la que debe atrapar el caso.
- **Conflicto de merge:** casi siempre es porque alguien tocó un archivo compartido. Resuélvelo
  tú y pide que no lo vuelvan a editar.
- **Falla el build de Android:** abre el job en *Actions* y lee el final del log del paso
  «Compilar APK». Si es un tema de dependencias, revisa `requirements` en `buildozer.spec`.
