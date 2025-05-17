import customtkinter as ctk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import traceback # Para imprimir trazas de error completas


class BaseView(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Cargar la imagen de fondo
        if not os.path.exists(BG_IMAGE_PATH):
            raise FileNotFoundError(f"No se encontró la imagen de fondo en: {BG_IMAGE_PATH}")

        bg_image_pil = Image.open(BG_IMAGE_PATH)

        # Ajustar la imagen al tamaño del master
        width = master.winfo_screenwidth()
        height = master.winfo_screenheight()
        bg_image_pil = bg_image_pil.resize((width, height))

        # Convertir a PhotoImage para tkinter
        self.bg_image = ImageTk.PhotoImage(bg_image_pil)

        # Crear un label para colocar como fondo
        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Asegurar que el frame pueda contener otros widgets por encima
        self.bg_label.lower()  # Envía el fondo al fondo de la pila de widgets
        
# --- Configuración de Rutas (como en la versión anterior, asegúrate que sea correcta para tu proyecto) ---
try:
    CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
    GUI_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
    APP_MODULE_DIR = os.path.dirname(GUI_DIR)
    # Asumiendo que 'assets' está dentro de 'app'
    ASSETS_DIR = os.path.join(APP_MODULE_DIR, "assets")
    if not os.path.isdir(ASSETS_DIR): # Fallback por si la estructura es diferente
        PROJECT_ROOT_DIR = os.path.dirname(APP_MODULE_DIR)
        ASSETS_DIR = os.path.join(PROJECT_ROOT_DIR, "assets")
    if not os.path.isdir(ASSETS_DIR): # Fallback muy genérico
        ASSETS_DIR = "assets"
except NameError:
    ASSETS_DIR = "assets"
    print("Advertencia: __file__ no definido. Usando rutas relativas simples para assets.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
BG_IMAGE_PATH = os.path.abspath(os.path.join(ASSETS_DIR, "backgroundstarwars.jpg"))


BG_IMAGE_PATH = os.path.join(ASSETS_DIR, "backgroundstarwars.jpg").replace("\\", "/")
ICON_VOLVER_PATH = os.path.join(ASSETS_DIR, "icon_volver.png").replace("\\", "/")

print(f"INFO: Ruta calculada para ASSETS_DIR: {os.path.abspath(ASSETS_DIR)}")
print(f"INFO: Ruta para BG_IMAGE_PATH: {BG_IMAGE_PATH}")
print(f"INFO: Ruta para ICON_VOLVER_PATH: {ICON_VOLVER_PATH}")
# --- Fin Configuración de Rutas ---

# Colores y Constantes (sin cambios)
COLOR_ROJO = "#FF0000"
COLOR_AMARILLO = "#FFFF00"
COLOR_ROJO_OSCURO = "#AA0000"
COLOR_AMARILLO_OSCURO = "#B8860B"
COLOR_FONDO_PRINCIPAL = "#000000"
COLOR_FONDO_SECUNDARIO = "#1A1A1A"
COLOR_FONDO_GANTT = "#000000"
COLOR_TEXTO_BLANCO = "#FFFFFF"
MIN_PROCESOS = 3
MAX_PROCESOS = 20


class ResultsView(ctk.CTkFrame):
    def __init__(self, master, datos_resultado_lista, callback_to_rr_view, bg_image_path_param=BG_IMAGE_PATH):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        
        # Asegurarse que datos_resultado_lista es una lista, incluso si viene vacía
        self.datos_resultado_lista = datos_resultado_lista if datos_resultado_lista is not None else []
        self.callback_to_rr_view = callback_to_rr_view
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
        display_area.pack(fill="both", expand=True, pady=(80, 10))

        self._mostrar_tabla_resultados(display_area) # Aquí aplicaremos los cambios
        self._mostrar_gantt(display_area)

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

    def _load_background(self):
        fondo_path = os.path.join("app", "assets", "backgroundstarwars.jpg")  
        fondo = Image.open(fondo_path)

        fondo_img = ctk.CTkImage(light_image=fondo, dark_image=fondo, size=(1000, 600))

        self.bg_label = ctk.CTkLabel(self, image=fondo_img, text="")
        self.bg_label.image = fondo_img
        self.bg_label.place(x=0, y=0)

    def _crear_titulo_resultados(self, parent):
        titulo = ctk.CTkLabel(parent, text="Simulación RR", font=("Star Jedi", 26), text_color=COLOR_AMARILLO)
        titulo.pack(pady=15)

    def _crear_boton_volver(self, parent):
        icono = None
        try:
            pil_compatible_path = ICON_VOLVER_PATH.replace("\\", "/")
            if os.path.exists(pil_compatible_path):
                icono_img = Image.open(pil_compatible_path)
                icono = ctk.CTkImage(light_image=icono_img, size=(20, 20))
            else: print(f"ERROR ResultsView: Icono Volver NO ENCONTRADO en '{pil_compatible_path}'")
        except Exception as e: print(f"ERROR ResultsView: Excepción al cargar icono volver: {e}")
        ctk.CTkButton(parent, image=icono, text=" Volver a Ingresar Datos", command=self.callback_to_rr_view,
            fg_color="transparent", border_color=COLOR_ROJO, border_width=2, text_color=COLOR_ROJO,
            hover_color=COLOR_AMARILLO_OSCURO, font=ctk.CTkFont(family="space age", size=12)
        ).place(x=15, y=15)


    def _mostrar_tabla_resultados(self, parent_frame):
        tabla_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=10)
        tabla_frame.pack(pady=10, padx=10, fill="x")

        headers = ["Proceso", "Llegada", "CPU Total", "Comienzos Seg.", "Fines Seg.", "Espera Total", "Turnaround Total"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(tabla_frame, text=h, text_color=COLOR_ROJO, font=("Arial", 13, "bold")).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        if not self.datos_resultado_lista:
            ctk.CTkLabel(tabla_frame, text="No hay datos de simulación para mostrar.", text_color=COLOR_AMARILLO).grid(row=1, column=0, columnspan=len(headers), pady=10)
            return

        # 1. Agrupar datos por proceso
        procesos_consolidados = {}
        for segmento in self.datos_resultado_lista:
            nombre_proc = segmento.get("proceso", "N/A_Proc")
            if nombre_proc not in procesos_consolidados:
                procesos_consolidados[nombre_proc] = {
                    "llegada": segmento.get("llegada", "-"),
                    "cpu_total": segmento.get("cpu", "-"), # Asumimos 'cpu' es la ráfaga total original
                    "comienzos_segmento": [],
                    "fines_segmento": [],
                    # Espera y Turnaround se toman del último segmento procesado para este proceso,
                    # asumiendo que el controlador los actualiza y el último tiene el valor final.
                    # O, si el controlador ya propaga los valores finales a todos los segmentos,
                    # tomar el primero es suficiente.
                    "espera_total": segmento.get("espera", "-"),
                    "turnaround_total": segmento.get("turnaround", "-")
                }
            
            procesos_consolidados[nombre_proc]["comienzos_segmento"].append(str(segmento.get("comienzo", "")))
            procesos_consolidados[nombre_proc]["fines_segmento"].append(str(segmento.get("final", "")))
            
            # Actualizar espera y turnaround con el valor del segmento actual, 
            # ya que el MockController los propaga.
            # Esto asegura que si un proceso tuvo segmentos marcados como "Calc..."
            # y luego uno final, se tome el final.
            current_espera = segmento.get("espera", "-")
            current_turnaround = segmento.get("turnaround", "-")
            if current_espera not in ["Calc...", "En Proceso", "No Term."]:
                 procesos_consolidados[nombre_proc]["espera_total"] = current_espera
            if current_turnaround not in ["Calc...", "En Proceso", "No Term."]:
                 procesos_consolidados[nombre_proc]["turnaround_total"] = current_turnaround


        # 2. Mostrar los datos consolidados
        nombres_procesos_ordenados = sorted(procesos_consolidados.keys())
        row_idx = 1
        for nombre_proc in nombres_procesos_ordenados:
            data = procesos_consolidados[nombre_proc]
            
            # Unir listas de comienzos y fines en cadenas separadas por comas
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
    # ***** FIN MÉTODO MODIFICADO *****

    def _mostrar_gantt(self, parent_frame): # Sin cambios, ya estaba bien según el usuario
        gantt_container_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_GANTT, corner_radius=10)
        gantt_container_frame.pack(pady=20, padx=10, fill="both", expand=True)
        
        # Asegurar que datos_resultado_lista no es None para evitar errores
        gantt_items = self.datos_resultado_lista if self.datos_resultado_lista is not None else []
        num_unique_processes = len(set(item.get('proceso') for item in gantt_items if item and item.get('proceso')))
        
        fig_height = max(4, num_unique_processes * 0.6 + 1) # Ajustar altura dinámicamente
        fig, ax = plt.subplots(figsize=(12, fig_height))
        fig.patch.set_facecolor(COLOR_FONDO_GANTT); ax.set_facecolor(COLOR_FONDO_GANTT)
        colores_gantt = {"A": "#FF0000", "B": "#FFFF00", "C": "#B22222", "D": "#FFD700", "E": "#DC143C", "F": "#F0E68C", "G": "#FF6347", "H": "#EEE8AA", "I": "#8B0000", "J": "#FFFACD", "K": "#FA8072", "L": "#FFFFE0", "M": "#CD5C5C", "N": "#FAFAD2", "O": "#E9967A", "P": "#FFEFD5", "Q": "#FFA07A", "R": "#FFF8DC", "S": "#FF7F50", "T": "#D2B48C"}
        default_color = "#BEBEBE"; max_final_time = 0
        
        if isinstance(gantt_items, list) and gantt_items and isinstance(gantt_items[0], dict):
            if not ('comienzo' in gantt_items[0] and 'final' in gantt_items[0]):
                ax.text(0.5, 0.5, "Datos incompletos.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)
            else:
                y_labels_unique = sorted(list(set(item.get("proceso", f"P_indef_{i}") for i, item in enumerate(gantt_items) if item)))
                y_pos = {label: i for i, label in enumerate(y_labels_unique)}
                for item_idx, item in enumerate(gantt_items):
                    nombre = item.get("proceso", f"P_indef_{item_idx}")
                    if nombre not in y_pos: y_pos[nombre] = len(y_labels_unique); y_labels_unique.append(nombre)
                    comienzo, final_val = item.get("comienzo", 0), item.get("final", item.get("comienzo", 0))
                    duracion = max(0, final_val - comienzo)
                    color_proceso = colores_gantt.get(nombre, default_color)
                    ax.barh(y_pos[nombre], duracion, left=comienzo, color=color_proceso, edgecolor=COLOR_FONDO_GANTT, height=0.6)
                    if duracion > 0.3:
                        text_color_in_bar = COLOR_FONDO_GANTT if color_proceso in [COLOR_AMARILLO, "#FFD700", "#F0E68C", "#EEE8AA", "#FFFACD", "#FFFFE0", "#FAFAD2", "#FFEFD5", "#FFF8DC"] else COLOR_TEXTO_BLANCO
                        ax.text(comienzo + duracion / 2, y_pos[nombre], nombre, ha='center', va='center', color=text_color_in_bar, fontsize=9, fontweight='bold')
                    if comienzo + duracion > max_final_time: max_final_time = comienzo + duracion
                ax.set_yticks(list(y_pos.values())); ax.set_yticklabels(list(y_pos.keys()), color=COLOR_AMARILLO)
        else:
            ax.text(0.5, 0.5, "No hay datos para Gantt.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)
        ax.set_xlabel("Tiempo", color=COLOR_AMARILLO, fontsize=12); ax.set_ylabel("Procesos", color=COLOR_AMARILLO, fontsize=12)
        ax.set_title("Diagrama de Gantt - Round Robin", color=COLOR_AMARILLO, fontsize=16, fontweight='bold')
        ax.grid(True, axis='x', linestyle=':', alpha=0.7, color=COLOR_AMARILLO_OSCURO)
        ax.tick_params(axis='x', colors=COLOR_AMARILLO); ax.tick_params(axis='y', colors=COLOR_AMARILLO)
        for spine_pos in ['bottom', 'top', 'left', 'right']: ax.spines[spine_pos].set_color(COLOR_AMARILLO_OSCURO)
        if max_final_time > 0:
            tick_step = np.ceil(max_final_time / 15) if max_final_time > 15 else 1.0; tick_step = max(1, tick_step)
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

# Clase RRView y MockRRController permanecen estructuralmente iguales a la versión anterior,
# ya que el cambio es solo en la presentación de resultados.
# Se incluyen aquí para completitud y con las correcciones de la última iteración.
class RRView(ctk.CTkFrame):
    def __init__(self, master, volver_callback):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        self.volver_callback = volver_callback
        self.proceso_entries = []
        self.cantidad_entry = None
        self.quantum_entry = None
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
        pil_compatible_path = BG_IMAGE_PATH.replace("\\", "/")
        abs_path_check = os.path.abspath(pil_compatible_path)
        if not os.path.exists(abs_path_check):
            print(f"ERROR RRView: Fondo NO ENCONTRADO en '{abs_path_check}'")
            if self.background_label: self.background_label.destroy()
            self.background_label = ctk.CTkLabel(self, text="Fondo no encontrado", fg_color=COLOR_ROJO_OSCURO, text_color=COLOR_AMARILLO, font=("Arial", 16))
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            return
        try:
            imagen_pil = Image.open(abs_path_check)
            master_width, master_height = self._get_master_dimensions()
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, size=(master_width, master_height))
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else: self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"ERROR RRView: Excepción al cargar fondo '{abs_path_check}': {e}"); traceback.print_exc()
            if self.background_label: self.background_label.destroy()
            self.background_label = ctk.CTkLabel(self, text="Error al cargar fondo", fg_color=COLOR_ROJO_OSCURO, text_color=COLOR_AMARILLO, font=("Arial", 16))
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

    def _load_titulo(self, parent):
        titulo = ctk.CTkLabel(parent, text="Algoritmo Round Robin", font=("Star Jedi", 32), text_color=COLOR_ROJO)
        titulo.pack(pady=(10, 20))

    def _crear_boton_volver_main(self, parent):
        icono = None
        try:
            pil_compatible_path = ICON_VOLVER_PATH.replace("\\", "/")
            if os.path.exists(pil_compatible_path):
                icono_img = Image.open(pil_compatible_path)
                icono = ctk.CTkImage(light_image=icono_img, size=(30, 30))
            else: print(f"ERROR RRView: Icono Volver NO ENCONTRADO en '{pil_compatible_path}'")
        except Exception as e: print(f"ERROR RRView: Excepción al cargar icono volver: {e}")
        ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback,
            fg_color="transparent", border_color=COLOR_ROJO, border_width=2,
            text_color=COLOR_ROJO, hover_color=COLOR_AMARILLO_OSCURO,
            font=ctk.CTkFont(family="space age", size=14)
        ).place(x=10, y=10)

    def _crear_formulario_inicial(self, parent):
        self.formulario_inicial_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.formulario_inicial_frame.pack(pady=10, anchor="center")
        ctk.CTkLabel(self.formulario_inicial_frame, text=f"Cantidad de procesos ({MIN_PROCESOS}-{MAX_PROCESOS}):", font=("space age", 16), text_color=COLOR_AMARILLO).pack(pady=5)
        self.cantidad_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.cantidad_entry.pack(pady=5)
        ctk.CTkLabel(self.formulario_inicial_frame, text="Quantum (1-4):", font=("space age", 16), text_color=COLOR_AMARILLO).pack(pady=(10,5))
        self.quantum_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.quantum_entry.pack(pady=5)
        ctk.CTkButton(self.formulario_inicial_frame, text="Generar Tabla de Entradas", command=self._generar_tabla_inputs,
            border_width=2, fg_color="transparent", font=("space age", 15, "bold"),
            border_color=COLOR_ROJO, text_color=COLOR_AMARILLO, hover_color=COLOR_ROJO_OSCURO
        ).pack(pady=(15,10))
        self.btn_calcular = ctk.CTkButton(self.formulario_inicial_frame, text="Calcular Round Robin", command=self._calcular_rr_and_show_results,
            border_width=2, fg_color="transparent", border_color=COLOR_AMARILLO, text_color=COLOR_ROJO,
            font=("space age", 15, "bold"), hover_color=COLOR_AMARILLO_OSCURO, state="disabled"
        )
        self.btn_calcular.pack(pady=5)

    def _generar_tabla_inputs(self):
        try:
            cantidad_str = self.cantidad_entry.get(); quantum_str = self.quantum_entry.get()
            if not cantidad_str or not quantum_str: print("Error: Cantidad y Quantum no pueden estar vacíos."); return
            cantidad = int(cantidad_str); quantum_val = int(quantum_str)
            if not (MIN_PROCESOS <= cantidad <= MAX_PROCESOS): print(f"Error: Cantidad entre {MIN_PROCESOS} y {MAX_PROCESOS}."); return
            if not (1 <= quantum_val <= 4): print("Error: Quantum entre 1 y 4."); return
        except ValueError: print("Error: Cantidad y Quantum deben ser enteros."); return

        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        
        dynamic_height = min(cantidad * 55 + 70, 450) 
        self.entrada_procesos_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame,
            label_text="Ingrese los Datos de los Procesos:", label_font=("space age", 14),
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
            ctk.CTkLabel(self.inner_entrada_frame, text=proceso_char, font=("Arial", 14, "bold"), text_color=COLOR_ROJO).grid(row=i + 1, column=0, padx=15, pady=8)
            e_llegada = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_llegada.grid(row=i + 1, column=1, padx=15, pady=8)
            e_cpu = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_cpu.grid(row=i + 1, column=2, padx=15, pady=8)
            self.proceso_entries.append((proceso_char, e_llegada, e_cpu))
        for col in range(3): self.inner_entrada_frame.grid_columnconfigure(col, weight=1)
        if self.btn_calcular: self.btn_calcular.configure(state="normal")

    def _calcular_rr_and_show_results(self):
        procesos_data_list = []
        try:
            for nombre, llegada_e, cpu_e in self.proceso_entries:
                llegada, duracion = int(llegada_e.get()), int(cpu_e.get())
                if llegada < 0 or duracion <= 0: print("Error: Llegada >= 0 y CPU > 0."); return
                procesos_data_list.append({"nombre": nombre, "llegada": llegada, "duracion": duracion, "duracion_original": duracion})
            quantum = int(self.quantum_entry.get())
            if not (1 <= quantum <= 4): print("Error: Quantum entre 1 y 4."); return
        except ValueError: print("Error: Todos los datos deben ser enteros."); return
        if not procesos_data_list: print("Error: No hay procesos."); return
        try:
            global RRController; RRController = RRController if 'RRController' in globals() and RRController else MockRRController
            resultado = RRController.simular_rr(procesos_data_list, quantum)
            if resultado is None: # El controlador podría devolver None en caso de error interno
                print("Error: La simulación no devolvió resultados.")
                return
        except Exception as e: print(f"Error en simulación: {e}"); traceback.print_exc(); return
        self.pack_forget()
        if self.results_view_instance: self.results_view_instance.destroy()
        self.results_view_instance = ResultsView(self.master_window, resultado, self._return_to_rr_view)

    def _return_to_rr_view(self):
        if self.results_view_instance: self.results_view_instance.destroy(); self.results_view_instance = None
        self._cargar_fondo()
        if self.background_label: self.background_label.lower()
        self.pack(fill="both", expand=True)
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy(); self.entrada_procesos_scrollable_frame = None; self.inner_entrada_frame = None
        if self.btn_calcular: self.btn_calcular.configure(state="disabled")
        if self.cantidad_entry: self.cantidad_entry.delete(0, 'end')
        if self.quantum_entry: self.quantum_entry.delete(0, 'end')
        self.proceso_entries = []

    def destroy(self):
        if self.results_view_instance: self.results_view_instance.destroy()
        if self.background_label: self.background_label.destroy()
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        super().destroy()

