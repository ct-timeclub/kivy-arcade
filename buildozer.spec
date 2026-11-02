[app]

# ---- Identidad de la app --------------------------------------------------------------
title = Kivy Arcade
package.name = kivyarcade
# Cámbialo por el dominio de tu clase/escuela (al revés). Ej.: edu.miescuela
package.domain = org.clase
version = 0.1.0

# ---- Qué archivos se empaquetan --------------------------------------------------------
# buildozer busca main.py en la carpeta raíz.
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,wav,ogg,mp3
# Carpetas que NO van dentro de la app (pruebas, documentación, CI, builds...).
source.exclude_dirs = tests, docs, bin, .github, .git, .venv, venv, .buildozer, ios-toolchain
# La plantilla de juego es solo para los alumnos; no hace falta en el móvil.
source.exclude_patterns = games/_template/*

# ---- Dependencias de Python -------------------------------------------------------------
# Si un juego usa otra librería (por ejemplo pillow), se añade aquí Y en requirements.txt.
# La versión de Python y de Kivy en Android NO se eligen aquí: las fija la receta de
# python-for-android (ver p4a.branch más abajo): Python 3.11.5 y Kivy 2.3.0.
requirements = python3,kivy

# ---- python-for-android (la herramienta que empaqueta Python + Kivy para Android) ----------
# Fijamos una versión ESTABLE y conocida. La rama «master» pasó a compilar Python 3.14, y
# Kivy 2.3.x todavía no es compatible con él (el build falla al instalar Kivy/pyjnius).
# Con esta etiqueta: Python 3.11.5, Kivy 2.3.0, NDK 25b, API 33.
# Para actualizar en el futuro: cambiar a una versión nueva cuando Kivy soporte Python 3.14.
p4a.branch = v2024.01.21

# ---- Pantalla ----------------------------------------------------------------------------
# De momento toda la app es vertical. (Cada juego podría pedir otra orientación más adelante.)
orientation = portrait
fullscreen = 0

# ---- Android -----------------------------------------------------------------------------
# Acepta automáticamente las licencias del SDK (necesario para compilar en CI).
android.accept_sdk_license = True
# arm64-v8a: móviles actuales. x86_64: emulador de Android Studio en un PC con Intel/AMD.
# Cada arquitectura añade tiempo de compilación; quita x86_64 si no usas emulador.
android.archs = arm64-v8a, x86_64
# Esta app no necesita permisos especiales (ni internet).
android.permissions =
android.allow_backup = True

# Versiones que exige la versión de python-for-android fijada arriba (NDK 25b, API 33).
android.api = 33
android.ndk = 25b

[buildozer]
# 0 = solo errores, 1 = información, 2 = depuración (muy detallado, útil si algo falla).
log_level = 2
warn_on_root = 1
