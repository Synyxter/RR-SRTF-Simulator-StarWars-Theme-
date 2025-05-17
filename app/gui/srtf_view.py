import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import traceback # Para imprimir trazas de error completas

# --- Configuración de Rutas ---
try:
    CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
    GUI_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
    APP_MODULE_DIR = os.path.dirname(GUI_DIR)
    ASSETS_DIR = os.path.join(APP_MODULE_DIR, "assets")
    if not os.path.isdir(ASSETS_DIR):
        PROJECT_ROOT_DIR = os.path.dirname(APP_MODULE_DIR)
        ASSETS_DIR = os.path.join(PROJECT_ROOT_DIR, "assets")
    if not os.path.isdir(ASSETS_DIR):
        ASSETS_DIR = "assets"
except NameError:
    ASSETS_DIR = "assets"
    print("Advertencia: __file__ no definido. Usando rutas relativas simples para assets.")

BG_IMAGE_PATH = os.path.join(ASSETS_DIR, "backgroundstarwars2.jpg").replace("\\", "/") # Cambiado para tematica SRTF si se desea
ICON_VOLVER_PATH = os.path.join(ASSETS_DIR, "icon_volver.png").replace("\\", "/") # Icono podría ser temático

print(f"INFO: Ruta calculada para ASSETS_DIR: {os.path.abspath(ASSETS_DIR)}")
print(f"INFO: Ruta para BG_IMAGE_PATH: {BG_IMAGE_PATH}") # Idealmente, crear un nuevo fondo o usar uno genérico
print(f"INFO: Ruta para ICON_VOLVER_PATH: {ICON_VOLVER_PATH}")
# --- Fin Configuración de Rutas ---

# Colores y Constantes
COLOR_VERDE = "#32CD32"  # Lime Green
COLOR_AMARILLO = "#FFFF00"
COLOR_VERDE_OSCURO = "#006400" # Dark Green
COLOR_AMARILLO_OSCURO = "#B8860B" # DarkGoldenrod
COLOR_FONDO_PRINCIPAL = "#000000"
COLOR_FONDO_SECUNDARIO = "#1A1A1A" # Gris oscuro para contraste
COLOR_FONDO_GANTT = "#000000"
COLOR_TEXTO_BLANCO = "#FFFFFF"
MIN_PROCESOS = 1 # SRTF puede funcionar con 1 proceso
MAX_PROCESOS = 20


