"""Ventanas de administracion."""

from .admin import AdminWindow
from .clients import ClientWindow
from .models import ModelWindow
from .parts import PartWindow
from .settings import SettingsWindow

__all__ = [
    "AdminWindow",
    "ClientWindow",
    "ModelWindow",
    "PartWindow",
    "SettingsWindow",
]
