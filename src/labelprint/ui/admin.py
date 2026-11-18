"""Ventana de autorizacion y acceso a la administracion."""

from __future__ import annotations

import tkinter as tk

from ..repositories.auth import AuthRepository
from .clients import ClientWindow
from .models import ModelWindow
from .parts import PartWindow
from .settings import SettingsWindow


class AdminWindow:
    def __init__(self, window: tk.Toplevel) -> None:
        self.wind = window
        self.wind.title("Autorizacion")
        self.wind.geometry("300x150")
        self.varMens = tk.StringVar()

        self.frame = tk.LabelFrame(self.wind, text="Supervisor")
        self.frame.grid(row=0, column=0, columnspan=3, pady=20, padx=20)

        tk.Label(self.frame, text="Usuario: ").grid(row=1, column=0)
        self.name = tk.Entry(self.frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        tk.Label(self.frame, text="Contrasena: ").grid(row=2, column=0)
        self.password = tk.Entry(self.frame, show="*")
        self.password.grid(row=2, column=1)
        self.password.bind("<Return>", self.validate_supervisor)

        tk.Button(
            self.frame, text="Validar", command=self.validate_supervisor
        ).grid(row=4, columnspan=3, sticky=tk.W + tk.E)

        tk.Label(
            self.frame, text="", textvariable=self.varMens, fg="red"
        ).grid(row=3, columnspan=3, sticky=tk.W + tk.E)

        self.frameOpc = tk.LabelFrame(self.wind, text="Opciones")
        self.frameOpc.grid(row=0, column=0, columnspan=3, pady=20)
        options = (
            ("Clientes", self.create_client_window),
            ("Modelos", self.create_model_window),
            ("Numeros de parte", self.create_part_window),
            ("Parametros", self.create_settings_window),
        )
        for index, (label, command) in enumerate(options, start=1):
            tk.Button(self.frameOpc, text=label, command=command).grid(
                row=index, columnspan=3, sticky=tk.W + tk.E, padx=10, pady=5
            )
        self.frameOpc.grid_forget()

    def validation(self) -> bool:
        return len(self.name.get()) != 0 and len(self.password.get()) != 0

    def validate_supervisor(self, event=None) -> None:
        if not self.validation():
            self.varMens.set("Usuario y contrasena son obligatorios!")
            return
        if AuthRepository.authenticate(self.name.get(), self.password.get()):
            self.wind.geometry("220x220")
            self.frame.grid_forget()
            self.frameOpc.grid(row=0, column=0, columnspan=3, pady=20, padx=20)
        else:
            self.varMens.set("Usuario o contrasena incorrectos!")

    def create_client_window(self) -> None:
        ClientWindow(tk.Toplevel(self.wind))

    def create_model_window(self) -> None:
        ModelWindow(tk.Toplevel(self.wind))

    def create_part_window(self) -> None:
        PartWindow(tk.Toplevel(self.wind))

    def create_settings_window(self) -> None:
        SettingsWindow(tk.Toplevel(self.wind))