class ResultsView(ctk.CTkFrame):
    def __init__(self, master, datos_resultado_lista, callback_to_srtf_view, bg_image_path_param=BG_IMAGE_PATH):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        
        self.datos_resultado_lista = datos_resultado_lista if datos_resultado_lista is not None else []
        self.callback_to_srtf_view = callback_to_srtf_view
        self.bg_image_path = bg_image_path_param
        self.background_img_obj = None
        self.background_label = None
        self.canvas_widget = None

        self._load_background()

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self._crear_titulo_resultados(self.content_frame)
        self._crear_boton_volver(self.content_frame)

        display_area = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        display_area.pack(fill="both", expand=True, pady=(80, 10)) # Espacio para título y botón

        self._mostrar_tabla_resultados(display_area)
        self._mostrar_gantt(display_area)

        self.pack(fill="both", expand=True)
        if self.background_label:
            self.background_label.lower()

    def _get_master_dimensions(self):
        try:
            width = self.master_window.winfo_width(); height = self.master_window.winfo_height()
            if width <= 1 or height <= 1: # Ventana aún no dibujada completamente
                geom = self.master_window.geometry(); size_part = geom.split('+')[0]
                width, height = map(int, size_part.split('x'))
            if width <= 1 or height <= 1: return 1280, 720 # Default
            return width, height
        except Exception: return 1280, 720

    def _load_background(self):
        # Usar una imagen de fondo genérica o específica para SRTF si existe
        # Para este ejemplo, se reusa la lógica pero el path podría cambiar
        pil_compatible_path = self.bg_image_path # BG_IMAGE_PATH ya está formateado
        abs_path_check = os.path.abspath(pil_compatible_path)

        if not os.path.exists(abs_path_check):
            print(f"ERROR ResultsView: Fondo NO ENCONTRADO en '{abs_path_check}'")
            # Fallback a un color de fondo si la imagen no carga
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None
            return

        try:
            imagen_pil = Image.open(abs_path_check)
            master_width, master_height = self._get_master_dimensions()
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(master_width, master_height))
            
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else:
                self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"ERROR ResultsView: Excepción al cargar fondo '{abs_path_check}': {e}"); traceback.print_exc()
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO) # Fallback
            if self.background_label: self.background_label.destroy(); self.background_label = None


    def _crear_titulo_resultados(self, parent):
        titulo = ctk.CTkLabel(parent, text="Simulación SRTF", font=("Star Jedi", 26), text_color=COLOR_AMARILLO) # O un tipo de letra diferente
        titulo.pack(pady=15)

    def _crear_boton_volver(self, parent):
        icono = None
        try:
            # Usar ICON_VOLVER_PATH que ya está configurado y chequeado al inicio
            if os.path.exists(ICON_VOLVER_PATH):
                icono_img = Image.open(ICON_VOLVER_PATH)
                icono = ctk.CTkImage(light_image=icono_img, size=(20, 20))
            else: print(f"ERROR ResultsView: Icono Volver NO ENCONTRADO en '{ICON_VOLVER_PATH}'")
        except Exception as e: print(f"ERROR ResultsView: Excepción al cargar icono volver: {e}")
        
        ctk.CTkButton(parent, image=icono, text=" Volver a Ingresar Datos", command=self.callback_to_srtf_view,
                      fg_color="transparent", border_color=COLOR_VERDE, border_width=2, text_color=COLOR_VERDE,
                      hover_color=COLOR_AMARILLO_OSCURO, font=ctk.CTkFont(family="space age", size=12) # O un tipo de letra diferente
        ).place(x=15, y=15)


    def _mostrar_tabla_resultados(self, parent_frame):
        tabla_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=10)
        tabla_frame.pack(pady=10, padx=10, fill="x")

        headers = ["Proceso", "Llegada", "CPU Total", "Comienzos Seg.", "Fines Seg.", "Espera Total", "Turnaround Total"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(tabla_frame, text=h, text_color=COLOR_VERDE, font=("Arial", 13, "bold")).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        if not self.datos_resultado_lista:
            ctk.CTkLabel(tabla_frame, text="No hay datos de simulación para mostrar.", text_color=COLOR_AMARILLO).grid(row=1, column=0, columnspan=len(headers), pady=10)
            return

        procesos_consolidados = {}
        for segmento in self.datos_resultado_lista:
            nombre_proc = segmento.get("proceso", "N/A_Proc")
            if nombre_proc not in procesos_consolidados:
                procesos_consolidados[nombre_proc] = {
                    "llegada": segmento.get("llegada", "-"),
                    "cpu_total": segmento.get("cpu_original", "-"), # Usar cpu_original
                    "comienzos_segmento": [],
                    "fines_segmento": [],
                    "espera_total": segmento.get("espera_final", "-"),
                    "turnaround_total": segmento.get("turnaround_final", "-")
                }
            
            procesos_consolidados[nombre_proc]["comienzos_segmento"].append(str(segmento.get("comienzo", "")))
            procesos_consolidados[nombre_proc]["fines_segmento"].append(str(segmento.get("final", "")))
            
            # Asegurar que los valores finales de espera y turnaround se tomen correctamente
            # El controlador SRTF debería ponerlos en cada segmento o al menos en el último relevante
            # Esta lógica asume que el último segmento procesado para un proceso en datos_resultado_lista
            # o cualquier segmento con valores finales válidos puede actualizar estos.
            current_espera = segmento.get("espera_final", procesos_consolidados[nombre_proc]["espera_total"])
            current_turnaround = segmento.get("turnaround_final", procesos_consolidados[nombre_proc]["turnaround_total"])

            if current_espera not in ["Calc...", "En Proceso", "No Term."]:
                 procesos_consolidados[nombre_proc]["espera_total"] = current_espera
            if current_turnaround not in ["Calc...", "En Proceso", "No Term."]:
                 procesos_consolidados[nombre_proc]["turnaround_total"] = current_turnaround


        nombres_procesos_ordenados = sorted(procesos_consolidados.keys())
        row_idx = 1
        for nombre_proc in nombres_procesos_ordenados:
            data = procesos_consolidados[nombre_proc]
            
            comienzos_str = ", ".join(data["comienzos_segmento"])
            fines_str = ", ".join(data["fines_segmento"])

            fila_a_mostrar = [
                nombre_proc,
                data["llegada"],
                data["cpu_total"],
                comienzos_str,
                fines_str,
                data["espera_total"],
                data["turnaround_total"]
            ]
            for col_idx, val in enumerate(fila_a_mostrar):
                ctk.CTkLabel(tabla_frame, text=str(val), text_color=COLOR_AMARILLO, font=("Arial", 12)).grid(row=row_idx, column=col_idx, padx=10, pady=6, sticky="w")
            row_idx += 1
        
        for i in range(len(headers)):
            tabla_frame.grid_columnconfigure(i, weight=1)

    def _mostrar_gantt(self, parent_frame):
        gantt_container_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_GANTT, corner_radius=10)
        gantt_container_frame.pack(pady=20, padx=10, fill="both", expand=True)
        
        gantt_items = self.datos_resultado_lista if self.datos_resultado_lista is not None else []
        num_unique_processes = len(set(item.get('proceso') for item in gantt_items if item and item.get('proceso')))
        
        fig_height = max(4, num_unique_processes * 0.6 + 1)
        fig, ax = plt.subplots(figsize=(12, fig_height))
        fig.patch.set_facecolor(COLOR_FONDO_GANTT); ax.set_facecolor(COLOR_FONDO_GANTT)
        
        # Paleta de colores para Gantt (Verde/Amarillo y complementarios)
        colores_gantt = {
            "A": "#32CD32", "B": "#ADFF2F", "C": "#9ACD32", "D": "#FFFF00", "E": "#F0E68C", 
            "F": "#BDB76B", "G": "#90EE90", "H": "#98FB98", "I": "#8FBC8F", "J": "#FFD700",
            "K": "#00FF00", "L": "#7FFF00", "M": "#7CFC00", "N": "#FFFFE0", "O": "#3CB371",
            "P": "#2E8B57", "Q": "#808000", "R": "#556B2F", "S": "#6B8E23", "T": "#DAA520"
        }
        default_color = "#BEBEBE"; max_final_time = 0
        
        if isinstance(gantt_items, list) and gantt_items and isinstance(gantt_items[0], dict):
            if not ('comienzo' in gantt_items[0] and 'final' in gantt_items[0]):
                ax.text(0.5, 0.5, "Datos incompletos para Gantt.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)
            else:
                y_labels_unique = sorted(list(set(item.get("proceso", f"P_indef_{i}") for i, item in enumerate(gantt_items) if item)))
                y_pos = {label: i for i, label in enumerate(y_labels_unique)}

                for item_idx, item in enumerate(gantt_items):
                    nombre = item.get("proceso", f"P_indef_{item_idx}")
                    if nombre not in y_pos: y_pos[nombre] = len(y_labels_unique); y_labels_unique.append(nombre) # Asegurar que todos tengan y_pos
                    
                    comienzo, final_val = item.get("comienzo", 0), item.get("final", item.get("comienzo", 0))
                    duracion = max(0, final_val - comienzo) # Evitar duración negativa
                    
                    color_proceso = colores_gantt.get(nombre, default_color)
                    ax.barh(y_pos[nombre], duracion, left=comienzo, color=color_proceso, edgecolor=COLOR_FONDO_GANTT, height=0.6)
                    
                    if duracion > 0.3: # Solo mostrar texto si la barra es suficientemente ancha
                        # Determinar color de texto para contraste
                        try:
                            # Convertir hex a RGB y calcular luminancia para decidir color de texto
                            hex_color = color_proceso.lstrip('#')
                            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                            text_color_in_bar = COLOR_FONDO_GANTT if luminance > 0.5 else COLOR_TEXTO_BLANCO
                        except: # Fallback
                            text_color_in_bar = COLOR_FONDO_GANTT if color_proceso in [COLOR_AMARILLO, "#ADFF2F", "#F0E68C", "#FFFF00", "#FFFFE0", "#90EE90", "#98FB98"] else COLOR_TEXTO_BLANCO

                        ax.text(comienzo + duracion / 2, y_pos[nombre], nombre, ha='center', va='center', color=text_color_in_bar, fontsize=9, fontweight='bold')
                    
                    if comienzo + duracion > max_final_time: max_final_time = comienzo + duracion
                
                ax.set_yticks(list(y_pos.values())); ax.set_yticklabels(list(y_pos.keys()), color=COLOR_AMARILLO)
        else:
            ax.text(0.5, 0.5, "No hay datos para Gantt.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)

        ax.set_xlabel("Tiempo", color=COLOR_AMARILLO, fontsize=12); ax.set_ylabel("Procesos", color=COLOR_AMARILLO, fontsize=12)
        ax.set_title("Diagrama de Gantt - SRTF", color=COLOR_AMARILLO, fontsize=16, fontweight='bold')
        ax.grid(True, axis='x', linestyle=':', alpha=0.7, color=COLOR_AMARILLO_OSCURO)
        ax.tick_params(axis='x', colors=COLOR_AMARILLO); ax.tick_params(axis='y', colors=COLOR_AMARILLO)
        for spine_pos in ['bottom', 'top', 'left', 'right']: ax.spines[spine_pos].set_color(COLOR_AMARILLO_OSCURO)
        
        if max_final_time > 0:
            tick_step = np.ceil(max_final_time / 15) if max_final_time > 15 else 1.0; tick_step = max(1, int(tick_step))
            ax.set_xticks(np.arange(0, np.ceil(max_final_time / tick_step) * tick_step + tick_step, tick_step))
            ax.set_xlim(left=-0.5, right=max_final_time + 0.5)
        else: ax.set_xticks(np.arange(0, 11, 1)); ax.set_xlim(left=-0.5, right=10.5)
        
        plt.tight_layout()
        if self.canvas_widget: self.canvas_widget.get_tk_widget().destroy()
        self.canvas_widget = FigureCanvasTkAgg(fig, master=gantt_container_frame)
        self.canvas_widget.draw(); self.canvas_widget.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=5, pady=5)
        plt.close(fig)

    def destroy(self):
        if self.canvas_widget: self.canvas_widget.get_tk_widget().destroy(); self.canvas_widget = None
        if self.background_label: self.background_label.destroy(); self.background_label = None
        super().destroy()


class SRTFView(ctk.CTkFrame):
    def __init__(self, master, volver_callback):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        self.volver_callback = volver_callback
        self.proceso_entries = []
        self.cantidad_entry = None
        # self.quantum_entry = None # SRTF no usa Quantum
        self.background_img_obj = None
        self.background_label = None
        self.entrada_procesos_scrollable_frame = None
        self.inner_entrada_frame = None
        self.results_view_instance = None
        self.main_content_frame = None
        self.btn_calcular = None

        self._cargar_fondo()

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._load_titulo(self.main_content_frame)
        self._crear_boton_volver_main(self.main_content_frame)
        self._crear_formulario_inicial(self.main_content_frame)

        self.pack(fill="both", expand=True)
        if self.background_label:
            self.background_label.lower()

    def _get_master_dimensions(self):
        try:
            width = self.master_window.winfo_width(); height = self.master_window.winfo_height()
            if width <= 1 or height <= 1:
                geom = self.master_window.geometry(); size_part = geom.split('+')[0]
                width, height = map(int, size_part.split('x'))
            if width <= 1 or height <= 1: return 1280, 720
            return width, height
        except Exception: return 1280, 720

    def _cargar_fondo(self):
        pil_compatible_path = BG_IMAGE_PATH # Ya formateado
        abs_path_check = os.path.abspath(pil_compatible_path)
        if not os.path.exists(abs_path_check):
            print(f"ERROR SRTFView: Fondo NO ENCONTRADO en '{abs_path_check}'")
            if self.background_label: self.background_label.destroy()
            self.background_label = ctk.CTkLabel(self, text="Fondo no encontrado", fg_color=COLOR_VERDE_OSCURO, text_color=COLOR_AMARILLO, font=("Arial", 16))
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            return
        try:
            imagen_pil = Image.open(abs_path_check)
            master_width, master_height = self._get_master_dimensions()
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(master_width, master_height))
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else: self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"ERROR SRTFView: Excepción al cargar fondo '{abs_path_check}': {e}"); traceback.print_exc()
            if self.background_label: self.background_label.destroy()
            self.background_label = ctk.CTkLabel(self, text="Error al cargar fondo", fg_color=COLOR_VERDE_OSCURO, text_color=COLOR_AMARILLO, font=("Arial", 16))
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def _load_titulo(self, parent):
        # Usar una fuente temática si se tiene, o una estándar
        titulo = ctk.CTkLabel(parent, text="Algoritmo SRTF", font=("Star Jedi", 32), text_color=COLOR_VERDE) # O "Arial" u otra
        titulo.pack(pady=(10, 20))

    def _crear_boton_volver_main(self, parent):
        icono = None
        try:
            if os.path.exists(ICON_VOLVER_PATH):
                icono_img = Image.open(ICON_VOLVER_PATH)
                icono = ctk.CTkImage(light_image=icono_img, size=(30, 30))
            else: print(f"ERROR SRTFView: Icono Volver NO ENCONTRADO en '{ICON_VOLVER_PATH}'")
        except Exception as e: print(f"ERROR SRTFView: Excepción al cargar icono volver: {e}")
        
        ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback,
                      fg_color="transparent", border_color=COLOR_VERDE, border_width=2,
                      text_color=COLOR_VERDE, hover_color=COLOR_AMARILLO_OSCURO,
                      font=ctk.CTkFont(family="space age", size=14) # O "Arial"
        ).place(x=10, y=10)

    def _crear_formulario_inicial(self, parent):
        self.formulario_inicial_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.formulario_inicial_frame.pack(pady=10, anchor="center")
        
        ctk.CTkLabel(self.formulario_inicial_frame, text=f"Cantidad de procesos ({MIN_PROCESOS}-{MAX_PROCESOS}):", font=("space age", 16), text_color=COLOR_AMARILLO).pack(pady=5) # O "Arial"
        self.cantidad_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.cantidad_entry.pack(pady=5)
        
        # SRTF no necesita Quantum
        # ctk.CTkLabel(self.formulario_inicial_frame, text="Quantum (1-4):", font=("space age", 16), text_color=COLOR_AMARILLO).pack(pady=(10,5))
        # self.quantum_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        # self.quantum_entry.pack(pady=5)
        
        ctk.CTkButton(self.formulario_inicial_frame, text="Generar Tabla de Entradas", command=self._generar_tabla_inputs,
                      border_width=2, fg_color="transparent", font=("space age", 15, "bold"), # O "Arial"
                      border_color=COLOR_VERDE, text_color=COLOR_AMARILLO, hover_color=COLOR_VERDE_OSCURO
        ).pack(pady=(15,10))
        
        self.btn_calcular = ctk.CTkButton(self.formulario_inicial_frame, text="Calcular SRTF", command=self._calcular_srtf_and_show_results,
                                           border_width=2, fg_color="transparent", border_color=COLOR_AMARILLO, text_color=COLOR_VERDE,
                                           font=("space age", 15, "bold"), hover_color=COLOR_AMARILLO_OSCURO, state="disabled" # O "Arial"
        )
        self.btn_calcular.pack(pady=5)

    def _generar_tabla_inputs(self):
        try:
            cantidad_str = self.cantidad_entry.get()
            if not cantidad_str: print("Error: Cantidad no puede estar vacía."); return # Validar
            cantidad = int(cantidad_str)
            if not (MIN_PROCESOS <= cantidad <= MAX_PROCESOS): print(f"Error: Cantidad entre {MIN_PROCESOS} y {MAX_PROCESOS}."); return
        except ValueError: print("Error: Cantidad debe ser un entero."); return

        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        
        dynamic_height = min(cantidad * 55 + 70, 450) 
        self.entrada_procesos_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame,
            label_text="Ingrese los Datos de los Procesos:", label_font=("space age", 14), # O "Arial"
            label_text_color=COLOR_AMARILLO, fg_color=COLOR_FONDO_SECUNDARIO, 
            corner_radius=10, height=dynamic_height
        )
        self.entrada_procesos_scrollable_frame.pack(pady=10, padx=20, fill="x", expand=False)
        self.inner_entrada_frame = ctk.CTkFrame(self.entrada_procesos_scrollable_frame, fg_color="transparent")
        self.inner_entrada_frame.pack(fill="x", expand=True)

        self.proceso_entries = []
        header_texts = ["Proceso", "Tiempo de Llegada", "Ráfaga de CPU"]
        for i, h_text in enumerate(header_texts):
            ctk.CTkLabel(self.inner_entrada_frame, text=h_text, font=("Arial", 16, "bold"), text_color=COLOR_AMARILLO).grid(row=0, column=i, padx=15, pady=10, sticky="nsew")
        
        for i in range(cantidad):
            proceso_char = chr(65 + i)
            ctk.CTkLabel(self.inner_entrada_frame, text=proceso_char, font=("Arial", 14, "bold"), text_color=COLOR_VERDE).grid(row=i + 1, column=0, padx=15, pady=8)
            e_llegada = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_llegada.grid(row=i + 1, column=1, padx=15, pady=8)
            e_cpu = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_cpu.grid(row=i + 1, column=2, padx=15, pady=8)
            self.proceso_entries.append((proceso_char, e_llegada, e_cpu))
        
        for col in range(3): self.inner_entrada_frame.grid_columnconfigure(col, weight=1)
        if self.btn_calcular: self.btn_calcular.configure(state="normal")

    def _calcular_srtf_and_show_results(self):
        procesos_data_list = []
        try:
            for nombre, llegada_e, cpu_e in self.proceso_entries:
                llegada, duracion = int(llegada_e.get()), int(cpu_e.get())
                if llegada < 0 or duracion <= 0: print("Error: Llegada debe ser >= 0 y Ráfaga de CPU debe ser > 0."); return
                procesos_data_list.append({"nombre": nombre, "llegada": llegada, "duracion_original": duracion, "restante": duracion})
        except ValueError: print("Error: Todos los datos de llegada y CPU deben ser enteros."); return
        if not procesos_data_list: print("Error: No hay procesos para simular."); return
        
        try:
            # Asegurar que el controlador correcto es llamado
            global SRTFController
            SRTFController = SRTFController if 'SRTFController' in globals() and SRTFController else MockSRTFController
            resultado = SRTFController.simular_srtf(procesos_data_list) # No necesita quantum
            if resultado is None: 
                print("Error: La simulación SRTF no devolvió resultados.")
                return
        except Exception as e: print(f"Error en simulación SRTF: {e}"); traceback.print_exc(); return
        
        self.pack_forget() # Oculta la vista actual (SRTFView)
        if self.results_view_instance: self.results_view_instance.destroy() # Destruye vista de resultados anterior si existe
        self.results_view_instance = ResultsView(self.master_window, resultado, self._return_to_srtf_view)

    def _return_to_srtf_view(self):
        if self.results_view_instance: self.results_view_instance.destroy(); self.results_view_instance = None
        self._cargar_fondo() # Recargar fondo por si acaso
        if self.background_label: self.background_label.lower()
        self.pack(fill="both", expand=True) # Vuelve a mostrar SRTFView
        
        # Limpiar entradas para nueva simulación
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy(); self.entrada_procesos_scrollable_frame = None; self.inner_entrada_frame = None
        if self.btn_calcular: self.btn_calcular.configure(state="disabled")
        if self.cantidad_entry: self.cantidad_entry.delete(0, 'end')
        # if self.quantum_entry: self.quantum_entry.delete(0, 'end') # No hay quantum_entry
        self.proceso_entries = []

    def destroy(self):
        if self.results_view_instance: self.results_view_instance.destroy()
        if self.background_label: self.background_label.destroy()
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        super().destroy()


