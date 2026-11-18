"""Acceso al catalogo de numeros de parte."""

from __future__ import annotations

from typing import Any

from . import fetch_row, fetch_rows


class PartRepository:
    @staticmethod
    def create(
        model_id: int,
        part_number: str,
        barcode1: str,
        barcode2: str,
        barcode3: str,
        scan_code: str,
        std_pack: int,
    ) -> tuple[Any, ...] | None:
        return fetch_row(
            "spNP",
            [
                "I",
                0,
                model_id,
                part_number,
                barcode1,
                barcode2,
                barcode3,
                0,
                scan_code,
                std_pack,
            ],
        )

    @staticmethod
    def update(
        part_id: int,
        model_id: int,
        part_number: str,
        barcode1: str,
        barcode2: str,
        barcode3: str,
        active: int,
        scan_code: str,
        std_pack: int,
    ) -> tuple[Any, ...] | None:
        return fetch_row(
            "spNP",
            [
                "E",
                part_id,
                model_id,
                part_number,
                barcode1,
                barcode2,
                barcode3,
                active,
                scan_code,
                std_pack,
            ],
        )

    @staticmethod
    def list_by_model(model_id: int) -> list[tuple[Any, ...]]:
        return fetch_rows("spNP", ["C1", 0, model_id, "", "", "", "", 0, "", 0])

    @staticmethod
    def get(part_id: int) -> list[tuple[Any, ...]]:
        return fetch_rows("spNP", ["C2", part_id, 0, "", "", "", "", 0, "", 0])

    @staticmethod
    def list_all() -> list[tuple[Any, ...]]:
        return fetch_rows("spNP", ["C3", 0, 0, "", "", "", "", 0, "", 0])

    @staticmethod
    def find_by_scan(scan_code: str) -> list[tuple[Any, ...]]:
        return fetch_rows("spNP", ["C4", 0, 0, "", "", "", "", 0, scan_code, 0])
