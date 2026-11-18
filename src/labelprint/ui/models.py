"""Administracion de modelos."""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, ttk

from ..config import project_root
from ..repositories.clients import ClientRepository
from ..repositories.models import ModelRepository


class ModelWindow:
    def __init__(self, window: tk.Toplevel) -> None:
        self.wind = window
        self.wind.title("Administracion de Modelos")
        self.Nuevo = 0
        self.vIdCliente = 0
        self.dsClientes: list[tuple] = []

        frame = tk.LabelFrame(self.wind, text="Modelos")
        frame.grid(row=0, column=0, columnspan=5, pady=20)

        tk.Label(frame, text="Modelo: ").grid(row=1, column=1)
        self.name = tk.Entry(frame)
        self.name.focus()
        self.name.grid(row=2, column=1)

        tk.Label(frame, text="Cliente: ").grid(row=1, column=0)
        self.combo = ttk.Combobox(frame)

        tk.Label(frame, text="Plantilla: ").grid(row=1, column=2)
        self.plantilla = tk.Entry(frame)
        self.plantilla.grid(row=2, column=2)
        tk.Button(frame, text="Buscar", command=self.select_template).grid(
            row=3, column=2
        )

        tk.Label(frame, text="Estilo: ").grid(row=1, column=3)
        self.estilo = tk.Entry(frame)
        self.estilo.grid(row=2, column=3)
        tk.Button(frame, text="Buscar", command=self.select_style).grid(
            row=3, column=3
        )

        self.vChk = tk.IntVar()
        self.activo = tk.Checkbutton(
            frame, text="Activo", variable=self.vChk, onvalue=1, offvalue=0
        )
        self.activo.grid(row=4, column=0)

        tk.Button(frame, text="Guardar", command=self.save_model).grid(
            row=5, columnspan=5
        )
        tk.Button(frame, text="Nuevo", command=self.new_model).grid(row=6, column=0)

        self.message = tk.Label(frame, text="", fg="red")
        self.message.grid(row=7, column=0, columnspan=5, sticky=tk.W + tk.E)

        self.tree = ttk.Treeview(
            frame,
            height=10,
            columns=("#1", "#2", "#3", "#4", "#5", "#6", "#7"),
            show="headings",
        )
        self.tree.grid(row=8, column=0, columnspan=5)
        self.tree.heading("#1", text="Cliente", anchor=tk.CENTER)
        self.tree.heading("#2", text="Modelo", anchor=tk.CENTER)
        self.tree.heading("#3", text="Activo", anchor=tk.CENTER)
        self.tree.heading("#4", text="Plantilla", anchor=tk.CENTER)
        self.tree.heading("#5", text="Estilo", anchor=tk.CENTER)
        self.tree.heading("#6", text="IdModelo", anchor=tk.CENTER)
        self.tree.heading("#7", text="IdCliente", anchor=tk.CENTER)
        self.tree.bind("<<TreeviewSelect>>", self.get_selected_item)

        self.clear_table()
        self.load_clients()
        self.load_models()

    def clear_table(self) -> None:
        for element in self.tree.get_children():
            self.tree.delete(element)

    def load_clients(self) -> None:
        values = [""]
        self.dsClientes = ClientRepository.list_active()
        for item in self.dsClientes:
            values.append(str(item[1]))
        self.combo["values"] = values
        self.combo.grid(row=2, column=0)

    def load_models(self) -> None:
        for item in ModelRepository.list_all():
            self.tree.insert(
                "",
                0,
                text=item[1],
                values=(item[1], item[3], item[5], item[6], item[7], item[2], item[0]),
            )
        self.tree.column("#1", width=150)
        self.tree.column("#2", width=150)
        self.tree.column("#3", width=100)
        self.tree.column("#4", width=250)
        self.tree.column("#5", width=250)
        self.tree["displaycolumns"] = ("#1", "#2", "#3", "#4", "#5")

    def validation(self) -> bool:
        return len(self.name.get()) != 0 and len(self.combo.get()) != 0

    def save_model(self) -> None:
        if self.validation():
            self.update_selected_client()
            if self.Nuevo == 0:
                ModelRepository.create(
                    self.name.get(),
                    self.vIdCliente,
                    self.plantilla.get(),
                    self.estilo.get(),
                )
            else:
                ModelRepository.update(
                    self.Nuevo,
                    self.name.get(),
                    self.vIdCliente,
                    int(self.vChk.get()),
                    self.plantilla.get(),
                    self.estilo.get(),
                )
            self.message["text"] = "Se guardo el registro correctamente!"
            self.clear_table()
            self.load_models()
            self.combo.current(0)
            self.new_model()
        else:
            self.message["text"] = "Se requiere el nombre del modelo y/o cliente!"
            self.name.focus()

    def new_model(self) -> None:
        self.message["text"] = ""
        self.Nuevo = 0
        self.vChk.set(1)
        self.combo.current(0)
        self.name.delete(0, "end")
        self.plantilla.delete(0, "end")
        self.estilo.delete(0, "end")
        self.name.focus()

    def get_selected_item(self, event) -> None:
        self.message["text"] = ""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected)["values"]
        client_name = values[0]
        self.Nuevo = int(values[5])
        self.name.delete(0, "end")
        self.name.insert(0, values[1])
        self.plantilla.delete(0, "end")
        self.plantilla.insert(0, values[3])
        self.estilo.delete(0, "end")
        self.estilo.insert(0, values[4])
        self.vChk.set(1 if values[2] == "Activo" else 0)

        for index, value in enumerate(self.combo["values"]):
            if value == client_name:
                self.combo.current(index)

    def update_selected_client(self) -> None:
        selected = self.combo.get()
        for item in self.dsClientes:
            if item[1] == selected:
                self.vIdCliente = item[0]

    def _ask_file(self, folder: str, pattern: str) -> str:
        return filedialog.askopenfilename(
            title="Seleccionar archivo",
            initialdir=str(project_root() / folder),
            filetypes=((pattern, f"*{pattern}"), ("Todos los archivos", "*.*")),
        )

    def select_template(self) -> None:
        filename = self._ask_file("templates", ".html")
        self.plantilla.delete(0, "end")
        self.plantilla.insert(0, filename)

    def select_style(self) -> None:
        filename = self._ask_file("styles", ".css")
        self.estilo.delete(0, "end")
        self.estilo.insert(0, filename)