class MockSRTFController:
    @staticmethod
    def simular_srtf(procesos_iniciales):
        if not procesos_iniciales:
            return []

        # Crear copias profundas para no modificar la lista original y añadir campos necesarios
        procesos = []
        for i, p_orig in enumerate(procesos_iniciales):
            p_copy = p_orig.copy()
            p_copy['id'] = p_orig.get('nombre', f"P{i}") # Asegurar 'nombre' es 'id'
            p_copy['restante'] = p_orig['duracion_original']
            p_copy['tiempo_finalizacion'] = 0
            p_copy['tiempo_espera'] = 0
            p_copy['turnaround'] = 0
            p_copy['ejecutado_al_menos_una_vez'] = False # Para registrar primer inicio
            procesos.append(p_copy)

        tiempo_actual = 0
        procesos_completados = 0
        gantt_chart_segments = []
        
        # Mapa para estadísticas finales por proceso
        stats_finales_procesos = {p['id']: {} for p in procesos}


        while procesos_completados < len(procesos):
            # Filtrar procesos listos: aquellos que han llegado y aún tienen tiempo restante
            procesos_listos = [p for p in procesos if p['llegada'] <= tiempo_actual and p['restante'] > 0]

            if not procesos_listos:
                # Si no hay procesos listos, avanzar el tiempo hasta la llegada del próximo proceso
                procesos_pendientes = [p for p in procesos if p['restante'] > 0]
                if not procesos_pendientes: # Todos completados
                    break
                tiempo_actual = min(p['llegada'] for p in procesos_pendientes if p['llegada'] > tiempo_actual)
                continue

            # Seleccionar el proceso con el menor tiempo restante
            procesos_listos.sort(key=lambda p: (p['restante'], p['llegada'])) # Desempate por llegada
            proceso_actual = procesos_listos[0]

            tiempo_inicio_segmento = tiempo_actual
            
            # Ejecutar el proceso por 1 unidad de tiempo o hasta que llegue otro proceso 
            # con menor tiempo restante, o hasta que termine el proceso actual.
            
            tiempo_para_siguiente_llegada = float('inf')
            for p in procesos:
                if p['llegada'] > tiempo_actual and p['restante'] > 0: # Proceso aún no llegado pero pendiente
                    tiempo_para_siguiente_llegada = min(tiempo_para_siguiente_llegada, p['llegada'])
            
            # Tiempo que puede correr este proceso antes de una posible preemoción por nueva llegada
            # o hasta que termine.
            tiempo_de_ejecucion_max_sin_nueva_llegada = proceso_actual['restante']
            if tiempo_para_siguiente_llegada != float('inf'):
                 tiempo_hasta_proxima_llegada_relevante = tiempo_para_siguiente_llegada - tiempo_actual
                 tiempo_de_ejecucion_max_sin_nueva_llegada = min(proceso_actual['restante'], tiempo_hasta_proxima_llegada_relevante)


            # Ejecutar por una unidad de tiempo para revaluar (simplificación común para SRTF)
            # O ejecutar hasta el próximo evento (terminación o llegada que pueda causar preemción)
            # Optamos por ejecutar la mínima unidad posible para mantener la lógica de preemción precisa
            # o hasta el tiempo de ejecución determinado arriba.
            
            # Para una simulación más granular y correcta de SRTF en cada instante de tiempo:
            # Se ejecuta por 1 unidad de tiempo, o hasta que termine, o hasta que llegue otro.
            # El tiempo de ejecución en este slot será 1, a menos que el proceso termine antes,
            # o que el próximo evento de llegada sea en menos de 1.

            tiempo_ejecucion_este_slot = 1 # Ejecutar por defecto 1 unidad de tiempo

            # Si el proceso termina en menos de 1 unidad de tiempo
            if proceso_actual['restante'] < tiempo_ejecucion_este_slot:
                tiempo_ejecucion_este_slot = proceso_actual['restante']

            # Si un nuevo proceso llega antes de que esta unidad de tiempo termine
            # y ese nuevo proceso podría ser más corto
            siguiente_evento_llegada = float('inf')
            for p_futuro in procesos:
                if p_futuro['llegada'] > tiempo_actual and p_futuro['llegada'] < tiempo_actual + tiempo_ejecucion_este_slot:
                    siguiente_evento_llegada = min(siguiente_evento_llegada, p_futuro['llegada'])
            
            if siguiente_evento_llegada != float('inf'):
                tiempo_ejecucion_este_slot = min(tiempo_ejecucion_este_slot, siguiente_evento_llegada - tiempo_actual)
            
            tiempo_ejecucion_este_slot = max(tiempo_ejecucion_este_slot, 0) # Asegurar no negativo si hay problemas de lógica

            if tiempo_ejecucion_este_slot == 0 and proceso_actual['restante'] > 0: # Si tiempo_actual coincide con una llegada, y el slot es 0, forzar avance mínimo si no hay otro proceso más corto.
                 # Esto puede pasar si tiempo_actual == siguiente_evento_llegada. Reevaluamos en el siguiente ciclo.
                 # Para evitar bucles infinitos si algo va mal, se puede forzar un avance si no hay procesos listos.
                 # La lógica de "if not procesos_listos:" maneja el avance si nada se ejecuta.
                 # Si el slot es 0 pero el proceso tiene restante, es que debe ceder inmediatamente.
                 # En este caso, el tiempo_actual no avanza por este proceso.
                 pass # Se re-evaluará en el siguiente ciclo de while.


            if tiempo_ejecucion_este_slot > 0:
                proceso_actual['restante'] -= tiempo_ejecucion_este_slot
                tiempo_actual += tiempo_ejecucion_este_slot
                tiempo_fin_segmento = tiempo_actual

                gantt_chart_segments.append({
                    'proceso': proceso_actual['id'],
                    'llegada': proceso_actual['llegada'], # Llegada original del proceso
                    'cpu_original': proceso_actual['duracion_original'], # CPU total original
                    'comienzo': tiempo_inicio_segmento,
                    'final': tiempo_fin_segmento,
                    'espera_final': "Calc...", # Se calculará al final
                    'turnaround_final': "Calc..." # Se calculará al final
                })

                if proceso_actual['restante'] <= 0:
                    procesos_completados += 1
                    proceso_actual['tiempo_finalizacion'] = tiempo_actual
                    proceso_actual['turnaround'] = proceso_actual['tiempo_finalizacion'] - proceso_actual['llegada']
                    proceso_actual['tiempo_espera'] = proceso_actual['turnaround'] - proceso_actual['duracion_original']
                    
                    stats_finales_procesos[proceso_actual['id']]['espera'] = proceso_actual['tiempo_espera']
                    stats_finales_procesos[proceso_actual['id']]['turnaround'] = proceso_actual['turnaround']
            
            # Si tiempo_ejecucion_este_slot fue 0, significa que tiempo_actual no cambió,
            # pero un nuevo proceso pudo haber llegado exactamente en tiempo_actual,
            # por lo que el bucle while se repetirá y se seleccionará el proceso correcto.

        # Actualizar 'espera_final' y 'turnaround_final' en todos los segmentos con los valores calculados
        for segment in gantt_chart_segments:
            nombre_proceso_segmento = segment['proceso']
            if nombre_proceso_segmento in stats_finales_procesos and stats_finales_procesos[nombre_proceso_segmento]:
                segment['espera_final'] = stats_finales_procesos[nombre_proceso_segmento].get('espera', 'Error E')
                segment['turnaround_final'] = stats_finales_procesos[nombre_proceso_segmento].get('turnaround', 'Error T')
            else:
                # Esto no debería ocurrir si todos los procesos se completan
                segment['espera_final'] = "No Term."
                segment['turnaround_final'] = "No Term."
        
        return gantt_chart_segments


