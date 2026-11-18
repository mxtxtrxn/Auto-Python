"""Conexion a MySQL y utilidades para llamar procedimientos almacenados."""

from __future__ import annotations

from typing import Any, Sequence

import mysql.connector
from mysql.connector import Error

from .config import DatabaseSettings, load_settings


class DatabaseError(RuntimeError):
    """Error controlado al ejecutar una operacion de base de datos."""


class Database:
    """Envoltorio minimo sobre una conexion de ``mysql-connector``."""

    def __init__(self, settings: DatabaseSettings | None = None) -> None:
        self.settings = settings or load_settings()
        self._connection = None

    def connect(self):
        if self._connection is None:
            self._connection = mysql.connector.connect(**self.settings.as_kwargs())
        return self._connection

    def close(self) -> None:
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
        self._connection = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def call_rows(
        self, procedure: str, arguments: Sequence[Any]
    ) -> list[tuple[Any, ...]]:
        """Ejecuta un procedimiento y devuelve todas las filas del resultado."""
        try:
            cursor = self.connect().cursor()
            cursor.callproc(procedure, list(arguments))
            rows: list[tuple[Any, ...]] = []
            for result in cursor.stored_results():
                rows.extend(result.fetchall())
            cursor.close()
            return rows
        except Error as exc:
            raise DatabaseError(f"{procedure}: {exc}") from exc

    def call_row(
        self, procedure: str, arguments: Sequence[Any]
    ) -> tuple[Any, ...] | None:
        """Ejecuta un procedimiento y devuelve la primera fila, si existe."""
        rows = self.call_rows(procedure, arguments)
        return rows[0] if rows else None
