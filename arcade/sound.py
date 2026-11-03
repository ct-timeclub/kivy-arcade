"""Efectos de sonido generados por código (estilo «chiptune»), sin archivos de audio.

Al primer uso se sintetizan unos archivos .wav pequeños en una carpeta temporal de la app y
se reproducen con SoundLoader de Kivy. Si algo falla (no hay audio, el dispositivo no lo
soporta...), el juego sigue en silencio: nunca debe tumbar la app.

Para desactivarlo del todo (por ejemplo en las pruebas): variable de entorno ARCADE_NO_SOUND=1.

Los juegos no usan esta clase directamente: llaman a `self.play_sound("coin")` (ver GameScreen).
"""

import array
import os
import random
import struct
import tempfile
import threading
import wave
from pathlib import Path

SAMPLE_RATE = 22050

# Cada efecto es una lista de «notas»:
#   (frecuencia_inicial, frecuencia_final, duración_s, onda, volumen)
# onda: "square" (cuadrada), "tri" (triangular), "noise" (ruido)
EFFECTS = {
    "flap": [(330, 560, 0.09, "square", 0.35)],
    "point": [(880, 880, 0.07, "square", 0.3), (1320, 1320, 0.12, "square", 0.3)],
    "hit": [(220, 70, 0.28, "noise", 0.5), (160, 60, 0.2, "square", 0.4)],
    "eat": [(520, 880, 0.09, "square", 0.3)],
    "golden": [(660, 660, 0.07, "square", 0.3), (880, 880, 0.07, "square", 0.3),
               (1320, 1320, 0.14, "square", 0.3)],
    "die": [(520, 520, 0.1, "tri", 0.45), (420, 420, 0.1, "tri", 0.45),
            (300, 90, 0.4, "tri", 0.45)],
    "jump": [(260, 640, 0.16, "square", 0.3)],
    "coin": [(988, 988, 0.07, "square", 0.3), (1319, 1319, 0.28, "square", 0.3)],
    "stomp": [(300, 120, 0.1, "square", 0.4), (200, 100, 0.06, "noise", 0.3)],
    "bump": [(150, 100, 0.08, "square", 0.4)],
    "win": [(523, 523, 0.12, "square", 0.3), (659, 659, 0.12, "square", 0.3),
            (784, 784, 0.12, "square", 0.3), (1047, 1047, 0.4, "square", 0.3)],
}


def _synthesize(notes):
    """Convierte la lista de notas en muestras de audio de 16 bits."""
    samples = array.array("h")
    for start_freq, end_freq, duration, kind, volume in notes:
        count = int(SAMPLE_RATE * duration)
        phase = 0.0
        for i in range(count):
            progress = i / max(count - 1, 1)
            freq = start_freq + (end_freq - start_freq) * progress
            phase += freq / SAMPLE_RATE
            if kind == "square":
                value = 1.0 if (phase % 1.0) < 0.5 else -1.0
            elif kind == "tri":
                value = 4.0 * abs((phase % 1.0) - 0.5) - 1.0
            else:
                value = random.uniform(-1.0, 1.0)
            # Envolvente: ataque cortísimo y caída suave para evitar «clics».
            attack = min(1.0, i / (SAMPLE_RATE * 0.004))
            decay = 1.0 - progress * 0.85
            samples.append(int(value * volume * attack * decay * 32000))
    return samples


def _write_wav(path, samples):
    """Escribe el .wav en un archivo temporal y lo renombra al final (así nunca queda a medias)."""
    temp = Path(f"{path}.{threading.get_ident()}.tmp")
    with wave.open(str(temp), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(struct.pack(f"<{len(samples)}h", *samples))
    os.replace(temp, path)


class SoundBank:
    """Genera (una sola vez) y reproduce los efectos. Se obtiene con SoundBank.get()."""

    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.enabled = os.environ.get("ARCADE_NO_SOUND") != "1"
        self._sounds = {}
        self._failed = set()
        self._folder = None
        self._warming = False

    def _folder_path(self):
        if self._folder is None:
            base = None
            try:
                from kivy.app import App

                app = App.get_running_app()
                if app is not None:
                    base = Path(app.user_data_dir)
            except Exception:  # noqa: BLE001
                base = None
            self._folder = (base or Path(tempfile.gettempdir())) / "sfx"
            self._folder.mkdir(parents=True, exist_ok=True)
        return self._folder

    def warm_up(self):
        """Genera TODOS los efectos en segundo plano (sin bloquear el juego).

        Sintetizar el audio en Python cuesta unos milisegundos por efecto; hacerlo aquí evita
        un tironcito la primera vez que suena cada uno en un teléfono lento.
        """
        if not self.enabled or self._warming:
            return
        self._warming = True
        folder = self._folder_path()      # se calcula en el hilo principal (usa Kivy)

        def work():
            for name, notes in EFFECTS.items():
                path = folder / f"{name}.wav"
                if not path.exists():
                    try:
                        _write_wav(path, _synthesize(notes))
                    except Exception:  # noqa: BLE001
                        pass

        threading.Thread(target=work, daemon=True).start()

    def _load(self, name):
        if name in self._sounds or name in self._failed or name not in EFFECTS:
            return self._sounds.get(name)
        try:
            from kivy.core.audio import SoundLoader

            path = self._folder_path() / f"{name}.wav"
            if not path.exists():
                _write_wav(path, _synthesize(EFFECTS[name]))
            sound = SoundLoader.load(str(path))
        except Exception:  # noqa: BLE001 - sin audio: seguimos en silencio
            sound = None
        if sound is None:
            self._failed.add(name)
            return None
        self._sounds[name] = sound
        return sound

    def play(self, name):
        """Reproduce el efecto `name`. Nunca lanza errores."""
        if not self.enabled:
            return
        try:
            sound = self._load(name)
            if sound is not None:
                sound.stop()
                sound.play()
        except Exception:  # noqa: BLE001
            self._failed.add(name)


def tone_length(name):
    """Duración total (en segundos) de un efecto. Útil para las pruebas."""
    return sum(note[2] for note in EFFECTS[name])
