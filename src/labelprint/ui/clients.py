"""Administracion de clientes."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..repositories.clients import ClientRepository


class ClientWindow:
    def __init__(self, window: tk.Toplevel) -> None:
        self.wind = window
        self.wind.title("Administracion de Clientes")
        self.Nuevo = 0

        frame = tk.LabelFrame(self.wind, text="Clientes")
        frame.grid(row=0, column=0, columnspan=5, pady=20)

        tk.Label(frame, text="Cliente: ").grid(row=1, column=0)
        self.name = tk.Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        self.vChk = tk.IntVar()
        self.activo = tk.Checkbutton(
            frame, text="Activo", variable=self.vChk, onvalue=1, offvalue=0
        )
        self.activo.grid(row=2, column=0)

        tk.Button(frame, text="Guardar", command=self.save_client).grid(
            row=3, columnspan=5
        )
        tk.Button(frame, text="Nuevo", command=self.new_client).grid(row=4)

        self.message = tk.Label(frame, text="", fg="red")
        self.message.grid(row=5, column=0, columnspan=5, sticky=tk.W + tk.E)

        self.tree = ttk.Treeview(frame, height=10, columns=2)
        self.tree.grid(row=6, column=0, columnspan=5)
        self.tree.heading("#0", text="Cliente", anchor=tk.CENTER)
        self.tree.heading("#1", text="Activo", anchor=tk.CENTER)
        self.tree.bind("<<TreeviewSelect>>", self.get_selected_item)

        self.clear_table()
        self.load_clients()

    def clear_table(self) -> None:
        for element in self.tree.get_children():
            self.tree.delete(element)

    def load_clients(self) -> None:
        for item in ClientRepository.list_all():
            self.tree.insert("", 0, text=item[1], values=(item[3], item[2], item[0]))

    def validation(self) -> bool:
        return len(self.name.get()) != 0

    def save_client(self) -> None:
        if self.validation():
            if self.Nuevo == 0:
                ClientRepository.create(self.name.get())
            else:
                ClientRepository.update(
                    self.Nuevo, self.name.get(), int(self.vChk.get())
                )
            self.message["text"] = "Se guardo el registro correctamente!"
            self.clear_table()
            self.load_clients()
        else:
            self.message["text"] = "Se requiere el nombre del cliente!"

    def new_client(self) -> None:
        self.message["text"] = ""
        self.Nuevo = 0
        self.vChk.set(1)
        self.name.delete(0, "end")
        self.name.focus()

    def get_selected_item(self, event) -> None:
        self.message["text"] = ""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected)["values"]
        text = self.tree.item(selected)["text"]
        self.Nuevo = int(values[2])
        self.name.delete(0, "end")
        self.name.insert(0, text)
        self.vChk.set(1)
