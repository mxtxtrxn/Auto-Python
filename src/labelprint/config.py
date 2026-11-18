"""Configuracion de la aplicacion."""

from __future__ import annotations

import configparser
import os
from dataclasses import dataclass
from pathlib import Path

ENV_PREFIX = "LABELPRINT_DB_"


def project_root() -> Path:
    """Devuelve la raiz del repositorio."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class DatabaseSettings:
    host: str = "localhost"
    database: str = "db_labelprint"
    user: str = "labelprint"
    password: str = ""

    def as_kwargs(self) -> dict[str, str]:
        return {
            "host": self.host,
            "database": self.database,
            "user": self.user,
            "password": self.password,
        }


def load_settings(path: Path | str | None = None) -> DatabaseSettings:
    """Lee la configuracion del INI y aplica las variables de entorno.

    Las variables de entorno tienen prioridad sobre el archivo, de modo que
    las credenciales no necesitan quedar escritas en el repositorio.
    """
    parser = configparser.ConfigParser()
    resolved = Path(path) if path is not None else project_root() / "config.ini"
    if resolved.is_file():
        parser.read(resolved, encoding="utf-8")

    def read(key: str, default: str) -> str:
        override = os.environ.get(ENV_PREFIX + key.upper())
        if override is not None:
            return override
        if parser.has_option("mysql", key):
            return parser.get("mysql", key)
        return default

    return DatabaseSettings(
        host=read("host", "localhost"),
        database=read("database", "db_labelprint"),
        user=read("user", "labelprint"),
        password=read("password", ""),
    )
