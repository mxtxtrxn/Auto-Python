"""Pruebas de la configuracion."""

from __future__ import annotations

from labelprint.config import DatabaseSettings, load_settings

ENV_VARS = (
    "LABELPRINT_DB_HOST",
    "LABELPRINT_DB_DATABASE",
    "LABELPRINT_DB_USER",
    "LABELPRINT_DB_PASSWORD",
)


def clear_environment(monkeypatch) -> None:
    for name in ENV_VARS:
        monkeypatch.delenv(name, raising=False)


def test_defaults_when_file_is_missing(monkeypatch, tmp_path) -> None:
    clear_environment(monkeypatch)
    settings = load_settings(tmp_path / "missing.ini")
    assert settings == DatabaseSettings()


def test_reads_values_from_ini(monkeypatch, tmp_path) -> None:
    clear_environment(monkeypatch)
    path = tmp_path / "config.ini"
    path.write_text(
        "[mysql]\n"
        "host = db.local\n"
        "database = labels\n"
        "user = app\n"
        "password = secret\n",
        encoding="utf-8",
    )
    settings = load_settings(path)
    assert settings.host == "db.local"
    assert settings.database == "labels"
    assert settings.user == "app"
    assert settings.password == "secret"


def test_environment_overrides_file(monkeypatch, tmp_path) -> None:
    path = tmp_path / "config.ini"
    path.write_text(
        "[mysql]\nhost = db.local\ndatabase = labels\nuser = app\npassword = file\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("LABELPRINT_DB_HOST", "env.local")
    monkeypatch.setenv("LABELPRINT_DB_PASSWORD", "env-secret")
    settings = load_settings(path)
    assert settings.host == "env.local"
    assert settings.password == "env-secret"
    assert settings.database == "labels"


def test_partial_file_falls_back_to_defaults(monkeypatch, tmp_path) -> None:
    clear_environment(monkeypatch)
    path = tmp_path / "config.ini"
    path.write_text("[mysql]\nuser = app\n", encoding="utf-8")
    settings = load_settings(path)
    assert settings.user == "app"
    assert settings.host == "localhost"
    assert settings.database == "db_labelprint"
    assert settings.password == ""


def test_as_kwargs_matches_mysql_connector_arguments() -> None:
    settings = DatabaseSettings(host="h", database="d", user="u", password="p")
    assert settings.as_kwargs() == {
        "host": "h",
        "database": "d",
        "user": "u",
        "password": "p",
    }
