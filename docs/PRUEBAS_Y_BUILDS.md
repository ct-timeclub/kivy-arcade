# Probar y compilar: PC, Android e iOS

## Respuesta corta: ¿puedo probarlo directo en mi PC?

| Plataforma | ¿En un PC con Windows? | Cómo |
|---|---|---|
| **App en el PC (escritorio)** | ✅ Sí, directo | `python main.py` |
| **Un solo juego** | ✅ Sí, directo | `python run_game.py snake` |
| **Simular pantalla de teléfono** | ✅ Sí | `python main.py -m screen:phone_iphone_6,portrait,scale=.6` |
| **Android** | ✅ Sí, con el emulador de Android Studio o un teléfono por USB | Instalar el APK (ver abajo) |
| **iOS** | ❌ **No** en Windows | Necesita un Mac con Xcode (ver abajo) |

**La clave:** casi todo el desarrollo (≈95 %) se hace y se prueba en el PC con `main.py` y
`run_game.py`, porque el código de Kivy es el mismo en todas las plataformas. El APK y el IPA se
generan al final para comprobar cómo se comporta en un dispositivo real.

---

## 1. Probar en el PC (el día a día)

```powershell
python main.py                 # la app completa, con ventana de teléfono
python run_game.py snake       # solo un juego (lo que usan los alumnos)
python -m games.snake          # equivalente
```

Simular otros tamaños y densidades de pantalla:

```powershell
python main.py -m screen                                  # lista de dispositivos
python main.py -m screen:phone_iphone_6,portrait,scale=.6
python main.py -m screen:phone_nexus_5,portrait,scale=.4
```

Esto cambia tamaño y densidad de la ventana para comprobar que el diseño aguanta. **No emula el
sistema operativo**: no prueba permisos, rendimiento real ni el comportamiento táctil del móvil.

---

## 2. Android

### Opción A: compilar con GitHub Actions (recomendada, no instalas nada)

1. Sube a `main` (o ve a **Actions → Build Android (APK) → Run workflow**).
2. Espera a que termine (25-40 min la primera vez).
3. Entra a la ejecución y descarga **kivy-arcade-apk** desde *Artifacts* (es un `.zip` con el `.apk`).

### Opción B: compilar en tu propio PC

`buildozer` **no funciona en Windows nativo**. Se puede dentro de **WSL2 (Ubuntu)** o con **Docker**:

```bash
# Con Docker (desde la raíz del repositorio):
docker run --rm -it --volume "$PWD":/home/user/hostcwd ghcr.io/kivy/buildozer:latest android debug
```

El APK queda en `bin/`. En WSL2 se siguen los mismos pasos del workflow `android.yml`.

### Instalar y probar el APK

**En un teléfono Android:**
1. Activa *Opciones de desarrollador* y *Depuración USB* en el teléfono.
2. Conéctalo por USB y ejecuta `adb install bin\kivyarcade-0.1.0-...-debug.apk`
   (`adb` viene con Android Studio / *platform-tools*).
   También puedes pasar el APK al teléfono y abrirlo (habrá que permitir «instalar apps de origen desconocido»).

**En el emulador de Android Studio:**
1. Instala Android Studio → *Device Manager* → crea un dispositivo virtual.
2. Elige una imagen **x86_64** (la mayoría de PC son Intel/AMD). Por eso `buildozer.spec` compila
   `arm64-v8a` **y** `x86_64`.
3. Arrastra el APK a la ventana del emulador, o `adb install <archivo>.apk`.

Para ver los mensajes de la app mientras corre: `adb logcat -s python`.

---

## 3. iOS

### Lo que NO se puede hacer en Windows

- **Ejecutar o simular iOS en un PC con Windows no es posible.** El Simulador de iOS y las
  herramientas para compilar (`Xcode`) solo existen en macOS.
- **Instalar en un iPhone real exige firmar la app** con un certificado de Apple.

### Lo que sí se puede

**Compilar en GitHub Actions** (un Mac en la nube) sin tener Mac:
**Actions → Build iOS (sin firmar) → Run workflow**. Genera:

| Archivo | Para qué sirve |
|---|---|
| `Kivy-Arcade-simulator.zip` | Una app para el **Simulador de iOS**. Hace falta un Mac con Xcode para ejecutarla. |
| `Kivy-Arcade-unsigned.ipa` | IPA **sin firmar**. No se instala tal cual: hay que firmarla primero. |

Esto comprueba que el proyecto **compila** para iOS, aunque no puedas ejecutarlo.

### Para ejecutarlo de verdad

| Camino | Qué necesitas |
|---|---|
| Simulador | Un Mac con Xcode. Abre el simulador y arrastra el `.app` del `.zip`. |
| iPhone real (pruebas) | Un Mac con Xcode y un Apple ID. Con cuenta gratuita, la app caduca a los 7 días y hay límites. |
| iPhone real, distribución | **Apple Developer Program** (de pago, anual). Permite TestFlight y firma ad hoc. |

Existen herramientas de terceros que firman un `.ipa` con un Apple ID gratuito desde Windows; no
las gestiona este proyecto, y sus condiciones cambian, así que consulta su documentación vigente.

### Firma automática en el workflow (para más adelante)

Cuando haya cuenta de Apple Developer, el workflow `ios.yml` puede ampliarse para firmar y subir a
TestFlight guardando el certificado y el perfil de aprovisionamiento como *Secrets* del repositorio.
No está incluido hoy porque requiere esas credenciales.

---

## 4. Recomendación para la clase

1. **Todos desarrollan y prueban en el PC** (`run_game.py` y `main.py`).
2. **Android** es el camino más fácil para ver la app en un móvil real: APK desde Actions → teléfono.
3. **iOS**: la clase puede verificar que compila con Actions; verlo funcionando requiere un Mac.
   Si nadie tiene Mac, **la entrega puede ser Android + escritorio**, y iOS queda compilado y listo
   para quien tenga acceso a Xcode.

## 5. Notas técnicas

- **Python:** Kivy 2.3.1 funciona con Python 3.8-3.13 (no con 3.14).
- **Python en Android:** python-for-android (la herramienta que empaqueta) pasó a compilar
  Python 3.14 en su rama `master`, y Kivy 2.3.x no lo soporta: el build fallaba al instalar Kivy.
  Por eso `buildozer.spec` fija `p4a.branch = v2024.01.21` (Python 3.11.5, Kivy 2.3.0, NDK 25b,
  API 33). En el PC se usa Kivy 2.3.1; el código es el mismo. Cuando Kivy soporte Python 3.14,
  se podrá actualizar esa línea.
- **Dependencias en móvil:** solo funcionan las librerías puras de Python o las que tienen
  «receta» en `python-for-android` / `kivy-ios`. Antes de usar una librería nueva, hay que
  comprobar que exista su receta.
- **Orientación:** la app es vertical (`orientation = portrait` en `buildozer.spec`).
- **Notch y barras (iPhone / Android):** aún no se maneja el área segura; la barra superior de los
  juegos podría quedar bajo el notch en algunos iPhone.
- **Sonido:** los ajustes se guardan; la reproducción la implementará cada juego.
