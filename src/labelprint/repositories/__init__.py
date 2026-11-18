"""Repositorios de datos."""

from __future__ import annotations

from typing import Any, Sequence

from ..database import Database, DatabaseError


def fetch_rows(procedure: str, arguments: Sequence[Any]) -> list[tuple[Any, ...]]:
    """Ejecuta un procedimiento de consulta y devuelve una lista vacia si falla."""
    try:
        with Database() as db:
            return db.call_rows(procedure, arguments)
    except DatabaseError as exc:
        print(f"{procedure}: {exc}")
        return []


def fetch_row(procedure: str, arguments: Sequence[Any]) -> tuple[Any, ...] | None:
    """Ejecuta un procedimiento de consulta y devuelve la primera fila."""
    try:
        with Database() as db:
            return db.call_row(procedure, arguments)
    except DatabaseError as exc:
        print(f"{procedure}: {exc}")
        return None
