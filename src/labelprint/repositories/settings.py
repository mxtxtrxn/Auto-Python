"""Acceso a los parametros de la celda de produccion."""

from __future__ import annotations

from typing import Any

from . import fetch_row, fetch_rows


class SettingsRepository:
    @staticmethod
    def get() -> list[tuple[Any, ...]]:
        return fetch_rows("spParametros", ["", 0, 0, 0, 0, 0, "C1", 0, 0])

    @staticmethod
    def save(
        name: str,
        pin_in: int,
        pin_out: int,
        delay: int,
        scanner: int,
        button: int,
        print_rack: int,
        hours: int,
    ) -> tuple[Any, ...] | None:
        return fetch_row(
            "spParametros",
            [name, pin_in, pin_out, delay, scanner, button, "E", print_rack, hours],
        )