class MockRRController: 
    
    
    @staticmethod
    def simular_rr(procesos_iniciales, quantum):
        results_list_of_segments = []
        if not procesos_iniciales: return []
        procesos_para_simular = []
        for p_orig in procesos_iniciales:
            p_copy = p_orig.copy()
            p_copy['restante'] = p_orig['duracion']
            p_copy['tiempo_finalizacion'] = 0; p_copy['tiempo_espera_calculado'] = 0
            p_copy['primer_comienzo_ejecucion'] = -1; p_copy['tiempo_en_cpu_total'] = 0
            procesos_para_simular.append(p_copy)
        procesos_para_simular.sort(key=lambda p: p['llegada'])
        tiempo_actual = 0; cola_listos = []; idx_proceso_entrante = 0; procesos_terminados_count = 0
        stats_finales_procesos = {p['nombre']: {} for p in procesos_para_simular}
        
        # Bucle principal de simulación
        while procesos_terminados_count < len(procesos_para_simular):
            # Añadir procesos llegados a la cola de listos
            nuevos_en_cola = False
            while idx_proceso_entrante < len(procesos_para_simular) and \
                  procesos_para_simular[idx_proceso_entrante]['llegada'] <= tiempo_actual:
                cola_listos.append(procesos_para_simular[idx_proceso_entrante])
                idx_proceso_entrante += 1
                nuevos_en_cola = True
            
            # Si la cola está vacía, avanzar tiempo hasta el próximo proceso o terminar
            if not cola_listos:
                if idx_proceso_entrante < len(procesos_para_simular): # Aún hay procesos por llegar
                    tiempo_actual = procesos_para_simular[idx_proceso_entrante]['llegada']
                else: # No hay más procesos por llegar y la cola está vacía
                    break 
                continue # Re-evaluar la llegada de procesos con el nuevo tiempo_actual

            proceso_actual_ref = cola_listos.pop(0) 

            tiempo_inicio_segmento = tiempo_actual
            if proceso_actual_ref['primer_comienzo_ejecucion'] == -1: # Primera vez que se ejecuta
                proceso_actual_ref['primer_comienzo_ejecucion'] = tiempo_inicio_segmento

            tiempo_ejecucion_este_quantum = min(proceso_actual_ref['restante'], quantum)
            
            proceso_actual_ref['restante'] -= tiempo_ejecucion_este_quantum
            proceso_actual_ref['tiempo_en_cpu_total'] += tiempo_ejecucion_este_quantum
            tiempo_actual += tiempo_ejecucion_este_quantum 
            tiempo_fin_segmento = tiempo_actual
            
            results_list_of_segments.append({
                'proceso': proceso_actual_ref['nombre'],
                'llegada': proceso_actual_ref['llegada'],
                'cpu': proceso_actual_ref['duracion_original'], # Ráfaga total original
                'comienzo': tiempo_inicio_segmento,
                'final': tiempo_fin_segmento,
                'espera': "Calc...", 
                'turnaround': "Calc..." 
            })

            # Volver a añadir procesos que pudieron haber llegado MIENTRAS este se ejecutaba
            # Esto es importante para que no se "salten" llegadas.
            while idx_proceso_entrante < len(procesos_para_simular) and \
                  procesos_para_simular[idx_proceso_entrante]['llegada'] <= tiempo_actual:
                # Evitar duplicados en cola_listos si ya estaba allí por una llegada anterior.
                # En RR simple, usualmente se añade al final y el sort o manejo de cola se encarga.
                # Aquí, solo nos aseguramos que los nuevos llegados estén disponibles.
                # Si el proceso actual no terminó, se añadirá de nuevo a la cola después.
                # Por ahora, solo los añadimos a la cola de listos.
                if procesos_para_simular[idx_proceso_entrante] not in cola_listos and procesos_para_simular[idx_proceso_entrante]['restante'] > 0 :
                     cola_listos.append(procesos_para_simular[idx_proceso_entrante])
                idx_proceso_entrante += 1


            if proceso_actual_ref['restante'] <= 0: # Proceso terminado
                proceso_actual_ref['tiempo_finalizacion'] = tiempo_actual
                
                turnaround_final = proceso_actual_ref['tiempo_finalizacion'] - proceso_actual_ref['llegada']
                # Espera = Turnaround - Tiempo Total de CPU (no el restante)
                espera_final = turnaround_final - proceso_actual_ref['duracion_original'] 

                stats_finales_procesos[proceso_actual_ref['nombre']]['espera'] = espera_final
                stats_finales_procesos[proceso_actual_ref['nombre']]['turnaround'] = turnaround_final
                
                procesos_terminados_count += 1
            else: # Proceso no terminado, vuelve a la cola (al final)
                cola_listos.append(proceso_actual_ref)
        
        # Actualizar 'espera' y 'turnaround' en todos los segmentos con los valores finales
        for segment in results_list_of_segments:
            nombre_proceso_segmento = segment['proceso']
            if nombre_proceso_segmento in stats_finales_procesos and stats_finales_procesos[nombre_proceso_segmento]:
                segment['espera'] = stats_finales_procesos[nombre_proceso_segmento].get('espera', 'Error E')
                segment['turnaround'] = stats_finales_procesos[nombre_proceso_segmento].get('turnaround', 'Error T')
            else: # Si un proceso no terminó (no debería pasar si el bucle es correcto y todos los procesos tienen CPU > 0)
                segment['espera'] = "No Term."
                segment['turnaround'] = "No Term."
        
        return results_list_of_segments

