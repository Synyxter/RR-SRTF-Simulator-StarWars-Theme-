import customtkinter as ctk
from PIL import Image
import os
from app.gui.rr_view import RRView
from app.gui.srtf_view import SRTFView

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador Planificación Cpu")
        self.geometry("1000x600")
        self.resizable(False, False)
        self.show()
        self._load_background()
        self._load_ui()

    def _load_background(self):
        fondo_path = os.path.join("app", "assets", "mainbackgroundsw.jpg")  
        fondo = Image.open(fondo_path)
        

        fondo_img = ctk.CTkImage(light_image=fondo, dark_image=fondo, size=(1000, 600))

        self.bg_label = ctk.CTkLabel(self, image=fondo_img, text="")
        self.bg_label.image = fondo_img
        self.bg_label.place(x=0, y=0)

    def show(self):
        self.lift()
        self._load_background()

    def _load_ui(self):
        self._load_title()
        self._load_buttons()
        

    def _load_title(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Simulador RR vs SRTF",
            font=("Star Jedi", 40, "bold"),  
            text_color="yellow",
            bg_color= "black"
        )
        self.title_label.place(relx=0.5, rely=0.1, anchor="center")
        
        mensaje = (
            "RR y SRTF son algoritmos de planificación de procesos.\n"
            "RR es justo pero equitativo, ideal para sistemas compartidos.\n"
            "SRTF es eficiente y veloz, óptimo para tareas cortas.\n"
            "Ambos buscan mejorar el rendimiento del sistema. . ."
        )

        self.info_label = ctk.CTkLabel(
            self,
            text=mensaje,
            font=("Century Gothic", 16, "bold"),  # Puedes cambiarlo a "Star Jedi" si ya está registrado
            text_color="#E0E0E0",
            justify="left",
            bg_color="black"
        )
        self.info_label.place(x=40, y=370)
        

    def _load_buttons(self):
        
        icon_rr_path = os.path.join("app", "assets", "round_robin_icon.jpg")
        icon_srtf_path = os.path.join("app", "assets", "srtf_icon.jpg")
        icon_dual_path = os.path.join("app", "assets", "dual_icon.jpg")

        icon_rr = ctk.CTkImage(Image.open(icon_rr_path), size=(40, 40))
        icon_srtf = ctk.CTkImage(Image.open(icon_srtf_path), size=(40, 40))
        icon_dual = ctk.CTkImage(Image.open(icon_dual_path), size=(40, 40))
        
        boton_rr = ctk.CTkButton(
            self, 
            text="Round Robin", 
            image=icon_rr,
            corner_radius=12,
            border_width=2,
            border_color="#FF0000",
            fg_color="transparent",
            hover_color="#1a0000",
            text_color="red",
            command=self._open_rr
        )
        boton_rr.place(x=40, y=150)
        
        boton_srtf = ctk.CTkButton(
            self, 
            text="    S R T F      ", 
            image=icon_srtf,
            corner_radius=12,
            border_width=2,
            border_color="#00FF00",
            fg_color="transparent",
            hover_color="#001a00",
            text_color="green",
            command=self._open_srtf
        )
        boton_srtf.place(x=40, y=220)

        boton_dual = ctk.CTkButton(
            self, 
            text=" RR vs SRTF", 
            image=icon_dual,
            corner_radius=12,
            border_width=2,
            border_color="#800080",
            fg_color="transparent",
            hover_color="#1a001a",
            text_color="purple",
            command=self._open_dual
        )
        boton_dual.place(x=40, y=290)

    def _open_rr(self):
        self.clear_view()
        self.rr_view = RRView(self, self._volver_menu)
        
    def _open_srtf(self):
        self.clear_view()
        self.srtf_view = SRTFView(self, self._volver_menu)


        
    def clear_view(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _open_dual(self):
        self.clear_view()
        label = ctk.CTkLabel(self, text="Vista dual (RR + SRTF) en desarrollo...", text_color="white", font=("Arial", 20))
        label.place(relx=0.5, rely=0.5, anchor="center")
        
    def _volver_menu(self):
        self.clear_view()
        self._load_ui()

if __name__ == '__main__':
    app = ctk.CTk()
    app.title("Simulador ")

# Para Windows, usa .ico. Para algunos Linux, .xbm o .png pueden funcionar.
# macOS maneja los íconos de ventana de manera diferente, a menudo a través del bundle de la app.
try:
    # Asegúrate que la ruta al ícono de la ventana sea correcta
    # Este ícono es para la ventana, no para el archivo .exe en sí.
    app.iconbitmap("app/assets/logolinuxstarwars.png")
except Exception as e:
    print(f"No se pudo establecer el ícono de la ventana: {e}")

# ... resto de tu configuración de la app ...
app.mainloop()