"""Acceso al catalogo de modelos."""

from __future__ import annotations

from typing import Any

from . import fetch_row, fetch_rows


class ModelRepository:
    @staticmethod
    def create(
        name: str, client_id: int, template: str, style: str
    ) -> tuple[Any, ...] | None:
        return fetch_row("spModelos", ["I", 0, name, client_id, 0, template, style])

    @staticmethod
    def update(
        model_id: int,
        name: str,
        client_id: int,
        active: int,
        template: str,
        style: str,
    ) -> tuple[Any, ...] | None:
        return fetch_row(
            "spModelos",
            ["E", model_id, name, client_id, active, template, style],
        )

    @staticmethod
    def list_by_client(client_id: int) -> list[tuple[Any, ...]]:
        return fetch_rows("spModelos", ["C2", 0, "0", client_id, 0, "", ""])

    @staticmethod
    def get(model_id: int) -> list[tuple[Any, ...]]:
        return fetch_rows("spModelos", ["C3", model_id, "0", 0, 0, "", ""])

    @staticmethod
    def list_all() -> list[tuple[Any, ...]]:
        return fetch_rows("spModelos", ["C4", 0, "0", 0, 0, "", ""])
