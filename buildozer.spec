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
requirements = python3,kivy==2.3.1

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

# (Los valores de android.api / android.ndk se dejan por defecto: buildozer elige
#  los que son compatibles con python-for-android.)

[buildozer]
# 0 = solo errores, 1 = información, 2 = depuración (muy detallado, útil si algo falla).
log_level = 2
warn_on_root = 1
