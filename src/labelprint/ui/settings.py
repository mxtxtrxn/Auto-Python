"""Administracion de parametros de la celda."""

from __future__ import annotations

import tkinter as tk

from ..repositories.settings import SettingsRepository


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class SettingsWindow:
    def __init__(self, window: tk.Toplevel) -> None:
        self.wind = window
        self.wind.title("Configuracion")
        self.Nuevo = 0

        frame = tk.LabelFrame(self.wind, text="Parametros")
        frame.grid(row=0, column=0, columnspan=3, pady=20)

        tk.Label(frame, text="Nombre de Celda: ").grid(row=1, column=0)
        self.name = tk.Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        tk.Label(frame, text="GPIO In: ").grid(row=2, column=0)
        self.gpioin = tk.Entry(frame)
        self.gpioin.grid(row=2, column=1)

        tk.Label(frame, text="GPIO Out: ").grid(row=3, column=0)
        self.gpioout = tk.Entry(frame)
        self.gpioout.grid(row=3, column=1)

        tk.Label(frame, text="Sleep impresion (s): ").grid(row=4, column=0)
        self.vsleep = tk.Entry(frame)
        self.vsleep.grid(row=4, column=1)

        self.vChk = tk.IntVar()
        self.scan = tk.Checkbutton(
            frame, text="Escanear", variable=self.vChk, onvalue=1, offvalue=0
        )
        self.scan.grid(row=5, column=1, sticky=tk.W)

        self.vChk2 = tk.IntVar()
        self.print_button = tk.Checkbutton(
            frame, text="Boton imprimir", variable=self.vChk2, onvalue=1, offvalue=0
        )
        self.print_button.grid(row=6, column=1, sticky=tk.W)

        self.vChk3 = tk.IntVar()
        self.print_rack = tk.Checkbutton(
            frame,
            text="Imprimir etiqueta rack",
            variable=self.vChk3,
            onvalue=1,
            offvalue=0,
        )
        self.print_rack.grid(row=7, column=1, sticky=tk.W)

        tk.Label(frame, text="Guardar produccion (hrs): ").grid(row=8, column=0)
        self.viHoras = tk.Entry(frame)
        self.viHoras.grid(row=8, column=1)

        tk.Button(frame, text="Guardar", command=self.save_settings).grid(
            row=9, columnspan=3, sticky=tk.W + tk.E
        )

        self.message = tk.Label(frame, text="", fg="red")
        self.message.grid(row=10, column=0, columnspan=3, sticky=tk.W + tk.E)

        self.load_settings()

    def load_settings(self) -> None:
        rows = SettingsRepository.get()
        if not rows:
            print("No hay parametros configurados")
            return
        item = rows[0]
        for field, value in zip(
            (self.name, self.gpioin, self.gpioout, self.vsleep, self.viHoras),
            (item[0], item[1], item[2], item[3], item[7]),
        ):
            field.delete(0, "end")
            field.insert(0, value)
        self.vChk.set(int(item[4]))
        self.vChk2.set(int(item[5]))
        self.vChk3.set(int(item[6]))

    def validation(self) -> bool:
        return (
            len(self.name.get()) != 0
            and len(self.gpioin.get()) != 0
            and len(self.gpioout.get()) != 0
            and len(self.vsleep.get()) != 0
        )

    def save_settings(self) -> None:
        if self.validation():
            SettingsRepository.save(
                self.name.get(),
                _to_int(self.gpioin.get()),
                _to_int(self.gpioout.get()),
                _to_int(self.vsleep.get()),
                int(self.vChk.get()),
                int(self.vChk2.get()),
                int(self.vChk3.get()),
                _to_int(self.viHoras.get()),
            )
            self.message["text"] = "Se guardo el registro correctamente!"
        else:
            self.message["text"] = "Se requiere llenar todos los campos!"
