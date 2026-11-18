"""Ventana principal del sistema de impresion de etiquetas."""

from __future__ import annotations

import os
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from .repositories.clients import ClientRepository
from .repositories.models import ModelRepository
from .repositories.parts import PartRepository
from .repositories.production import ProductionRepository
from .repositories.settings import SettingsRepository
from .ui.admin import AdminWindow

try:
    import RPi.GPIO as GPIO
except ImportError:  # pragma: no cover - depende del hardware
    GPIO = None

try:
    import cups
except ImportError:  # pragma: no cover - depende del hardware
    cups = None

try:
    from blabel import LabelWriter
except ImportError:  # pragma: no cover - depende del entorno
    LabelWriter = None


def _to_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class LabelPrintApp:
    def __init__(self, window: tk.Tk) -> None:
        self.wind = window
        self.wind.title("LabelPrint 1.0")
        self.wind.geometry("1200x650")
        self.wind.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.Nuevo = 0
        self.vIdCliente = 0
        self.dsClientes: list[tuple] = []
        self.vIdModelo = 0
        self.dsModelo: list[tuple] = []
        self.vIdNP = 0
        self.vIdNPCliente = 0
        self.viContador = 0
        self.viTotal = 0
        self.dsNP: list[tuple] = []
        self.itemNP = None
        self.impresora = ""
        self.paramCelda = ""
        self.paramGPIOIn = 0
        self.paramGPIOOut = 0
        self.paramSleep = 0
        self.paramBoton = 0
        self.paramEscaner = 0
        self.paramHoras = 0

        self.var = tk.StringVar()
        self.varCliente = tk.StringVar()
        self.varModelo = tk.StringVar()
        self.varNP = tk.StringVar()
        self.varNPCliente = tk.StringVar()
        self.varProceso = tk.StringVar()
        self.varTotalPiezas = tk.StringVar()
        self.varTotalPiezasMens = tk.StringVar()
        self.varPiezasContador = tk.StringVar()
        self.varClienteRack = tk.StringVar()
        self.varModeloRack = tk.StringVar()
        self.varParteRack = tk.StringVar()
        self.varNPClienteRack = tk.StringVar()
        self.varTotalPiezasRack = tk.StringVar()
        self.varerror = tk.StringVar()

        self.CB1 = ""
        self.CB2 = ""
        self.CB3 = ""
        self.varplantilla = ""
        self.varestilo = ""
        self.vParte = ""
        self.vCodigoBarras = ""
        self.hilo = None
        self.bHiloEjecutando = 0
        self.bCerrarHilo = 0
        self.IdProduccion = 0
        self.IdProduccionAnterior = 0
        self.iHorasProduccion = 0
        self.iStdPack = 0
        self.IPiezasPrint = 0
        self.bReturnPrint = 0
        self.iPiezasPendientes = 0
        self.iPiezasActivas = 0

        menubar = tk.Menu(self.wind)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Cerrar", command=self.salida)
        menubar.add_command(label="Ajustar", command=self.ajustar_piezas)
        menubar.add_command(label="Configuracion", command=self.open_admin)
        menubar.add_cascade(label="Salir", menu=filemenu)
        self.wind.config(menu=menubar)

        self.Titulo = tk.Label(
            self.wind,
            text="   ",
            font=("Arial", 20),
            fg="black",
            bg="light sky blue",
            textvariable=self.var,
        )
        self.Titulo.grid(row=0, column=0, columnspan=6, sticky=tk.W + tk.E)

        frameMensaje = tk.LabelFrame(self.wind, text="")
        frameMensaje.grid(
            row=4, column=0, columnspan=4, padx=20, pady=20, sticky=tk.W + tk.E
        )
        self.printers = tk.Label(frameMensaje, text="", font=("Arial", 10))
        self.printers.grid(
            row=2, column=0, columnspan=3, sticky=tk.W + tk.E, padx=10, pady=5
        )
        self.perror = tk.Label(
            frameMensaje,
            text="",
            font=("Arial", 12),
            fg="white",
            bg="red",
            textvariable=self.varerror,
        )
        self.perror.grid(
            row=4, column=0, columnspan=3, sticky=tk.W + tk.E, padx=10, pady=5
        )

        self.frame = tk.LabelFrame(
            self.wind, text="Seleccion de No. Parte", font=("Arial", 12)
        )
        self.frame.grid(row=1, column=0, padx=20, pady=20, sticky=tk.N)
        tk.Label(self.frame, text="Clientes: ").grid(row=1, column=1)
        self.combocliente = ttk.Combobox(self.frame)
        self.combocliente.grid(row=2, column=1, padx=10, pady=10)
        self.combocliente.bind("<<ComboboxSelected>>", self.get_selected_client)
        tk.Label(self.frame, text="Modelos: ").grid(row=3, column=1)
        self.comboModelo = ttk.Combobox(self.frame)
        self.comboModelo.grid(row=4, column=1, padx=10, pady=10)
        self.comboModelo.bind("<<ComboboxSelected>>", self.get_selected_model)
        tk.Label(self.frame, text="No. Parte: ").grid(row=5, column=1)
        self.comboNP = ttk.Combobox(self.frame)
        self.comboNP.grid(row=6, column=1, padx=10, pady=10)
        self.comboNP.bind("<<ComboboxSelected>>", self.get_selected_np)
        tk.Button(self.frame, text="Iniciar", command=self.start).grid(
            row=7, column=1, pady=5
        )

        self.load_clients()
        self.build_rack_grid()
        self.build_scan_grid()
        self.find_printer()
        self.load_parameters()
        self.varProceso.set("Esperando senal!")

    def on_closing(self) -> None:
        if messagebox.askokcancel("Salir", "Quiere salir?"):
            self.bCerrarHilo = 1
            self.wind.destroy()

    def build_scan_grid(self) -> None:
        self.frameInicio = tk.LabelFrame(self.wind, text="Escaneo")
        self.frameInicio.grid(row=1, column=0, padx=20, pady=20, sticky=tk.N)
        tk.Label(self.frameInicio, text="Escanear: ", font=("Arial", 14)).grid(
            row=1, column=1
        )
        self.cbPieza = tk.Entry(self.frameInicio)
        self.cbPieza.focus()
        self.cbPieza.grid(row=2, column=1, padx=10, pady=10)
        self.cbPieza.bind("<Return>", self.on_scan_enter)
        self.lblCliente = tk.Label(
            self.frameInicio,
            text="Cliente:",
            font=("Arial", 11),
            textvariable=self.varCliente,
        )
        self.lblCliente.grid(
            row=4, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lblModelo = tk.Label(
            self.frameInicio,
            text="Modelo:",
            font=("Arial", 11),
            textvariable=self.varModelo,
        )
        self.lblModelo.grid(
            row=5, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lblParte = tk.Label(
            self.frameInicio,
            text="No. Parte:",
            font=("Arial", 11),
            textvariable=self.varNP,
        )
        self.lblParte.grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)
        self.lblNPCliente = tk.Label(
            self.frameInicio,
            text="NP Cliente:",
            font=("Arial", 11),
            textvariable=self.varNPCliente,
        )
        self.lblNPCliente.grid(
            row=7, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lStatus = tk.Label(
            self.frameInicio,
            text="Esperando",
            font=("Arial", 25),
            fg="black",
            bg="gold",
        )
        self.lStatus.grid(row=8, column=0, columnspan=3, sticky=tk.W + tk.E)

    def build_rack_grid(self) -> None:
        self.frameInicioRack = tk.LabelFrame(self.wind, text="Impresion Etiqueta")
        self.frameInicioRack.grid(row=1, column=4, padx=20, pady=20, sticky=tk.N)
        tk.Label(
            self.frameInicioRack, text="Escanear numero parte: ", font=("Arial", 14)
        ).grid(row=1, column=1)
        self.cbRack = tk.Entry(self.frameInicioRack)
        self.cbRack.focus()
        self.cbRack.grid(row=2, column=1, padx=10, pady=10)
        self.cbRack.bind("<Return>", self.on_scan_rack_enter)
        self.lblClienteRack = tk.Label(
            self.frameInicioRack,
            text="Cliente:",
            font=("Arial", 11),
            textvariable=self.varClienteRack,
        )
        self.lblClienteRack.grid(
            row=4, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lblModeloRack = tk.Label(
            self.frameInicioRack,
            text="Modelo:",
            font=("Arial", 11),
            textvariable=self.varModeloRack,
        )
        self.lblModeloRack.grid(
            row=5, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lblParteRack = tk.Label(
            self.frameInicioRack,
            text="No. Parte:",
            font=("Arial", 11),
            textvariable=self.varParteRack,
        )
        self.lblParteRack.grid(row=6, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5)
        self.lblNPClienteRack = tk.Label(
            self.frameInicioRack,
            text="NP Cliente:",
            font=("Arial", 11),
            textvariable=self.varNPClienteRack,
        )
        self.lblNPClienteRack.grid(
            row=7, column=0, columnspan=3, sticky=tk.W, padx=10, pady=5
        )
        self.lStatusRack = tk.Label(
            self.frameInicioRack,
            text="Esperando",
            font=("Arial", 25),
            fg="black",
            bg="plum2",
        )
        self.lStatusRack.grid(row=8, column=0, columnspan=3, sticky=tk.W + tk.E)

    def load_clients(self) -> None:
        values = [""]
        self.dsClientes = ClientRepository.list_active()
        if self.dsClientes:
            for item in self.dsClientes:
                values.append(str(item[1]))
            self.combocliente["values"] = values
        else:
            self.combocliente["values"] = ["No hay registros"]

    def get_selected_client(self, event) -> None:
        selected = self.combocliente.get()
        if len(selected) > 0:
            for item in self.dsClientes:
                if item[1] == selected:
                    self.vIdCliente = item[0]
                    self.varCliente.set("Cliente: " + str(item[1]))
            self.load_models(self.vIdCliente)

    def load_models(self, client_id: int) -> None:
        values = [""]
        self.dsModelo = ModelRepository.list_by_client(client_id)
        if self.dsModelo:
            for item in self.dsModelo:
                values.append(str(item[3]))
            self.comboModelo["values"] = values
            
            self.comboNP["values"] = ""
            self.comboNP.delete(0, "end")

    def get_selected_model(self, event) -> None:
        selected = self.comboModelo.get()
        if len(selected) > 0:
            for item in self.dsModelo:
                if item[3] == selected:
                    self.vIdModelo = item[2]
                    self.varModelo.set("Modelo: " + str(item[3]))
            self.load_parts(self.vIdModelo)

    def load_parts(self, model_id: int) -> None:
        values = [""]
        self.dsNP = PartRepository.list_by_model(model_id)
        if self.dsNP:
            for item in self.dsNP:
                values.append(str(item[1]))
            self.comboNP["values"] = values

    def get_selected_np(self, event) -> None:
        selected = self.comboNP.get()
        if len(selected) == 0:
            return
        for item in self.dsNP:
            if item[1] == selected:
                self.itemNP = item
                self.vIdNP = item[0]
                self.vSAP = str(item[1])
                self.vCodigoBarras = str(item[5])
                self.CB1 = str(item[2])
                self.CB2 = str(item[3])
                self.CB3 = str(item[4])
                self.iStdPack = int(item[6])
                self.varNP.set("No. Parte: " + str(item[1]))
                self.varNPCliente.set("NP Cliente: " + str(item[2]))
                model_rows = ModelRepository.get(self.vIdModelo)
                if model_rows:
                    self.varplantilla = model_rows[0][4]
                    self.varestilo = model_rows[0][5]

    def start(self) -> None:
        if hasattr(self, "frameGeneral"):
            self.frameGeneral.grid_forget()
        self.frameGeneral = tk.LabelFrame(self.wind)
        self.frameGeneral.grid(row=1, column=1, padx=20, pady=20, sticky=tk.N)

        framePrint = tk.LabelFrame(
            self.frameGeneral, text="IMPRESION", font=("Arial", 14)
        )
        framePrint.grid(row=1, column=1, padx=20, pady=20, sticky=tk.N)
        self.lblproceso = tk.Label(
            framePrint,
            text="Esperando senal",
            textvariable=self.varProceso,
            font=("Arial", 40),
            fg="red",
            bg="yellow",
        )
        self.lblproceso.grid(row=2, column=1, sticky=tk.W + tk.E, padx=10, pady=5)

        if self.bHiloEjecutando == 1:
            self.bCerrarHilo = 1

        self.varPiezasContador.set("0")
        self.frameConteo = tk.LabelFrame(
            self.frameGeneral, text="CONTADOR", font=("Arial", 14)
        )
        self.frameConteo.grid(row=2, column=1, padx=20, pady=20, sticky=tk.N)
        self.lblContador = tk.Label(
            self.frameConteo,
            text="",
            textvariable=self.varPiezasContador,
            font=("Arial", 80),
            fg="white",
            bg="lightgray",
        )
        self.lblContador.grid(row=1, column=0, padx=5, pady=5)
        tk.Label(self.frameConteo, text="de", font=("Arial", 40), fg="black").grid(
            row=1, column=2, padx=5, pady=5
        )
        self.lblTotal = tk.Label(
            self.frameConteo,
            text="",
            textvariable=self.varTotalPiezas,
            font=("Arial", 80),
            fg="white",
            bg="lightblue",
        )
        self.lblTotal.grid(row=1, column=3, padx=5, pady=5)

        if self.paramEscaner == 1:
            self.cbPieza.grid_forget()
            tk.Button(self.frameInicio, text="Detener", command=self.stop).grid(
                row=11, column=1, pady=5
            )
            raw_rack = getattr(self, "vPTRack", "")
            target = int(raw_rack[1:]) if raw_rack[:1].upper() == "Q" else 0
            rows = ProductionRepository.find_active(self.vCodigoBarras)
            if not rows:
                self.IdProduccion = ProductionRepository.create(
                    self.vParte, self.vCodigoBarras, 0, target
                ) or 0
            else:
                row = rows[0]
                self.iHorasProduccion = int(row[2]) if row[2] is not None else 0
                if self.iHorasProduccion > self.paramHoras:
                    ProductionRepository.close(int(row[0]))
                    self.IdProduccion = ProductionRepository.create(
                        self.vParte, self.vCodigoBarras, 0, target
                    ) or 0
                    messagebox.showinfo(
                        "Aviso",
                        "Se cerro una produccion con mas de "
                        + str(self.paramHoras)
                        + " hrs",
                    )
                elif messagebox.askyesno(
                    "Alerta", "Hay una produccion abierta, cerrar la produccion?"
                ):
                    production_id = int(row[0])
                    if int(row[4]) > int(row[3]):
                        ProductionRepository.close_with_pieces(production_id)
                    else:
                        ProductionRepository.close(production_id)
                    self.IdProduccion = ProductionRepository.create(
                        self.vParte, self.vCodigoBarras, 0, target
                    ) or 0
                else:
                    self.varPiezasContador.set(str(row[3]))
                    self.varTotalPiezas.set(str(row[4]))
                    self.IdProduccion = int(row[0])

        self.bHiloEjecutando = 1
        self.hilo = threading.Thread(target=self.thread_read, args=(1,), daemon=True)
        self.hilo.start()

    def on_scan_enter(self, event) -> None:
        text = self.cbPieza.get()
        if len(text) > 0:
            rows = PartRepository.find_by_scan(text.upper())
            if rows:
                item = rows[0]
                self.vIdCliente = item[0]
                self.varCliente.set("Cliente: " + str(item[1]))
                self.vIdModelo = int(item[2])
                self.varModelo.set("Modelo: " + str(item[3]))
                self.vIdNP = item[4]
                self.varNP.set("No. Parte: " + str(item[5]))
                self.vParte = str(item[5])
                self.vCodigoBarras = text.upper()
                self.varNPCliente.set("NP Cliente: " + str(item[6]))
                self.CB1 = str(item[6])
                self.CB2 = str(item[7])
                self.CB3 = str(item[8])
                self.lStatus.config(bg="green", fg="white")
                self.lStatus["text"] = "Correcto"
                model_rows = ModelRepository.get(self.vIdModelo)
                if model_rows:
                    self.varplantilla = model_rows[0][4]
                    self.varestilo = model_rows[0][5]
                if self.bHiloEjecutando == 1:
                    self.bHiloEjecutando = 0
                    self.bCerrarHilo = 1
                self.varTotalPiezasMens.set("Piezas:")
                self.lblPiezasRack = tk.Label(
                    self.frameInicio,
                    text="Piezas:",
                    font=("Arial", 11),
                    textvariable=self.varTotalPiezasMens,
                )
                self.lblPiezasRack.grid(
                    row=9, column=1, sticky=tk.W, padx=10, pady=5
                )
                self.cbPiezasRack = tk.Entry(self.frameInicio)
                self.cbPiezasRack.grid(row=10, column=1, padx=1, pady=5)
                self.cbPiezasRack.focus()
                self.cbPiezasRack.bind("<Return>", self.on_pieces_enter)
            else:
                self.lStatus.config(bg="red", fg="white")
                self.lStatus["text"] = "No. Parte incorrecto!"
        else:
            self.lStatus.config(bg="red", fg="white")
            self.lStatus["text"] = "Sin lectura!"
        self.cbPieza.delete(0, tk.END)

    def on_scan_rack_enter(self, event) -> None:
        text = self.cbRack.get()
        if len(text) > 0:
            rows = PartRepository.find_by_scan(text.upper())
            if rows:
                item = rows[0]
                self.vIdCliente = item[0]
                self.varClienteRack.set("Cliente: " + str(item[1]))
                self.vIdModelo = int(item[2])
                self.varModeloRack.set("Modelo: " + str(item[3]))
                self.vIdNP = item[4]
                self.varParteRack.set("No. Parte: " + str(item[5]))
                self.vParte = str(item[5])
                self.vCodigoBarras = text.upper()
                self.varNPClienteRack.set("NP Cliente: " + str(item[6]))
                self.CB1 = str(item[6])
                self.CB2 = str(item[7])
                self.CB3 = str(item[8])
                self.iStdPack = int(item[13])
                self.lStatusRack.config(bg="green", fg="white")
                self.lStatusRack["text"] = "Correcto"
                model_rows = ModelRepository.get(self.vIdModelo)
                if model_rows:
                    self.varplantilla = model_rows[0][4]
                    self.varestilo = model_rows[0][5]

                self.iPiezasPendientes = 0
                self.IdProduccionAnterior = 0
                rows = ProductionRepository.find_with_pieces(text.upper())
                if rows:
                    row = rows[0]
                    self.IdProduccionAnterior = int(row[0])
                    self.lStatusRack["text"] = "Piezas " + str(row[3])
                    self.iPiezasPendientes = int(row[3])
                else:
                    self.iPiezasActivas = 0
                    rows = ProductionRepository.find_active(text.upper())
                    if rows:
                        row = rows[0]
                        self.lStatusRack["text"] = "Piezas " + str(row[3])
                        self.iPiezasActivas = int(row[3])
                    else:
                        messagebox.showinfo(
                            "Aviso", "No hay piezas para ese numero de parte!"
                        )
                self.varTotalPiezasRack.set("Cantidad:")
                self.lblPiezasRackPrint = tk.Label(
                    self.frameInicioRack,
                    text="Piezas:",
                    font=("Arial", 11),
                    textvariable=self.varTotalPiezasRack,
                )
                self.lblPiezasRackPrint.grid(
                    row=9, column=1, sticky=tk.W, padx=10, pady=5
                )
                self.cbPiezasRackPrint = tk.Entry(self.frameInicioRack)
                self.cbPiezasRackPrint.grid(row=10, column=1, padx=1, pady=5)
                self.cbPiezasRackPrint.focus()
                self.cbPiezasRackPrint.bind("<Return>", self.on_rack_pieces_enter)
            else:
                self.lStatusRack.config(bg="red", fg="white")
                self.lStatusRack["text"] = "No. Parte incorrecto!"
        else:
            self.lStatusRack.config(bg="red", fg="white")
            self.lStatusRack["text"] = "Sin lectura!"
        self.cbRack.delete(0, tk.END)

    def on_pieces_enter(self, event) -> None:
        self.vPTRack = str(self.cbPiezasRack.get())
        if self.vPTRack[0:1].upper() == "Q":
            self.varTotalPiezasMens.set("Piezas: " + self.vPTRack[1:])
            self.cbPiezasRack.grid_forget()
            self.varTotalPiezas.set(self.vPTRack[1:])
            tk.Button(self.frameInicio, text="Iniciar", command=self.start).grid(
                row=11, column=1, pady=5
            )

    def on_rack_pieces_enter(self, event) -> None:
        self.vPTRack = str(self.cbPiezasRackPrint.get())
        if self.vPTRack[0:1].upper() != "Q":
            return
        quantity = _to_int(self.vPTRack[1:])
        self.varTotalPiezasRack.set("Piezas: " + self.vPTRack[1:])
        if self.iStdPack < quantity:
            self.varTotalPiezasRack.set("Piezas: ")
            self.cbPiezasRackPrint.delete(0, tk.END)
            messagebox.showwarning(
                "Aviso", "Cantidad de piezas mayor al standard pack!"
            )
            return

        self.IPiezasPrint = quantity
        self.cbPiezasRackPrint.grid_forget()
        if self.iPiezasPendientes > 0:
            if self.iPiezasPendientes >= self.IPiezasPrint:
                result = ProductionRepository.remove_pieces(
                    self.IdProduccionAnterior, self.IPiezasPrint
                )
                self.print_label()
                if result and int(result[0]) == 0:
                    ProductionRepository.close(self.IdProduccionAnterior)
                    messagebox.showinfo("Aviso", "Se cerro la produccion anterior!")
            else:
                messagebox.showwarning(
                    "Aviso", "No hay piezas suficientes de la produccion anterior!"
                )
        else:
            if self.iPiezasActivas >= self.IPiezasPrint:
                result = ProductionRepository.remove_pieces(
                    self.IdProduccion, self.IPiezasPrint
                )
                if result and int(result[0]) == 0:
                    ProductionRepository.close(self.IdProduccion)
                    messagebox.showinfo("Aviso", "Se cerro la produccion actual!")
                self.print_label()
            else:
                messagebox.showwarning("Aviso", "No hay piezas suficientes!")

        self.varClienteRack.set("")
        self.varModeloRack.set("")
        self.varParteRack.set("")
        self.varNPClienteRack.set("")
        self.lStatusRack.config(bg="plum2", fg="black")
        self.lStatusRack["text"] = "Esperando"
        self.varTotalPiezasRack.set("")

    def ajustar_piezas(self) -> None:
        if not hasattr(self, "frameGeneral"):
            return
        if hasattr(self, "frameAjuste"):
            self.frameAjuste.grid_forget()
        self.frameAjuste = tk.LabelFrame(
            self.frameGeneral, text="Ajuste de piezas", font=("Arial", 14)
        )
        self.frameAjuste.grid(row=3, column=1, padx=20, pady=20, sticky=tk.N)
        tk.Button(self.frameAjuste, text="+", command=self.add_pieces).grid(
            row=1, column=2, pady=5, padx=5
        )
        tk.Label(self.frameAjuste, text="          ").grid(row=1, column=1)
        tk.Button(self.frameAjuste, text="-", command=self.remove_pieces).grid(
            row=1, column=0, pady=5, padx=5
        )

    def add_pieces(self) -> None:
        pieces = _to_int(self.varTotalPiezas.get()) + 1
        if pieces <= 50:
            self.varTotalPiezas.set(str(pieces))

    def remove_pieces(self) -> None:
        pieces = _to_int(self.varTotalPiezas.get()) - 1
        if pieces >= _to_int(self.varPiezasContador.get()):
            self.varTotalPiezas.set(str(pieces))

    def thread_read(self, running: int) -> None:
        if GPIO is None:
            self.varerror.set("RPi.GPIO no esta disponible en este equipo")
            return
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            button = self.paramGPIOIn
            GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            signal = 0
            while running == 1:
                if GPIO.input(button) == 1:
                    if signal == 0:
                        signal = 1
                        self.varProceso.set("Imprimiendo!")
                        self.lblproceso.config(fg="green", bg="white")
                        self.viTotal = _to_int(self.varTotalPiezas.get())
                        self.viContador = _to_int(self.varPiezasContador.get()) + 1
                        if self.viContador < self.viTotal:
                            self.add_production_piece()
                            time.sleep(self.paramSleep)
                        else:
                            if self.viContador == self.viTotal:
                                self.add_production_piece()
                                self.wind.after(0, self.stop)
                            else:
                                self.wind.after(0, self.stop)
                    time.sleep(0.1)
                if GPIO.input(button) == 0:
                    if signal == 1:
                        signal = 0
                        time.sleep(0.1)
                        self.varProceso.set("Esperando senal!")
                        self.lblproceso.config(fg="red", bg="yellow")
                if self.bCerrarHilo == 1:
                    self.bCerrarHilo = 0
                    break
        except Exception as exc:
            self.varerror.set("Error en hilo: " + str(exc))

    def add_production_piece(self) -> None:
        if not self.IdProduccion:
            rows = ProductionRepository.find_active(self.vCodigoBarras)
            if rows:
                self.IdProduccion = int(rows[0][0])
        if self.IdProduccion:
            ProductionRepository.add_piece(self.IdProduccion)

    def find_printer(self) -> None:
        if cups is None:
            self.printers["text"] = "Impresora: servicio no disponible"
            return
        try:
            printers = cups.Connection().getPrinters()
            for printer in printers:
                self.impresora = printer
            self.printers["text"] = "Impresora: " + self.impresora
        except Exception as exc:
            self.printers["text"] = "Impresora: error (" + str(exc) + ")"

    def print_button(self) -> None:
        self.viTotal = _to_int(self.varTotalPiezas.get())
        self.viContador = _to_int(self.varPiezasContador.get()) + 1
        if self.viContador < self.viTotal:
            self.print_label()
            time.sleep(self.paramSleep)
        else:
            if self.viContador == self.viTotal:
                self.print_label()
            self.stop()

    def print_label(self) -> None:
        if LabelWriter is None or cups is None:
            self.varerror.set("La impresion no esta disponible en este equipo")
            return
        try:
            self.varPiezasContador.set(str(self.viContador))
            self.perror.config(text="")
            code = self.CB2 + "$" + datetime.now().strftime("%y%m%d%H%M%S")
            code += "$" + str(self.IPiezasPrint)
            records = [
                {
                    "sample_id": code,
                    "BC_1": self.CB1,
                    "BC_2": self.CB2,
                    "BC_3": "Pza:" + str(self.IPiezasPrint),
                }
            ]
            writer = LabelWriter(
                self.varplantilla, default_stylesheets=(self.varestilo,)
            )
            size = 0
            while size == 0:
                try:
                    writer.write_labels(records, target="label.pdf")
                    writer.write_labels(records, target="label1.pdf")
                    size = os.path.getsize("label.pdf")
                except Exception as exc:
                    size = 0
                    self.bReturnPrint = 0
                    print("Error al generar la etiqueta: " + str(exc))

            connection = cups.Connection()
            if len(connection.getJobs()) > 1:
                self.varerror.set(
                    "Error en Imprimir Etiqueta - hay un trabajo bloqueando"
                )
                print("Error en Imprimir Etiqueta - hay un trabajo bloqueando")
                time.sleep(0.2)
                self.print_label()
            else:
                size = os.path.getsize("label.pdf")
                target = "label.pdf" if size > 0 else "label1.pdf"
                job = connection.printFile(
                    self.impresora,
                    target,
                    "",
                    {
                        "orientation-request": "5",
                        "PageSize": "Custom.45x15mm",
                        "zeTearOffPosition": "25",
                    },
                )
                while connection.getJobs().get(job, None) is not None:
                    time.sleep(0.1)
        except Exception as exc:
            self.varerror.set("Error en Imprimir: " + str(exc))
            self.bReturnPrint = 0

    def stop(self) -> None:
        if self.bHiloEjecutando == 1:
            self.bHiloEjecutando = 0
            self.bCerrarHilo = 1
        if hasattr(self, "frameGeneral"):
            self.frameGeneral.grid_forget()
        self.frameInicio.grid_forget()
        self.varCliente.set("Cliente: ")
        self.varModelo.set("Modelo: ")
        self.varNP.set("No. Parte: ")
        self.varNPCliente.set("NP Cliente: ")
        self.build_scan_grid()

    def salida(self) -> None:
        if messagebox.askyesno("Salir", "Quiere salir?"):
            self.wind.destroy()

    def open_admin(self) -> None:
        AdminWindow(tk.Toplevel(self.wind))

    def load_parameters(self) -> None:
        rows = SettingsRepository.get()
        if not rows:
            return
        item = rows[0]
        self.paramCelda = item[0]
        self.paramGPIOIn = int(item[1])
        self.paramGPIOOut = int(item[2])
        self.paramSleep = int(item[3])
        self.paramEscaner = int(item[4])
        self.paramBoton = int(item[5])
        self.paramHoras = int(item[7])
        self.var.set(str(self.paramCelda))
        if self.paramEscaner == 1:
            self.frame.grid_forget()
        else:
            self.frameInicio.grid_forget()
        if self.paramBoton == 1:
            tk.Button(
                self.wind,
                text="Imprimir",
                command=self.print_button,
                width=10,
                height=3,
            ).grid(row=2, column=0, pady=5)


def main() -> None:
    window = tk.Tk()
    LabelPrintApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
