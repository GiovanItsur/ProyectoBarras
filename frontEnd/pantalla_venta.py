from tkinter import ttk, messagebox
from datetime import datetime
import customtkinter as ctk

from BackEnd.PuntoVentaBKN import PuntoDeVentaBackend

TASA_IVA = 0.16

C_FONDO = "#FAF5EE"        # crema (fondo general)
C_TARJETA = "#FFFDF9"      # blanco cálido (tarjetas)
C_ARENA = "#F0E6D8"        # arena (campos, encabezados, botones secundarios)
C_ARENA_HOVER = "#E6D8C5"
C_BORDE = "#E8DCCB"        # bordes
C_TEXTO = "#3E2F2A"        # café oscuro
C_TEXTO_SUAVE = "#8A776B"  # café grisáceo
C_ACENTO = "#C4622D"       # terracota
C_ACENTO_HOVER = "#A84F21"
C_SELECCION = "#F6DCCB"    # terracota muy claro
C_PELIGRO = "#A6473B"      # rojo ladrillo

FUENTE = "Segoe UI"
MIN_CARACTERES_EMPLEADO = 3

class pantallaVenta(ctk.CTkFrame):
    def __init__(self, master, controlador, rolUsuario="Cajero", empleado=""):
        super().__init__(master, fg_color=C_FONDO)
        self.controlador = controlador
        self.rolUsuario = rolUsuario
        self.backend = PuntoDeVentaBackend()

        self.carrito = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_izquierdo()
        self._crear_panel_derecho(empleado)
        self._crear_atajos()

        self.entry_codigo.focus_set()

    def _crear_panel_izquierdo(self):
        izq = ctk.CTkFrame(self, fg_color="transparent")
        izq.grid(row=0, column=0, sticky="nsew", padx=(24, 12), pady=20)

        ctk.CTkLabel(izq, text="Escanear producto", font=(FUENTE, 12),
                     text_color=C_TEXTO_SUAVE).pack(anchor="w", padx=4)
        self.entry_codigo = ctk.CTkEntry(
            izq, height=46, corner_radius=12, font=(FUENTE, 16),
            fg_color=C_TARJETA, border_color=C_BORDE, border_width=1,
            text_color=C_TEXTO, placeholder_text="Código de barras",
            placeholder_text_color=C_TEXTO_SUAVE)
        self.entry_codigo.pack(fill="x", pady=(4, 12))
        self.entry_codigo.bind("<Return>", self.capturar_producto)

        tarjeta = ctk.CTkFrame(izq, fg_color=C_TARJETA, corner_radius=16,
                               border_width=1, border_color=C_BORDE)
        tarjeta.pack(fill="both", expand=True)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("POS.Treeview", background=C_TARJETA, fieldbackground=C_TARJETA,
                         foreground=C_TEXTO, rowheight=34, borderwidth=0,
                         font=(FUENTE, 11))
        estilo.map("POS.Treeview",
                   background=[("selected", C_SELECCION)],
                   foreground=[("selected", C_TEXTO)])
        estilo.configure("POS.Treeview.Heading", background=C_ARENA, foreground=C_TEXTO_SUAVE,
                         font=(FUENTE, 10, "bold"), borderwidth=0, relief="flat", padding=(8, 8))
        estilo.map("POS.Treeview.Heading", background=[("active", C_ARENA)])
        estilo.layout("POS.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        columnas = ("clave", "producto", "precio", "cantidad", "importe")
        self.grid_productos = ttk.Treeview(tarjeta, columns=columnas, show="headings",
                                           style="POS.Treeview", selectmode="browse")
        config = {"clave": ("CLAVE", 140, "w"), "producto": ("PRODUCTO", 190, "w"),
                  "precio": ("PRECIO", 80, "e"), "cantidad": ("CANT.", 60, "center"),
                  "importe": ("IMPORTE", 90, "e")}
        for col, (titulo, ancho, ancla) in config.items():
            self.grid_productos.heading(col, text=titulo)
            self.grid_productos.column(col, width=ancho, anchor=ancla)
        self.grid_productos.tag_configure("par", background=C_TARJETA)
        self.grid_productos.tag_configure("impar", background="#FBF6EE")
        self.grid_productos.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self.grid_productos.bind(
            "<<TreeviewSelect>>", lambda e: self.after_idle(self.entry_codigo.focus_set))

        acciones = ctk.CTkFrame(tarjeta, fg_color="transparent")
        acciones.pack(fill="x", padx=8, pady=(0, 8))
        self._boton_suave(acciones, "−", 40, lambda: self._cambiar_cantidad(-1)).pack(side="left", padx=(0, 6))
        self._boton_suave(acciones, "+", 40, lambda: self._cambiar_cantidad(1)).pack(side="left")
        ctk.CTkLabel(acciones, text="Teclas + y −  ·  F12 guardar", font=(FUENTE, 10),
                     text_color=C_TEXTO_SUAVE).pack(side="left", padx=12)
        self._boton_suave(acciones, "Quitar", 90, self.quitar_producto,
                          color_texto=C_PELIGRO).pack(side="right")

    def _crear_panel_derecho(self, empleado):
        der = ctk.CTkFrame(self, fg_color="transparent", width=290)
        der.grid(row=0, column=1, sticky="ns", padx=(12, 24), pady=20)

        ctk.CTkLabel(der, text="Punto de venta", font=(FUENTE, 22, "bold"),
                     text_color=C_TEXTO).pack(anchor="w", padx=4)
        ctk.CTkLabel(der, text="Nueva venta", font=(FUENTE, 12),
                     text_color=C_TEXTO_SUAVE).pack(anchor="w", padx=4, pady=(0, 12))

        # Tarjeta de datos de la venta
        datos = self._tarjeta(der)
        self.entry_folio = self._campo(datos, "FOLIO", "Se asigna al guardar", deshabilitado=True)
        self.entry_fecha = self._campo(datos, "FECHA", deshabilitado=True)
        self.entry_empleado = self._campo(datos, "EMPLEADO", ultimo=True)
        if empleado:
            self.entry_empleado.insert(0, empleado)
        # Al escribir, se quita el resaltado de error
        self.entry_empleado.bind(
            "<KeyRelease>", lambda e: self.entry_empleado.configure(border_width=0))
        self._poner_fecha()

        # Tarjeta de totales
        totales = self._tarjeta(der)
        self.lbl_subtotal = self._fila_total(totales, "Subtotal")
        self.lbl_iva = self._fila_total(totales, "IVA (16%)")
        ctk.CTkFrame(totales, height=1, fg_color=C_BORDE).pack(fill="x", padx=16, pady=6)
        fila = ctk.CTkFrame(totales, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(2, 14))
        ctk.CTkLabel(fila, text="Total", font=(FUENTE, 14, "bold"),
                     text_color=C_TEXTO).pack(side="left")
        self.lbl_total = ctk.CTkLabel(fila, text="$0.00", font=(FUENTE, 26, "bold"),
                                      text_color=C_ACENTO)
        self.lbl_total.pack(side="right")

        # Botones principales
        ctk.CTkButton(der, text="Guardar venta  (F12)", height=48, corner_radius=12,
                      font=(FUENTE, 15, "bold"), fg_color=C_ACENTO,
                      hover_color=C_ACENTO_HOVER, text_color="#FFFFFF",
                      command=self.guardar_venta).pack(fill="x", pady=(10, 8))
        ctk.CTkButton(der, text="Cancelar venta", height=40, corner_radius=12,
                      font=(FUENTE, 13), fg_color=C_ARENA, hover_color=C_ARENA_HOVER,
                      text_color=C_TEXTO, command=self.cancelar_venta).pack(fill="x")

    def _crear_atajos(self):
        # F12 guarda la venta desde cualquier parte de esta pantalla.
        # customtkinter no permite bind_all en sus widgets, así que se enlaza
        # a la ventana principal (recibe la tecla sin importar qué campo tenga el foco).
        self.winfo_toplevel().bind("<F12>", self._atajo_guardar)

        # + y - modifican la cantidad del producto seleccionado.
        # Solo se enlazan al lector y al grid (no al campo de empleado, para poder
        # escribir guiones en nombres). Devolver "break" evita que se escriba el símbolo.
        for widget in (self.entry_codigo, self.grid_productos):
            for tecla in ("<plus>", "<KP_Add>"):
                widget.bind(tecla, self._tecla_mas)
            for tecla in ("<minus>", "<KP_Subtract>"):
                widget.bind(tecla, self._tecla_menos)

    def destroy(self):
        # Libera F12 al cambiar de pantalla
        try:
            self.winfo_toplevel().unbind("<F12>")
        except Exception:
            pass
        super().destroy()

    # --------------------------------------------------- Helpers de diseño
    def _tarjeta(self, parent):
        t = ctk.CTkFrame(parent, fg_color=C_TARJETA, corner_radius=16,
                         border_width=1, border_color=C_BORDE)
        t.pack(fill="x", pady=(0, 12))
        return t

    def _campo(self, parent, titulo, placeholder="", deshabilitado=False, ultimo=False):
        ctk.CTkLabel(parent, text=titulo, font=(FUENTE, 10, "bold"),
                     text_color=C_TEXTO_SUAVE).pack(anchor="w", padx=16, pady=(8, 0))
        entry = ctk.CTkEntry(parent, height=32, corner_radius=8, fg_color=C_ARENA,
                             border_width=0, text_color=C_TEXTO, font=(FUENTE, 12),
                             placeholder_text=placeholder,
                             placeholder_text_color=C_TEXTO_SUAVE)
        # El último campo lleva margen inferior para no pegarse al borde de la tarjeta
        entry.pack(fill="x", padx=16, pady=(2, 14 if ultimo else 0))
        if deshabilitado:
            entry.configure(state="disabled")
        return entry

    def _fila_total(self, parent, texto):
        fila = ctk.CTkFrame(parent, fg_color="transparent")
        fila.pack(fill="x", padx=16, pady=(10, 0))
        ctk.CTkLabel(fila, text=texto, font=(FUENTE, 12),
                     text_color=C_TEXTO_SUAVE).pack(side="left")
        lbl = ctk.CTkLabel(fila, text="$0.00", font=(FUENTE, 13),
                           text_color=C_TEXTO)
        lbl.pack(side="right")
        return lbl

    def _boton_suave(self, parent, texto, ancho, comando, color_texto=C_TEXTO):
        return ctk.CTkButton(parent, text=texto, width=ancho, height=32, corner_radius=8,
                             font=(FUENTE, 13), fg_color=C_ARENA, hover_color=C_ARENA_HOVER,
                             text_color=color_texto, command=comando)

    def _set_texto(self, entry, texto):
        entry.configure(state="normal")
        entry.delete(0, "end")
        entry.insert(0, texto)
        entry.configure(state="disabled")

    def _poner_fecha(self):
        self._set_texto(self.entry_fecha, datetime.now().strftime("%d/%m/%Y  %H:%M"))

    # ------------------------------------------------------- Atajos de teclado
    def _atajo_guardar(self, event=None):
        self.guardar_venta()
        return "break"

    def _tecla_mas(self, event=None):
        self._cambiar_cantidad(1, silencioso=True)
        return "break"

    def _tecla_menos(self, event=None):
        self._cambiar_cantidad(-1, silencioso=True)
        return "break"

    # ------------------------------------------------------------ Lógica
    def capturar_producto(self, event=None):
        codigo = self.entry_codigo.get().strip()
        self.entry_codigo.delete(0, "end")
        if not codigo:
            return

        # Si el producto ya está en el carrito, solo sube la cantidad
        for item in self.carrito:
            if item["clave"] == codigo:
                self._agregar_cantidad(item)
                return

        ok, resultado = self.backend.buscar_producto(codigo)
        if not ok:
            messagebox.showwarning("Aviso", resultado)
            return

        id_producto, descripcion, precio, stock = resultado
        if stock <= 0:
            messagebox.showwarning("Sin stock", f"'{descripcion}' no tiene existencias.")
            return

        self.carrito.append({
            "id": id_producto, "clave": codigo, "producto": descripcion,
            "precio": float(precio), "cantidad": 1, "stock": int(stock),
        })
        # El último producto escaneado queda seleccionado para ajustarlo con + y -
        self.refrescar_grid(seleccionar=len(self.carrito) - 1)

    def _agregar_cantidad(self, item):
        if item["cantidad"] + 1 > item["stock"]:
            messagebox.showwarning("Sin stock", f"Solo hay {item['stock']} pieza(s) de '{item['producto']}'.")
            return
        item["cantidad"] += 1
        self.refrescar_grid(seleccionar=self.carrito.index(item))

    def _item_seleccionado(self, silencioso=False):
        seleccion = self.grid_productos.selection()
        if not seleccion:
            if not silencioso:
                messagebox.showinfo("Aviso", "Seleccione un producto del listado.")
            return None
        return self.carrito[self.grid_productos.index(seleccion[0])]

    def _cambiar_cantidad(self, delta, silencioso=False):
        item = self._item_seleccionado(silencioso)
        if item is None:
            return
        if delta > 0:
            self._agregar_cantidad(item)
        elif item["cantidad"] > 1:
            item["cantidad"] -= 1
            self.refrescar_grid(seleccionar=self.carrito.index(item))

    def quitar_producto(self):
        item = self._item_seleccionado()
        if item is not None:
            self.carrito.remove(item)
            self.refrescar_grid()

    def refrescar_grid(self, seleccionar=None):
        """Redibuja el grid, conserva la selección y recalcula subtotal, IVA y total."""
        if seleccionar is None:
            actual = self.grid_productos.selection()
            seleccionar = self.grid_productos.index(actual[0]) if actual else None

        self.grid_productos.delete(*self.grid_productos.get_children())
        for n, item in enumerate(self.carrito):
            importe = round(item["precio"] * item["cantidad"], 2)
            self.grid_productos.insert("", "end", tags=("par" if n % 2 == 0 else "impar",),
                                       values=(item["clave"], item["producto"],
                                               f"{item['precio']:.2f}", item["cantidad"],
                                               f"{importe:.2f}"))

        filas = self.grid_productos.get_children()
        if seleccionar is not None and filas:
            fila = filas[min(seleccionar, len(filas) - 1)]
            self.grid_productos.selection_set(fila)
            self.grid_productos.see(fila)

        subtotal, iva, total = self.calcular_totales()
        self.lbl_subtotal.configure(text=f"${subtotal:,.2f}")
        self.lbl_iva.configure(text=f"${iva:,.2f}")
        self.lbl_total.configure(text=f"${total:,.2f}")
        self.entry_codigo.focus_set()

    def calcular_totales(self):
        total = round(sum(i["precio"] * i["cantidad"] for i in self.carrito), 2)
        subtotal = round(total / (1 + TASA_IVA), 2)
        iva = round(total - subtotal, 2)
        return subtotal, iva, total

    def guardar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Aviso", "No hay productos en la venta.")
            return

        empleado = self.entry_empleado.get().strip()
        if len(empleado) < MIN_CARACTERES_EMPLEADO:
            self.entry_empleado.configure(border_width=2, border_color=C_PELIGRO)
            messagebox.showwarning(
                "Aviso",
                f"Capture el nombre del empleado (mínimo {MIN_CARACTERES_EMPLEADO} caracteres).")
            self.entry_empleado.focus_set()
            return

        subtotal, iva, total = self.calcular_totales()
        # Formato que espera el backend: (id_producto, cantidad, precio, importe)
        carrito_bd = [
            (i["id"], i["cantidad"], i["precio"], round(i["precio"] * i["cantidad"], 2))
            for i in self.carrito
        ]

        ok, mensaje = self.backend.guardar_venta(empleado, subtotal, iva, total, carrito_bd)
        if ok:
            messagebox.showinfo("Venta", mensaje)
            self.nueva_venta()
        else:
            messagebox.showerror("Error", mensaje)

    def cancelar_venta(self):
        if self.carrito and not messagebox.askyesno("Cancelar", "¿Descartar la venta actual?"):
            return
        self.nueva_venta()

    def nueva_venta(self):
        self.carrito.clear()
        self.refrescar_grid()
        self._poner_fecha()