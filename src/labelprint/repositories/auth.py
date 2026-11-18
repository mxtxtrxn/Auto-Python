"""Validacion de usuarios de administracion."""

from __future__ import annotations

from typing import Any

from . import fetch_row


class AuthRepository:
    @staticmethod
    def authenticate(user: str, password: str) -> tuple[Any, ...] | None:
        return fetch_row("spSupervisor", [user, password])
