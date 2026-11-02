"""Pruebas del guardado de puntuaciones y ajustes (no necesitan ventana)."""

from arcade.storage import Storage


def test_empty_storage_has_zero_scores(tmp_path):
    storage = Storage(tmp_path / "data.json")
    assert storage.best("snake") == 0
    assert storage.plays("snake") == 0


def test_submit_score_tracks_record_and_plays(tmp_path):
    storage = Storage(tmp_path / "data.json")
    assert storage.submit_score("snake", 10) is True     # primer récord
    assert storage.submit_score("snake", 4) is False     # no supera
    assert storage.submit_score("snake", 25) is True     # nuevo récord
    assert storage.best("snake") == 25
    assert storage.plays("snake") == 3


def test_data_persists_between_instances(tmp_path):
    path = tmp_path / "data.json"
    Storage(path).submit_score("flappy", 7)
    assert Storage(path).best("flappy") == 7


def test_corrupt_file_does_not_crash(tmp_path):
    path = tmp_path / "data.json"
    path.write_text("{esto no es json", encoding="utf-8")
    storage = Storage(path)
    assert storage.best("snake") == 0


def test_settings_and_reset(tmp_path):
    storage = Storage(tmp_path / "data.json")
    assert storage.get_setting("sound", True) is True
    storage.set_setting("sound", False)
    storage.submit_score("snake", 5)
    storage.reset_scores()
    assert storage.get_setting("sound", True) is False   # los ajustes no se borran
    assert storage.best("snake") == 0
