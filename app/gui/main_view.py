import customtkinter as ctk
from PIL import Image
import os

class MainView(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Simulador Planificación Cpu")
        self.geometry("1000x600")
        self.resizable(False, False)

        self._load_background()
        self._load_ui()

    def _load_background(self):
        fondo_path = os.path.join("app", "assets", "mainbackgroundsw.jpg")  # Aquí va fondo dual
        fondo = Image.open(fondo_path)

        fondo_img = ctk.CTkImage(light_image=fondo, dark_image=fondo, size=(1000, 600))

        self.bg_label = ctk.CTkLabel(self, image=fondo_img, text="")
        self.bg_label.image = fondo_img
        self.bg_label.place(x=0, y=0)

    def _load_ui(self):
        self._load_title()
        self._load_desc()
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
        
    def _load_desc(self):
        self.desc_label = ctk.CTkLabel(
            self,
            text="Bienvenido Padawan",
            font=("Times New Roman", 18, "bold"),  
            text_color="white",
            bg_color= "black"
        )
        self.desc_label.place(relx=0.104, rely=0.7, anchor="center")

    def _load_buttons(self):
        
        icon_rr_path = os.path.join("app", "assets", "round_robin_icon.png")
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

    # def _open_rr(self):
    #     from app.gui.rr_view import RRView
    #     self.destroy()
    #     rr_view = RRView()
    #     rr_view.mainloop()

    # def _open_srtf(self):
    #     from app.gui.srtf_view import SRTFView
    #     self.destroy()
    #     srtf_view = SRTFView()
    #     srtf_view.mainloop()

    # def _open_dual(self):
    #     from app.gui.dual_view import DualView
    #     self.destroy()
    #     dual_view = DualView()
    #     dual_view.mainloop()
    
        # Por ahora solo imprimimos un mensaje de prueba para que no dé error
    def _open_rr(self):
        print("Abrir RR View - pendiente de implementar")

    def _open_srtf(self):
        print("Abrir SRTF View - pendiente de implementar")

    def _open_dual(self):
        print("Abrir Dual View - pendiente de implementar")
