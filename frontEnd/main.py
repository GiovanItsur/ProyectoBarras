import customtkinter as ctk
from pantalla_venta import pantallaVenta

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class pantallaLogin(ctk.CTkFrame):
    def __init__(self, master, controlador):
        super().__init__(master, fg_color = "#ffffff")
        self.controlador = controlador

class mainApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("1050x700")
        self.title("Sistema POS")
        self.resizable(False, False)

        self.pantallaActual = None
        self.cambiarPantalla(pantallaVenta)

    def cambiarPantalla(self, clasePantalla):
        if self.pantallaActual is not None:
            self.pantallaActual.destroy()

        self.pantallaActual = clasePantalla(master = self, controlador = self)
        self.pantallaActual.pack(fill = "both", expand = True)

    def cambiarPantallaConRol(self, clasePantalla, rol):
        if self.pantallaActual is not None:
            self.pantallaActual.destroy()

        self.pantallaActual = clasePantalla(
            master = self, controlador = self, rolUsuario = rol
        )
        self.pantallaActual.pack(fill = "both", expand = True)

# Función main
if __name__ == "__main__":
    app = mainApp()
    app.mainloop()