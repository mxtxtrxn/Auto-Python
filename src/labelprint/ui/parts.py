"""Administracion de numeros de parte."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..repositories.clients import ClientRepository
from ..repositories.models import ModelRepository
from ..repositories.parts import PartRepository


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class PartWindow:
    def __init__(self, window: tk.Toplevel) -> None:
        self.wind = window
        self.wind.title("Administracion de Numeros de Parte")
        self.Nuevo = 0
        self.vIdCliente = 0
        self.dsClientes: list[tuple] = []
        self.vIdModelo = 0
        self.dsModelos: list[tuple] = []

        frame = tk.LabelFrame(self.wind, text="Numeros de parte")
        frame.grid(row=0, column=0, pady=20, padx=10)

        tk.Label(frame, text="Clientes: ").grid(row=1, column=1)
        self.combocliente = ttk.Combobox(frame)
        self.combocliente.grid(row=2, column=1)
        self.combocliente.bind("<<ComboboxSelected>>", self.get_selected_client)

        tk.Label(frame, text="Modelos: ").grid(row=1, column=2)
        self.combo = ttk.Combobox(frame)
        self.combo.grid(row=2, column=2)

        tk.Label(frame, text="No. Parte: ").grid(row=1, column=3)
        self.parte = tk.Entry(frame)
        self.parte.focus()
        self.parte.grid(row=2, column=3)

        tk.Label(frame, text="No. Parte Cliente: ").grid(row=3, column=1)
        self.cb1 = tk.Entry(frame)
        self.cb1.grid(row=4, column=1)

        tk.Label(frame, text="Barcode linea 2 (opcional): ").grid(row=3, column=2)
        self.cb2 = tk.Entry(frame)
        self.cb2.grid(row=4, column=2)

        tk.Label(frame, text="Barcode linea 3 (opcional): ").grid(row=3, column=3)
        self.cb3 = tk.Entry(frame)
        self.cb3.grid(row=4, column=3)

        tk.Label(frame, text="Barcode escaner (opcional): ").grid(row=5, column=1)
        self.cbEscan = tk.Entry(frame)
        self.cbEscan.grid(row=6, column=1)

        tk.Label(frame, text="Standard pack: ").grid(row=5, column=2)
        self.cbstandpack = tk.Entry(frame)
        self.cbstandpack.grid(row=6, column=2)

        self.vChk = tk.IntVar()
        self.activo = tk.Checkbutton(
            frame, text="Activo", variable=self.vChk, onvalue=1, offvalue=0
        )
        self.activo.grid(row=6, column=3)

        tk.Button(frame, text="Nuevo", command=self.new_part).grid(row=2, column=0)
        tk.Button(frame, text="Guardar", command=self.save_part).grid(row=4, column=0)

        self.message = tk.Label(frame, text="", fg="red")
        self.message.grid(row=7, column=0, columnspan=5, sticky=tk.W + tk.E)

        self.tree = ttk.Treeview(
            frame,
            height=10,
            columns=tuple(f"#{i}" for i in range(1, 12)),
            show="headings",
        )
        self.tree.grid(row=9, column=0, columnspan=5)
        headers = (
            "Cliente",
            "Modelo",
            "No. Parte",
            "No. Parte Cliente",
            "Barcode 2",
            "Barcode 3",
            "Activo",
            "Barcode Scan",
            "Std Pack",
            "IdNP",
            "IdModelo",
        )
        for index, header in enumerate(headers, start=1):
            self.tree.heading(f"#{index}", text=header, anchor=tk.CENTER)
        self.tree.bind("<<TreeviewSelect>>", self.get_selected_item)

        self.clear_table()
        self.load_clients()
        self.load_parts()

    def clear_table(self) -> None:
        for element in self.tree.get_children():
            self.tree.delete(element)

    def validation(self) -> bool:
        return (
            len(self.parte.get()) != 0
            and len(self.combo.get()) != 0
            and len(self.cb1.get()) != 0
        )

    def load_clients(self) -> None:
        values = [""]
        self.dsClientes = ClientRepository.list_active()
        for item in self.dsClientes:
            values.append(str(item[1]))
        self.combocliente["values"] = values

    def get_selected_client(self, event) -> None:
        selected = self.combocliente.get()
        if len(selected) > 0:
            for item in self.dsClientes:
                if item[1] == selected:
                    self.vIdCliente = item[0]
            self.load_models(self.vIdCliente)

    def load_models(self, client_id: int) -> None:
        values = [""]
        self.dsModelos = ModelRepository.list_by_client(client_id)
        for item in self.dsModelos:
            values.append(str(item[3]))
        self.combo["values"] = values

    def save_part(self) -> None:
        if self.validation():
            self.update_selected_model()
            if self.Nuevo == 0:
                PartRepository.create(
                    self.vIdModelo,
                    self.parte.get(),
                    self.cb1.get(),
                    self.cb2.get(),
                    self.cb3.get(),
                    self.cbEscan.get(),
                    _to_int(self.cbstandpack.get()),
                )
            else:
                PartRepository.update(
                    self.Nuevo,
                    self.vIdModelo,
                    self.parte.get(),
                    self.cb1.get(),
                    self.cb2.get(),
                    self.cb3.get(),
                    int(self.vChk.get()),
                    self.cbEscan.get(),
                    _to_int(self.cbstandpack.get()),
                )
            self.message["text"] = "Se guardo el registro correctamente!"
            self.clear_table()
            self.combocliente.current(0)
            self.combo.current(0)
            self.load_parts()
            self.new_part()
        else:
            self.message["text"] = "Se requiere el numero de parte, modelo y cliente!"
            self.parte.focus()

    def new_part(self) -> None:
        self.message["text"] = ""
        self.Nuevo = 0
        self.vChk.set(1)
        self.combocliente.current(0)
        self.combo["values"] = ""
        self.combo.delete(0, "end")
        for field in (self.cb1, self.cb2, self.cb3, self.parte,
                      self.cbEscan, self.cbstandpack):
            field.delete(0, "end")
        self.parte.focus()

    def load_parts(self) -> None:
        for item in PartRepository.list_all():
            self.tree.insert(
                "",
                0,
                values=(
                    item[1],
                    item[3],
                    item[5],
                    item[6],
                    item[7],
                    item[8],
                    item[11],
                    item[12],
                    item[13],
                    item[4],
                    item[2],
                ),
            )
        for index in range(1, 10):
            self.tree.column(f"#{index}", width=150)
        self.tree["displaycolumns"] = tuple(f"#{i}" for i in range(1, 10))

    def get_selected_item(self, event) -> None:
        self.message["text"] = ""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected)["values"]
        client_name = values[0]
        self.Nuevo = int(values[9])
        self.parte.delete(0, "end")
        self.parte.insert(0, values[2])
        self.cb1.delete(0, "end")
        self.cb1.insert(0, values[3])
        self.cb2.delete(0, "end")
        self.cb2.insert(0, values[4])
        self.cb3.delete(0, "end")
        self.cb3.insert(0, values[5])
        self.cbEscan.delete(0, "end")
        self.cbEscan.insert(0, values[7])
        self.cbstandpack.delete(0, "end")
        self.cbstandpack.insert(0, values[8])
        self.vChk.set(1 if values[6] == "Activo" else 0)

        for index, value in enumerate(self.combocliente["values"]):
            if value == client_name:
                self.combocliente.current(index)

        self.update_selected_client()
        self.load_models(self.vIdCliente)
        model_name = values[1]
        for index, value in enumerate(self.combo["values"]):
            if value == model_name:
                self.combo.current(index)

    def update_selected_client(self) -> None:
        selected = self.combocliente.get()
        for item in self.dsClientes:
            if item[1] == selected:
                self.vIdCliente = item[0]

    def update_selected_model(self) -> None:
        selected = self.combo.get()
        for item in self.dsModelos:
            if str(item[3]) == str(selected):
                self.vIdModelo = item[2]
