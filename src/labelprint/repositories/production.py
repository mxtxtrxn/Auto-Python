"""Acceso a las producciones y al conteo de piezas."""

from __future__ import annotations

from typing import Any

from . import fetch_row, fetch_rows


class ProductionRepository:
    @staticmethod
    def create(
        part_number: str, scan_code: str, quantity: int, target: int
    ) -> int | None:
        row = fetch_row("spPiezas", ["I", part_number, scan_code, quantity, target, 0])
        return int(row[0]) if row else None

    @staticmethod
    def close(production_id: int) -> tuple[Any, ...] | None:
        return fetch_row("spPiezas", ["CE", "", "", 0, 0, production_id])

    @staticmethod
    def close_with_pieces(production_id: int) -> tuple[Any, ...] | None:
        return fetch_row("spPiezas", ["CP", "", "", 0, 0, production_id])

    @staticmethod
    def find_active(scan_code: str) -> list[tuple[Any, ...]]:
        return fetch_rows("spPiezas", ["C1", "", scan_code, 0, 0, 0])

    @staticmethod
    def find_with_pieces(scan_code: str) -> list[tuple[Any, ...]]:
        return fetch_rows("spPiezas", ["C2", "", scan_code, 0, 0, 0])

    @staticmethod
    def clear(production_id: int) -> tuple[Any, ...] | None:
        return fetch_row("spPiezas", ["CL", "", "", 0, 0, production_id])

    @staticmethod
    def add_piece(production_id: int) -> tuple[Any, ...] | None:
        return fetch_row("spPiezas", ["AD", "", "", 0, 0, production_id])

    @staticmethod
    def remove_pieces(production_id: int, quantity: int) -> tuple[Any, ...] | None:
        return fetch_row("spPiezas", ["LE", "", "", quantity, 0, production_id])