if __name__ == '__main__':
    # Reconfigurar rutas si es necesario para el contexto de __main__
    # Esto es similar a lo que ya tenías, ajustado ligeramente.
    try:
        # Si __file__ está definido (ejecutando el script directamente)
        CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
        # Asumiendo una estructura: ProjectRoot/app/gui_module.py y ProjectRoot/app/assets/
        # Si gui_module.py está en ProjectRoot/app/ (o similar)
        APP_DIR_FROM_SCRIPT = os.path.dirname(CURRENT_SCRIPT_PATH) # Directorio del script actual
        
        # Intento 1: assets está en el mismo directorio que el script (menos común para proyectos estructurados)
        ASSETS_DIR_MAIN = os.path.join(APP_DIR_FROM_SCRIPT, "assets")

        if not os.path.isdir(ASSETS_DIR_MAIN):
            # Intento 2: assets está un nivel arriba del directorio del script (ProjectRoot/assets, si script está en ProjectRoot/src)
            PROJECT_ROOT_CANDIDATE1 = os.path.dirname(APP_DIR_FROM_SCRIPT)
            ASSETS_DIR_MAIN = os.path.join(PROJECT_ROOT_CANDIDATE1, "assets")

        if not os.path.isdir(ASSETS_DIR_MAIN):
             # Intento 3: Estructura app/assets donde app es hermano de este script o un subdirectorio conocido
             # Esto es más complejo de adivinar sin conocer la estructura exacta.
             # El código original usaba APP_MODULE_DIR = os.path.dirname(GUI_DIR)
             # Si este script es el "main", GUI_DIR sería el dir del script.
             GUI_DIR_MAIN = os.path.dirname(CURRENT_SCRIPT_PATH)
             APP_MODULE_DIR_MAIN = os.path.dirname(GUI_DIR_MAIN) # Sube un nivel
             ASSETS_DIR_MAIN = os.path.join(APP_MODULE_DIR_MAIN, "assets")


        if not os.path.isdir(ASSETS_DIR_MAIN): # Fallback muy genérico
            ASSETS_DIR_MAIN = "assets" # Asume que 'assets' está en el CWD de ejecución
        
        # Actualizar las variables globales BG_IMAGE_PATH y ICON_VOLVER_PATH
        # Usar nombres de archivo genéricos o específicos para SRTF si existen
        BG_IMAGE_PATH = os.path.join(ASSETS_DIR_MAIN, "backgroundstarwars2.jpg").replace("\\", "/")
        if not os.path.exists(BG_IMAGE_PATH): # Fallback a la imagen original si la nueva no existe
            BG_IMAGE_PATH = os.path.join(ASSETS_DIR_MAIN, "backgroundstarwars.jpg").replace("\\", "/")

        ICON_VOLVER_PATH = os.path.join(ASSETS_DIR_MAIN, "icon_volver.png").replace("\\", "/")
        if not os.path.exists(ICON_VOLVER_PATH): # Fallback al icono original
            ICON_VOLVER_PATH = os.path.join(ASSETS_DIR_MAIN, "icon_volver.png").replace("\\", "/")

        print(f"DEBUG (__main__): ASSETS_DIR_MAIN calculado como: {os.path.abspath(ASSETS_DIR_MAIN)}")
        print(f"DEBUG (__main__): BG_IMAGE_PATH seteado a: {BG_IMAGE_PATH}")
        print(f"DEBUG (__main__): ICON_VOLVER_PATH seteado a: {ICON_VOLVER_PATH}")

    except NameError: 
        print("Advertencia (__main__): __file__ no definido. Las rutas de assets pueden ser incorrectas.")
        # Mantener los valores por defecto de ASSETS_DIR si __file__ no está definido
        BG_IMAGE_PATH = os.path.join(ASSETS_DIR, "backgroundstarwars2.jpg").replace("\\", "/")
        ICON_VOLVER_PATH = os.path.join(ASSETS_DIR, "icon_volver.png").replace("\\", "/")


    app = ctk.CTk()
    app.title("Simulador SRTF"); app.geometry("1280x720"); ctk.set_appearance_mode("dark")
    
    # Mock para la función de volver al menú principal, si tuvieras uno.
    def go_to_main_menu_mock():
        print("Volviendo al menú principal (simulado)")
        # Lógica para limpiar la ventana y mostrar el menú principal
        for widget in app.winfo_children(): widget.destroy()
        # Aquí instanciarías tu MainMenuView(app)
        # Por ahora, simplemente cerramos la app para este ejemplo.
        # main_menu = MainMenuView(app, show_srtf_view_callback_func) # Suponiendo que tienes un MainMenuView
        # main_menu.pack(fill="both", expand=True)
        app.quit() # O alguna otra acción

    # Instanciar y mostrar la vista SRTF
    # El callback 'volver_callback' en SRTFView podría llamar a go_to_main_menu_mock
    srtf_view = SRTFView(master=app, volver_callback=go_to_main_menu_mock)
    #srtf_view.pack(fill="both", expand=True) # SRTFView ya se empaqueta en su __init__

    app.mainloop()