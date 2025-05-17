import customtkinter as ctk
import os
import app.config as config
from app.config import APP_ICON_PATH, ASSETS_DIR, BG_IMAGE_RR_PATH, BG_IMAGE_SRTF_PATH, COLOR_AMARILLO

# Importar las vistas desde views.py dentro de app/gui
from app.gui.views import RRView, SRTFView
# Nota: ResultsView es llamada por RRView y SRTFView, no directamente aquí a menos que tengas un menú más complejo.

class MainApplication(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Simulador de Planificación RR & SRTF")
        self.geometry("1280x720+100+50") # Ancho x Alto + offset_x + offset_y
        ctk.set_appearance_mode("dark")
        # ctk.set_default_color_theme("blue") # O "green", "dark-blue"

        # Establecer el ícono de la ventana
        if os.path.exists(APP_ICON_PATH):
            try:
                self.iconbitmap(APP_ICON_PATH) # Para Windows, necesita un archivo .ico
                print(f"INFO (MainApp): Ícono de ventana establecido desde '{APP_ICON_PATH}'")
            except Exception as e:
                print(f"ERROR (MainApp): No se pudo establecer el ícono de ventana desde '{APP_ICON_PATH}': {e}")
                print("Asegúrate que el archivo es un .ico válido y la ruta es correcta.")
        else:
            print(f"ADVERTENCIA (MainApp): Archivo de ícono para la ventana NO ENCONTRADO en '{APP_ICON_PATH}'")

        self.current_view = None
        self.create_main_menu_buttons() # Crear botones para seleccionar RR o SRTF

    def create_main_menu_buttons(self):
        # Limpiar cualquier vista anterior
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None

        # Frame para los botones del menú
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Título del Menú
        try:
            font_titulo_menu = ("Star Jedi", 40)
            ctk.CTkLabel(menu_frame, text="Simulador de Planificación", font=font_titulo_menu, text_color=config.COLOR_AMARILLO).pack(pady=(20, 40))
        except:
            font_titulo_menu = ("Arial", 30, "bold")
            ctk.CTkLabel(menu_frame, text="Simulador de Planificación", font=font_titulo_menu, text_color=config.COLOR_AMARILLO).pack(pady=(20, 40))


        # Botones para RR y SRTF
        button_font = ("space age", 18)
        try: ctk.CTkButton(menu_frame, text="", font=button_font).destroy() # Check font
        except: button_font = ("Arial", 16, "bold")

        btn_rr = ctk.CTkButton(menu_frame, text="Round Robin (RR)", command=self.show_rr_view,
                               font=button_font, width=300, height=60,
                               fg_color=config.COLOR_ROJO, hover_color=config.COLOR_ROJO_OSCURO,
                               text_color=config.COLOR_AMARILLO)
        btn_rr.pack(pady=20)

        btn_srtf = ctk.CTkButton(menu_frame, text="Shortest Remaining Time First (SRTF)", command=self.show_srtf_view,
                                 font=button_font, width=300, height=60,
                                 fg_color=config.COLOR_VERDE, hover_color=config.COLOR_VERDE_OSCURO,
                                 text_color=config.COLOR_AMARILLO)
        btn_srtf.pack(pady=20)

        # Botón de Salir
        btn_salir = ctk.CTkButton(menu_frame, text="Salir", command=self.quit,
                                 font=button_font, width=200, height=50,
                                 fg_color="#555555", hover_color="#333333")
        btn_salir.pack(pady=(40,20))


    def show_rr_view(self):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = RRView(master=self, volver_callback_menu_principal=self.create_main_menu_buttons)
        # RRView se empaqueta a sí misma en su __init__

    def show_srtf_view(self):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = SRTFView(master=self, volver_callback_menu_principal=self.create_main_menu_buttons)
        # SRTFView se empaqueta a sí misma en su __init__

if __name__ == "__main__":
    # --- Verificación de Rutas (Importante para Depuración) ---
    print(f"--- INICIANDO APLICACIÓN ---")
    print(f"Directorio Base (config.py): {config.BASE_DIR}")
    print(f"Directorio de Assets (config.py): {ASSETS_DIR}")
    if not os.path.isdir(ASSETS_DIR):
        print(f"ERROR CRÍTICO: El directorio de ASSETS '{ASSETS_DIR}' NO EXISTE.")
        print("Por favor, crea la carpeta 'assets' en el mismo directorio que 'config.py' y coloca las imágenes allí.")
    else:
        print(f"Ruta Ícono App (config.py): {APP_ICON_PATH} - Existe: {os.path.exists(APP_ICON_PATH)}")
        print(f"Ruta Fondo RR (config.py): {BG_IMAGE_RR_PATH} - Existe: {os.path.exists(BG_IMAGE_RR_PATH)}")
        print(f"Ruta Fondo SRTF (config.py): {BG_IMAGE_SRTF_PATH} - Existe: {os.path.exists(BG_IMAGE_SRTF_PATH)}")
    print(f"----------------------------")

    app = MainApplication()
    app.mainloop()
    print(f"--- APLICACIÓN FINALIZADA ---")