if __name__ == '__main__':
    try:
        CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
        GUI_DIR = os.path.dirname(CURRENT_SCRIPT_PATH)
        APP_MODULE_DIR = os.path.dirname(GUI_DIR)
        ASSETS_DIR_MAIN = os.path.join(APP_MODULE_DIR, "assets")
        if not os.path.isdir(ASSETS_DIR_MAIN):
            PROJECT_ROOT_DIR = os.path.dirname(APP_MODULE_DIR)
            ASSETS_DIR_MAIN = os.path.join(PROJECT_ROOT_DIR, "assets")
        if not os.path.isdir(ASSETS_DIR_MAIN): ASSETS_DIR_MAIN = "assets"
        BG_IMAGE_PATH = os.path.join(ASSETS_DIR_MAIN, "backgroundstarwars.jpg").replace("\\", "/")
        ICON_VOLVER_PATH = os.path.join(ASSETS_DIR_MAIN, "icon_volver.png").replace("\\", "/")
        print(f"DEBUG (__main__): BG_IMAGE_PATH redefinido a: {BG_IMAGE_PATH}")
    except NameError: print("Advertencia (__main__): __file__ no definido.")

    def _load_background(self):
        fondo_path = os.path.join("app", "assets", "backgroundstarwars.jpg")  
        fondo = Image.open(fondo_path)

        fondo_img = ctk.CTkImage(light_image=fondo, dark_image=fondo, size=(1000, 600))

        self.bg_label = ctk.CTkLabel(self, image=fondo_img, text="")
        self.bg_label.image = fondo_img
        self.bg_label.place(x=0, y=0)
    
    app = ctk.CTk()
    app.title("Test RR Scheduler GUI"); app.geometry("1280x720"); ctk.set_appearance_mode("dark")
    def go_to_main_menu_mock():
        print("Volviendo al menú principal (mock)")
        for widget in app.winfo_children(): widget.destroy()
        ctk.CTkLabel(app, text="Menú Principal (Placeholder)", font=("Arial",30,"bold"),text_color=COLOR_AMARILLO).pack(expand=True)
    RRView(app, volver_callback=go_to_main_menu_mock).mainloop()