"""Acceso al catalogo de clientes."""

from __future__ import annotations

from typing import Any

from . import fetch_row, fetch_rows


class ClientRepository:
    @staticmethod
    def create(name: str) -> tuple[Any, ...] | None:
        return fetch_row("spClientes", ["I", 0, name, 0])

    @staticmethod
    def update(client_id: int, name: str, active: int) -> tuple[Any, ...] | None:
        return fetch_row("spClientes", ["E", client_id, name, active])

    @staticmethod
    def list_active() -> list[tuple[Any, ...]]:
        return fetch_rows("spClientes", ["C1", 0, "", 0])

    @staticmethod
    def get(client_id: int) -> list[tuple[Any, ...]]:
        return fetch_rows("spClientes", ["C2", client_id, "", 0])

    @staticmethod
    def list_all() -> list[tuple[Any, ...]]:
        return fetch_rows("spClientes", ["C3", 0, "", 0])
