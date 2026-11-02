"""Guardado local de puntuaciones y ajustes en un archivo JSON.

No depende de Kivy, así que se puede probar sin abrir ninguna ventana.
La app lo guarda dentro de `App.user_data_dir`, que es una carpeta privada de la app
tanto en Android como en iOS (y en el PC, en %APPDATA%).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

log = logging.getLogger("arcade.storage")


class Storage:
    """Lee y escribe `{"scores": {...}, "settings": {...}}` en un archivo JSON."""

    def __init__(self, path):
        self.path = Path(path)
        self._data = {"scores": {}, "settings": {}}
        self.load()

    # -- disco ---------------------------------------------------------------
    def load(self):
        """Carga el archivo. Si no existe o está dañado, se parte de cero sin fallar."""
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        if isinstance(raw, dict):
            for key in ("scores", "settings"):
                if isinstance(raw.get(key), dict):
                    self._data[key] = raw[key]

    def save(self):
        """Guarda de forma segura: escribe un temporal y lo renombra al final."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            os.replace(tmp, self.path)
        except OSError as exc:
            log.warning("No se pudo guardar %s: %s", self.path, exc)

    # -- puntuaciones --------------------------------------------------------
    def best(self, game_id: str) -> int:
        """Mejor puntuación de un juego (0 si nunca se ha jugado)."""
        return int(self._data["scores"].get(game_id, {}).get("best", 0))

    def plays(self, game_id: str) -> int:
        """Cuántas partidas se han terminado en ese juego."""
        return int(self._data["scores"].get(game_id, {}).get("plays", 0))

    def submit_score(self, game_id: str, score) -> bool:
        """Registra una partida terminada. Devuelve True si es un nuevo récord."""
        score = int(score)
        entry = self._data["scores"].setdefault(game_id, {"best": 0, "plays": 0})
        entry["plays"] = int(entry.get("plays", 0)) + 1
        is_record = score > int(entry.get("best", 0))
        if is_record:
            entry["best"] = score
        self.save()
        return is_record

    def reset_scores(self):
        """Borra todas las puntuaciones (no toca los ajustes)."""
        self._data["scores"] = {}
        self.save()

    # -- ajustes -------------------------------------------------------------
    def get_setting(self, key: str, default=None):
        return self._data["settings"].get(key, default)

    def set_setting(self, key: str, value):
        self._data["settings"][key] = value
        self.save()
