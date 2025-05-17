import customtkinter as ctk
from PIL import Image # PIL.ImageTk no es necesario si CTkImage maneja la imagen PIL directamente
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import traceback # Para trazas de error más detalladas

# Importar constantes y rutas desde config.py
from config import (
    BG_IMAGE_RR_PATH, BG_IMAGE_SRTF_PATH,
    ICON_VOLVER_RR_PATH, ICON_VOLVER_SRTF_PATH,
    COLOR_ROJO, COLOR_AMARILLO, COLOR_ROJO_OSCURO, COLOR_AMARILLO_OSCURO,
    COLOR_VERDE, COLOR_VERDE_OSCURO,
    COLOR_FONDO_PRINCIPAL, COLOR_FONDO_SECUNDARIO, COLOR_FONDO_GANTT, COLOR_TEXTO_BLANCO,
    MIN_PROCESOS_RR, MAX_PROCESOS_RR, MIN_PROCESOS_SRTF, MAX_PROCESOS_SRTF
)
# Importar controladores (las vistas los usarán)
from controllers import RRController, SRTFController, MockRRController, MockSRTFController

# Variable global para decidir si usar los controladores Mock o los reales
# Cambia a False para usar los controladores reales (RRController, SRTFController)
USAR_CONTROLADORES_MOCK = False


class ResultsView(ctk.CTkFrame):
    def __init__(self, master, datos_resultado_lista, callback_to_previous_view, bg_image_path_to_use):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        self.datos_resultado_lista = datos_resultado_lista if datos_resultado_lista is not None else []
        self.callback_to_previous_view = callback_to_previous_view
        self.bg_image_path = bg_image_path_to_use # Ruta de fondo específica para esta vista
        
        self.background_img_obj = None
        self.background_label = None
        self.canvas_widget = None # Para el widget del canvas de Matplotlib

        # Asegurar que la ventana maestra tenga dimensiones antes de cargar el fondo
        self.master_window.update_idletasks()
        self._load_background()

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # El título y el botón volver dependen del tipo de simulación,
        # pero para simplificar, usaremos un título genérico o lo pasamos como parámetro.
        # Aquí asumimos que el título se puede inferir o es genérico.
        # Si bg_image_path_to_use es BG_IMAGE_RR_PATH, es RR, si no, SRTF.
        sim_type = "RR" if self.bg_image_path == BG_IMAGE_RR_PATH else "SRTF"
        icon_volver_path = ICON_VOLVER_RR_PATH if sim_type == "RR" else ICON_VOLVER_SRTF_PATH
        color_principal_sim = COLOR_ROJO if sim_type == "RR" else COLOR_VERDE

        self._crear_titulo_resultados(self.content_frame, f"Simulación {sim_type}")
        self._crear_boton_volver(self.content_frame, icon_volver_path, color_principal_sim)

        display_area = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        # Ajustar pady para que el título y el botón no se superpongan
        display_area.pack(fill="both", expand=True, pady=(60, 10)) # Aumentado pady superior

        self._mostrar_tabla_resultados(display_area, color_principal_sim)
        self._mostrar_gantt(display_area, sim_type) # Pasar sim_type para el título del Gantt

        # Empaquetar el frame principal de la vista y bajar el fondo
        self.pack(fill="both", expand=True)
        if self.background_label:
            self.background_label.lower()

    def _get_master_dimensions(self):
        try:
            self.master_window.update_idletasks() # Actualiza dimensiones pendientes
            width = self.master_window.winfo_width()
            height = self.master_window.winfo_height()
            if width <= 1 or height <= 1:
                geom = self.master_window.geometry()
                size_part = geom.split('+')[0]
                width, height = map(int, size_part.split('x'))
            if width <= 1 or height <= 1:
                print(f"ADVERTENCIA (ResultsView): Dimensiones de ventana no válidas. Usando 1280x720.")
                return 1280, 720
            return width, height
        except Exception as e:
            print(f"ERROR (ResultsView) obteniendo dimensiones: {e}. Usando 1280x720.")
            return 1280, 720

    def _load_background(self):
        if not os.path.exists(self.bg_image_path):
            print(f"ERROR (ResultsView): Fondo NO ENCONTRADO en '{self.bg_image_path}'. Se usará color.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None
            return

        master_width, master_height = self._get_master_dimensions()
        if master_width <= 1 or master_height <= 1:
            print(f"ERROR (ResultsView): Dimensiones de ventana no válidas ({master_width}x{master_height}) para cargar fondo.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO) # Fallback
            return

        try:
            imagen_pil = Image.open(self.bg_image_path)
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(master_width, master_height))
            
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else:
                self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"EXCEPCIÓN (ResultsView) al cargar fondo '{self.bg_image_path}': {e}")
            traceback.print_exc()
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None

    def _crear_titulo_resultados(self, parent, titulo_texto):
        # Usar un tipo de letra temático si está disponible, o uno estándar.
        # El color del título podría depender del tipo de simulación.
        color_titulo = COLOR_AMARILLO # Color genérico para el título
        try:
            font_titulo = ("Star Jedi", 26) # Fuente temática
            ctk.CTkLabel(parent, text=titulo_texto, font=font_titulo, text_color=color_titulo).pack(pady=15, anchor="n")
        except Exception: # Fallback si la fuente no está disponible
            font_titulo = ("Arial", 22, "bold")
            ctk.CTkLabel(parent, text=titulo_texto, font=font_titulo, text_color=color_titulo).pack(pady=15, anchor="n")


    def _crear_boton_volver(self, parent, icon_path, color_borde_texto):
        icono = None
        if os.path.exists(icon_path):
            try:
                icono_img = Image.open(icon_path)
                icono = ctk.CTkImage(light_image=icono_img, dark_image=icono_img, size=(20, 20))
            except Exception as e:
                print(f"ERROR (ResultsView): Excepción al cargar icono volver desde '{icon_path}': {e}")
        else:
            print(f"ERROR (ResultsView): Icono Volver NO ENCONTRADO en '{icon_path}'")
        
        try:
            font_boton = ("space age", 12) # Fuente temática
            ctk.CTkButton(parent, image=icono, text=" Volver a Ingresar Datos", command=self.callback_to_previous_view,
                          fg_color="transparent", border_color=color_borde_texto, border_width=2, text_color=color_borde_texto,
                          hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=15, y=15) # Usar place para posicionar en la esquina superior
        except Exception: # Fallback de fuente
            font_boton = ("Arial", 10)
            ctk.CTkButton(parent, image=icono, text=" Volver a Ingresar Datos", command=self.callback_to_previous_view,
                          fg_color="transparent", border_color=color_borde_texto, border_width=2, text_color=color_borde_texto,
                          hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=15, y=15)

    def _mostrar_tabla_resultados(self, parent_frame, color_header):
        tabla_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_SECUNDARIO, corner_radius=10)
        tabla_frame.pack(pady=10, padx=10, fill="x")

        headers = ["Proceso", "Llegada", "CPU Total", "Comienzos Seg.", "Fines Seg.", "Espera Total", "Turnaround Total"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(tabla_frame, text=h, text_color=color_header, font=("Arial", 13, "bold")).grid(row=0, column=i, padx=10, pady=8, sticky="w")

        if not self.datos_resultado_lista:
            ctk.CTkLabel(tabla_frame, text="No hay datos de simulación para mostrar.", text_color=COLOR_AMARILLO).grid(row=1, column=0, columnspan=len(headers), pady=10)
            return

        procesos_consolidados = {}
        for segmento in self.datos_resultado_lista:
            nombre_proc = segmento.get("proceso", "N/A_Proc")
            if nombre_proc not in procesos_consolidados:
                procesos_consolidados[nombre_proc] = {
                    "llegada": segmento.get("llegada", "-"),
                    "cpu_total": segmento.get("cpu_original", "-"),
                    "comienzos_segmento": [],
                    "fines_segmento": [],
                    "espera_total": segmento.get("espera_final", "-"),
                    "turnaround_total": segmento.get("turnaround_final", "-")
                }
            
            procesos_consolidados[nombre_proc]["comienzos_segmento"].append(str(segmento.get("comienzo", "")))
            procesos_consolidados[nombre_proc]["fines_segmento"].append(str(segmento.get("final", "")))
            
            # Actualizar con los valores finales si este segmento los tiene (para asegurar que se toma el último cálculo)
            current_espera = segmento.get("espera_final", procesos_consolidados[nombre_proc]["espera_total"])
            current_turnaround = segmento.get("turnaround_final", procesos_consolidados[nombre_proc]["turnaround_total"])

            if isinstance(current_espera, (int, float)) or (isinstance(current_espera, str) and current_espera not in ["Calc...", "En Proceso", "No Term.", "Error E"]):
                 procesos_consolidados[nombre_proc]["espera_total"] = current_espera
            if isinstance(current_turnaround, (int, float)) or (isinstance(current_turnaround, str) and current_turnaround not in ["Calc...", "En Proceso", "No Term.", "Error T"]):
                 procesos_consolidados[nombre_proc]["turnaround_total"] = current_turnaround

        nombres_procesos_ordenados = sorted(procesos_consolidados.keys())
        row_idx = 1
        for nombre_proc in nombres_procesos_ordenados:
            data = procesos_consolidados[nombre_proc]
            comienzos_str = ", ".join(filter(None, data["comienzos_segmento"])) # Filtrar Nones o vacíos
            fines_str = ", ".join(filter(None, data["fines_segmento"]))

            fila_a_mostrar = [
                nombre_proc, data["llegada"], data["cpu_total"],
                comienzos_str, fines_str, data["espera_total"], data["turnaround_total"]
            ]
            for col_idx, val in enumerate(fila_a_mostrar):
                ctk.CTkLabel(tabla_frame, text=str(val), text_color=COLOR_AMARILLO, font=("Arial", 12)).grid(row=row_idx, column=col_idx, padx=10, pady=6, sticky="w")
            row_idx += 1
        
        for i in range(len(headers)):
            tabla_frame.grid_columnconfigure(i, weight=1)

    def _mostrar_gantt(self, parent_frame, sim_type):
        gantt_container_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_FONDO_GANTT, corner_radius=10)
        gantt_container_frame.pack(pady=20, padx=10, fill="both", expand=True)
        
        gantt_items = self.datos_resultado_lista if self.datos_resultado_lista is not None else []
        if not gantt_items:
             ctk.CTkLabel(gantt_container_frame, text="No hay datos para el Diagrama de Gantt.", text_color=COLOR_AMARILLO, font=("Arial", 14)).pack(expand=True)
             return

        num_unique_processes = len(set(item.get('proceso') for item in gantt_items if item and item.get('proceso')))
        fig_height = max(4, num_unique_processes * 0.6 + 1.5) # +1.5 para márgenes y título
        
        fig, ax = plt.subplots(figsize=(12, fig_height)) # Ajustar figsize según necesidad
        fig.patch.set_facecolor(COLOR_FONDO_GANTT)
        ax.set_facecolor(COLOR_FONDO_GANTT)
        
        # Paleta de colores para Gantt (diferente para RR y SRTF si se desea)
        if sim_type == "RR":
            colores_gantt_usar = {"A": "#FF0000", "B": "#FFFF00", "C": "#B22222", "D": "#FFD700", "E": "#DC143C", "F": "#F0E68C", "G": "#FF6347", "H": "#EEE8AA", "I": "#8B0000", "J": "#FFFACD", "K": "#FA8072", "L": "#FFFFE0", "M": "#CD5C5C", "N": "#FAFAD2", "O": "#E9967A", "P": "#FFEFD5", "Q": "#FFA07A", "R": "#FFF8DC", "S": "#FF7F50", "T": "#D2B48C"}
        else: # SRTF
            colores_gantt_usar = {"A": "#32CD32", "B": "#ADFF2F", "C": "#9ACD32", "D": "#FFFF00", "E": "#F0E68C", "F": "#BDB76B", "G": "#90EE90", "H": "#98FB98", "I": "#8FBC8F", "J": "#FFD700", "K": "#00FF00", "L": "#7FFF00", "M": "#7CFC00", "N": "#FFFFE0", "O": "#3CB371", "P": "#2E8B57", "Q": "#808000", "R": "#556B2F", "S": "#6B8E23", "T": "#DAA520"}
        
        default_color = "#BEBEBE" # Gris para procesos sin color asignado
        max_final_time = 0
        
        if isinstance(gantt_items, list) and gantt_items and isinstance(gantt_items[0], dict):
            if not ('comienzo' in gantt_items[0] and 'final' in gantt_items[0]):
                ax.text(0.5, 0.5, "Datos de Gantt incompletos.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)
            else:
                y_labels_unique = sorted(list(set(item.get("proceso", f"P_indef_{i}") for i, item in enumerate(gantt_items) if item)))
                y_pos = {label: i for i, label in enumerate(y_labels_unique)}

                for item_idx, item in enumerate(gantt_items):
                    nombre = item.get("proceso", f"P_indef_{item_idx}")
                    if nombre not in y_pos: # Asegurar que todos tengan y_pos (no debería pasar con la línea anterior)
                        y_pos[nombre] = len(y_labels_unique)
                        y_labels_unique.append(nombre)
                    
                    comienzo, final_val = item.get("comienzo", 0), item.get("final", item.get("comienzo", 0))
                    # Validar que comienzo y final_val sean numéricos
                    if not (isinstance(comienzo, (int, float)) and isinstance(final_val, (int, float))):
                        print(f"ADVERTENCIA (Gantt): Segmento para '{nombre}' tiene tiempos no numéricos: comienzo={comienzo}, final={final_val}. Saltando segmento.")
                        continue

                    duracion = max(0.1, final_val - comienzo) # Mínima duración para visibilidad
                    
                    color_proceso = colores_gantt_usar.get(nombre, default_color)
                    ax.barh(y_pos[nombre], duracion, left=comienzo, color=color_proceso, edgecolor=COLOR_FONDO_GANTT, height=0.6)
                    
                    if duracion > 0.3:
                        try:
                            hex_color = color_proceso.lstrip('#')
                            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                            luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
                            text_color_in_bar = COLOR_FONDO_GANTT if luminance > 0.6 else COLOR_TEXTO_BLANCO # Ajustar umbral
                        except:
                            text_color_in_bar = COLOR_TEXTO_BLANCO # Fallback
                        ax.text(comienzo + duracion / 2, y_pos[nombre], nombre, ha='center', va='center', color=text_color_in_bar, fontsize=9, fontweight='bold')
                    
                    if final_val > max_final_time: max_final_time = final_val
                
                ax.set_yticks(list(y_pos.values()))
                ax.set_yticklabels(list(y_pos.keys()), color=COLOR_AMARILLO)
        else:
            ax.text(0.5, 0.5, "No hay datos válidos para Gantt.", color=COLOR_AMARILLO, ha='center', va='center', transform=ax.transAxes)

        ax.set_xlabel("Tiempo", color=COLOR_AMARILLO, fontsize=12)
        ax.set_ylabel("Procesos", color=COLOR_AMARILLO, fontsize=12)
        ax.set_title(f"Diagrama de Gantt - {sim_type}", color=COLOR_AMARILLO, fontsize=16, fontweight='bold')
        ax.grid(True, axis='x', linestyle=':', alpha=0.7, color=COLOR_AMARILLO_OSCURO)
        ax.tick_params(axis='x', colors=COLOR_AMARILLO)
        ax.tick_params(axis='y', colors=COLOR_AMARILLO)
        for spine_pos in ['bottom', 'top', 'left', 'right']: ax.spines[spine_pos].set_color(COLOR_AMARILLO_OSCURO)
        
        if max_final_time > 0:
            tick_step = np.ceil(max_final_time / 15) if max_final_time > 15 else 1.0
            tick_step = max(1, int(tick_step)) # Asegurar que sea al menos 1 y entero
            ax.set_xticks(np.arange(0, np.ceil(max_final_time / tick_step) * tick_step + tick_step, tick_step))
            ax.set_xlim(left=-0.5, right=max_final_time + 0.5)
        else:
            ax.set_xticks(np.arange(0, 11, 1))
            ax.set_xlim(left=-0.5, right=10.5)
        
        plt.tight_layout(pad=1.5) # Añadir padding
        if self.canvas_widget: self.canvas_widget.get_tk_widget().destroy()
        self.canvas_widget = FigureCanvasTkAgg(fig, master=gantt_container_frame)
        self.canvas_widget.draw()
        self.canvas_widget.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True, padx=5, pady=5)
        plt.close(fig) # Cerrar la figura para liberar memoria

    def destroy(self):
        # Limpiar el widget de Matplotlib si existe
        if self.canvas_widget:
            self.canvas_widget.get_tk_widget().destroy()
            self.canvas_widget = None
        # Limpiar la etiqueta de fondo si existe
        if self.background_label:
            self.background_label.destroy()
            self.background_label = None
        super().destroy()


class RRView(ctk.CTkFrame):
    def __init__(self, master, volver_callback_menu_principal):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        self.volver_callback_menu_principal = volver_callback_menu_principal
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

        self.master_window.update_idletasks()
        self._cargar_fondo()

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._load_titulo(self.main_content_frame)
        self._crear_boton_volver_main(self.main_content_frame)
        self._crear_formulario_inicial(self.main_content_frame)

        self.pack(fill="both", expand=True)
        if self.background_label:
            self.background_label.lower()

    def _get_master_dimensions(self): # Idéntico a ResultsView._get_master_dimensions
        try:
            self.master_window.update_idletasks()
            width = self.master_window.winfo_width()
            height = self.master_window.winfo_height()
            if width <= 1 or height <= 1:
                geom = self.master_window.geometry(); size_part = geom.split('+')[0]
                width, height = map(int, size_part.split('x'))
            if width <= 1 or height <= 1: return 1280, 720
            return width, height
        except Exception: return 1280, 720

    def _cargar_fondo(self): # Adaptado de ResultsView._load_background
        ruta_fondo_actual = BG_IMAGE_RR_PATH # Específico para RRView
        if not os.path.exists(ruta_fondo_actual):
            print(f"ERROR (RRView): Fondo NO ENCONTRADO en '{ruta_fondo_actual}'. Se usará color.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None
            return

        master_width, master_height = self._get_master_dimensions()
        if master_width <= 1 or master_height <= 1:
            print(f"ERROR (RRView): Dimensiones de ventana no válidas para cargar fondo.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            return
        try:
            imagen_pil = Image.open(ruta_fondo_actual)
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(master_width, master_height))
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else:
                self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"EXCEPCIÓN (RRView) al cargar fondo '{ruta_fondo_actual}': {e}")
            traceback.print_exc()
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None

    def _load_titulo(self, parent):
        try:
            titulo = ctk.CTkLabel(parent, text="Algoritmo Round Robin", font=("Star Jedi", 32), text_color=COLOR_ROJO)
            titulo.pack(pady=(10, 20), anchor="n")
        except:
            titulo = ctk.CTkLabel(parent, text="Algoritmo Round Robin", font=("Arial", 28, "bold"), text_color=COLOR_ROJO)
            titulo.pack(pady=(10, 20), anchor="n")


    def _crear_boton_volver_main(self, parent): # Adaptado de ResultsView._crear_boton_volver
        icono = None
        icon_path = ICON_VOLVER_RR_PATH # Específico para RRView
        if os.path.exists(icon_path):
            try:
                icono_img = Image.open(icon_path)
                icono = ctk.CTkImage(light_image=icono_img, dark_image=icono_img, size=(30, 30))
            except Exception as e: print(f"ERROR (RRView): Excepción al cargar icono volver main: {e}")
        else: print(f"ERROR (RRView): Icono Volver Main NO ENCONTRADO en '{icon_path}'")
        
        try:
            font_boton = ("space age", 14)
            ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback_menu_principal,
                          fg_color="transparent", border_color=COLOR_ROJO, border_width=2,
                          text_color=COLOR_ROJO, hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=10, y=10)
        except:
            font_boton = ("Arial", 12)
            ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback_menu_principal,
                          fg_color="transparent", border_color=COLOR_ROJO, border_width=2,
                          text_color=COLOR_ROJO, hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=10, y=10)


    def _crear_formulario_inicial(self, parent):
        self.formulario_inicial_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.formulario_inicial_frame.pack(pady=10, anchor="center")
        
        font_label_form = ("space age", 16)
        try: # Prueba si la fuente existe
            ctk.CTkLabel(self.formulario_inicial_frame, text="", font=font_label_form).destroy()
        except:
            font_label_form = ("Arial", 14)

        ctk.CTkLabel(self.formulario_inicial_frame, text=f"Cantidad de procesos ({MIN_PROCESOS_RR}-{MAX_PROCESOS_RR}):", font=font_label_form, text_color=COLOR_AMARILLO).pack(pady=5)
        self.cantidad_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.cantidad_entry.pack(pady=5)
        
        ctk.CTkLabel(self.formulario_inicial_frame, text="Quantum (1-4):", font=font_label_form, text_color=COLOR_AMARILLO).pack(pady=(10,5))
        self.quantum_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.quantum_entry.pack(pady=5)
        
        font_boton_form = ("space age", 15, "bold")
        try:
             ctk.CTkButton(self.formulario_inicial_frame, text="", font=font_boton_form).destroy()
        except:
            font_boton_form = ("Arial", 13, "bold")

        ctk.CTkButton(self.formulario_inicial_frame, text="Generar Tabla de Entradas", command=self._generar_tabla_inputs,
                      border_width=2, fg_color="transparent", font=font_boton_form,
                      border_color=COLOR_ROJO, text_color=COLOR_AMARILLO, hover_color=COLOR_ROJO_OSCURO
        ).pack(pady=(15,10))
        
        self.btn_calcular = ctk.CTkButton(self.formulario_inicial_frame, text="Calcular Round Robin", command=self._calcular_rr_and_show_results,
                                           border_width=2, fg_color="transparent", border_color=COLOR_AMARILLO, text_color=COLOR_ROJO,
                                           font=font_boton_form, hover_color=COLOR_AMARILLO_OSCURO, state="disabled"
        )
        self.btn_calcular.pack(pady=5)

    def _generar_tabla_inputs(self):
        try:
            cantidad_str = self.cantidad_entry.get()
            quantum_str = self.quantum_entry.get()
            if not cantidad_str or not quantum_str:
                print("Error: Cantidad y Quantum no pueden estar vacíos.")
                # Aquí podrías mostrar un mensaje en la GUI en lugar de print
                return
            cantidad = int(cantidad_str)
            quantum_val = int(quantum_str) # Validar quantum_val si es necesario
            if not (MIN_PROCESOS_RR <= cantidad <= MAX_PROCESOS_RR):
                print(f"Error: Cantidad debe estar entre {MIN_PROCESOS_RR} y {MAX_PROCESOS_RR}.")
                return
            if not (1 <= quantum_val <= 4): # Asumiendo la validación del código original
                print("Error: Quantum debe estar entre 1 y 4.")
                return
        except ValueError:
            print("Error: Cantidad y Quantum deben ser números enteros.")
            return

        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        
        dynamic_height = min(cantidad * 55 + 70, 350) # Ajustar altura máxima
        
        font_label_scroll = ("space age", 14)
        try: ctk.CTkLabel(self.main_content_frame, text="", font=font_label_scroll).destroy()
        except: font_label_scroll = ("Arial", 12, "italic")

        self.entrada_procesos_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame,
            label_text="Ingrese los Datos de los Procesos:", label_font=font_label_scroll,
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
                llegada_str, duracion_str = llegada_e.get(), cpu_e.get()
                if not llegada_str or not duracion_str:
                    print("Error: Todos los campos de llegada y CPU deben estar llenos.")
                    return
                llegada, duracion = int(llegada_str), int(duracion_str)
                if llegada < 0 or duracion <= 0:
                    print("Error: Tiempo de llegada debe ser >= 0 y Ráfaga de CPU debe ser > 0.")
                    return
                procesos_data_list.append({"nombre": nombre, "llegada": llegada, "duracion_original": duracion})
            
            quantum_str = self.quantum_entry.get()
            if not quantum_str:
                print("Error: Quantum no puede estar vacío.")
                return
            quantum = int(quantum_str)
            if not (1 <= quantum <= 4): # Asumiendo validación del código original
                print("Error: Quantum debe estar entre 1 y 4.")
                return
        except ValueError:
            print("Error: Todos los datos de llegada, CPU y Quantum deben ser números enteros.")
            return
        
        if not procesos_data_list:
            print("Error: No hay procesos para simular.")
            return
        
        try:
            controlador_usar = RRController if not USAR_CONTROLADORES_MOCK else MockRRController
            resultado_simulacion = controlador_usar.simular_rr(procesos_data_list, quantum)
            
            if resultado_simulacion is None: 
                print("Error: La simulación RR no devolvió resultados.")
                return
        except Exception as e:
            print(f"Error en simulación RR: {e}")
            traceback.print_exc()
            return
        
        self.pack_forget()
        if self.results_view_instance: self.results_view_instance.destroy()
        # Pasar la ruta de fondo correcta para RR
        self.results_view_instance = ResultsView(self.master_window, resultado_simulacion, self._return_to_rr_view, BG_IMAGE_RR_PATH)

    def _return_to_rr_view(self):
        if self.results_view_instance: self.results_view_instance.destroy(); self.results_view_instance = None
        
        # Recargar fondo y re-empaquetar
        self.master_window.update_idletasks()
        self._cargar_fondo() # Asegurar que el fondo se recargue
        self.pack(fill="both", expand=True)
        if self.background_label: self.background_label.lower()
        
        # Limpiar entradas para nueva simulación
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


class SRTFView(ctk.CTkFrame): # Similar estructura a RRView
    def __init__(self, master, volver_callback_menu_principal):
        super().__init__(master, fg_color=COLOR_FONDO_PRINCIPAL)
        self.master_window = master
        self.volver_callback_menu_principal = volver_callback_menu_principal
        self.proceso_entries = []
        self.cantidad_entry = None
        # SRTF no usa Quantum_entry
        self.background_img_obj = None
        self.background_label = None
        self.entrada_procesos_scrollable_frame = None
        self.inner_entrada_frame = None
        self.results_view_instance = None
        self.main_content_frame = None
        self.btn_calcular = None

        self.master_window.update_idletasks()
        self._cargar_fondo()

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._load_titulo(self.main_content_frame)
        self._crear_boton_volver_main(self.main_content_frame)
        self._crear_formulario_inicial(self.main_content_frame)

        self.pack(fill="both", expand=True)
        if self.background_label:
            self.background_label.lower()

    def _get_master_dimensions(self): # Idéntico a RRView
        try:
            self.master_window.update_idletasks()
            width = self.master_window.winfo_width()
            height = self.master_window.winfo_height()
            if width <= 1 or height <= 1:
                geom = self.master_window.geometry(); size_part = geom.split('+')[0]
                width, height = map(int, size_part.split('x'))
            if width <= 1 or height <= 1: return 1280, 720
            return width, height
        except Exception: return 1280, 720

    def _cargar_fondo(self): # Adaptado para SRTFView
        ruta_fondo_actual = BG_IMAGE_SRTF_PATH # Específico para SRTFView
        if not os.path.exists(ruta_fondo_actual):
            print(f"ERROR (SRTFView): Fondo NO ENCONTRADO en '{ruta_fondo_actual}'. Se usará color.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None
            return

        master_width, master_height = self._get_master_dimensions()
        if master_width <= 1 or master_height <= 1:
            print(f"ERROR (SRTFView): Dimensiones de ventana no válidas para cargar fondo.")
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            return
        try:
            imagen_pil = Image.open(ruta_fondo_actual)
            self.background_img_obj = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(master_width, master_height))
            if self.background_label is None:
                self.background_label = ctk.CTkLabel(self, image=self.background_img_obj, text="")
            else:
                self.background_label.configure(image=self.background_img_obj)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"EXCEPCIÓN (SRTFView) al cargar fondo '{ruta_fondo_actual}': {e}")
            traceback.print_exc()
            self.configure(fg_color=COLOR_FONDO_SECUNDARIO)
            if self.background_label: self.background_label.destroy(); self.background_label = None
            
    def _load_titulo(self, parent):
        try:
            titulo = ctk.CTkLabel(parent, text="Algoritmo SRTF", font=("Star Jedi", 32), text_color=COLOR_VERDE)
            titulo.pack(pady=(10, 20), anchor="n")
        except:
            titulo = ctk.CTkLabel(parent, text="Algoritmo SRTF", font=("Arial", 28, "bold"), text_color=COLOR_VERDE)
            titulo.pack(pady=(10, 20), anchor="n")

    def _crear_boton_volver_main(self, parent):
        icono = None
        icon_path = ICON_VOLVER_SRTF_PATH # Específico para SRTFView
        if os.path.exists(icon_path):
            try:
                icono_img = Image.open(icon_path)
                icono = ctk.CTkImage(light_image=icono_img, dark_image=icono_img, size=(30, 30))
            except Exception as e: print(f"ERROR (SRTFView): Excepción al cargar icono volver main: {e}")
        else: print(f"ERROR (SRTFView): Icono Volver Main NO ENCONTRADO en '{icon_path}'")
        
        try:
            font_boton = ("space age", 14)
            ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback_menu_principal,
                          fg_color="transparent", border_color=COLOR_VERDE, border_width=2,
                          text_color=COLOR_VERDE, hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=10, y=10)
        except:
            font_boton = ("Arial", 12)
            ctk.CTkButton(parent, image=icono, text=" Volver al Menú", command=self.volver_callback_menu_principal,
                          fg_color="transparent", border_color=COLOR_VERDE, border_width=2,
                          text_color=COLOR_VERDE, hover_color=COLOR_AMARILLO_OSCURO, font=font_boton
            ).place(x=10, y=10)

    def _crear_formulario_inicial(self, parent):
        self.formulario_inicial_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.formulario_inicial_frame.pack(pady=10, anchor="center")
        
        font_label_form = ("space age", 16); font_boton_form = ("space age", 15, "bold")
        try: ctk.CTkLabel(self.formulario_inicial_frame, text="", font=font_label_form).destroy()
        except: font_label_form = ("Arial", 14)
        try: ctk.CTkButton(self.formulario_inicial_frame, text="", font=font_boton_form).destroy()
        except: font_boton_form = ("Arial", 13, "bold")

        ctk.CTkLabel(self.formulario_inicial_frame, text=f"Cantidad de procesos ({MIN_PROCESOS_SRTF}-{MAX_PROCESOS_SRTF}):", font=font_label_form, text_color=COLOR_AMARILLO).pack(pady=5)
        self.cantidad_entry = ctk.CTkEntry(self.formulario_inicial_frame, width=200, justify="center", font=("Arial", 14))
        self.cantidad_entry.pack(pady=5)
        
        # SRTF no necesita Quantum
        
        ctk.CTkButton(self.formulario_inicial_frame, text="Generar Tabla de Entradas", command=self._generar_tabla_inputs,
                      border_width=2, fg_color="transparent", font=font_boton_form,
                      border_color=COLOR_VERDE, text_color=COLOR_AMARILLO, hover_color=COLOR_VERDE_OSCURO
        ).pack(pady=(15,10))
        
        self.btn_calcular = ctk.CTkButton(self.formulario_inicial_frame, text="Calcular SRTF", command=self._calcular_srtf_and_show_results,
                                           border_width=2, fg_color="transparent", border_color=COLOR_AMARILLO, text_color=COLOR_VERDE,
                                           font=font_boton_form, hover_color=COLOR_AMARILLO_OSCURO, state="disabled"
        )
        self.btn_calcular.pack(pady=5)

    def _generar_tabla_inputs(self): # Similar a RRView pero usa constantes de SRTF
        try:
            cantidad_str = self.cantidad_entry.get()
            if not cantidad_str: print("Error: Cantidad no puede estar vacía."); return
            cantidad = int(cantidad_str)
            if not (MIN_PROCESOS_SRTF <= cantidad <= MAX_PROCESOS_SRTF):
                print(f"Error: Cantidad debe estar entre {MIN_PROCESOS_SRTF} y {MAX_PROCESOS_SRTF}.")
                return
        except ValueError: print("Error: Cantidad debe ser un número entero."); return

        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        
        dynamic_height = min(cantidad * 55 + 70, 350)
        font_label_scroll = ("space age", 14)
        try: ctk.CTkLabel(self.main_content_frame, text="", font=font_label_scroll).destroy()
        except: font_label_scroll = ("Arial", 12, "italic")

        self.entrada_procesos_scrollable_frame = ctk.CTkScrollableFrame(self.main_content_frame,
            label_text="Ingrese los Datos de los Procesos:", label_font=font_label_scroll,
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
            ctk.CTkLabel(self.inner_entrada_frame, text=proceso_char, font=("Arial", 14, "bold"), text_color=COLOR_VERDE).grid(row=i + 1, column=0, padx=15, pady=8) # Color Verde para SRTF
            e_llegada = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_llegada.grid(row=i + 1, column=1, padx=15, pady=8)
            e_cpu = ctk.CTkEntry(self.inner_entrada_frame, width=120, justify="center", font=("Arial", 14)); e_cpu.grid(row=i + 1, column=2, padx=15, pady=8)
            self.proceso_entries.append((proceso_char, e_llegada, e_cpu))
        
        for col in range(3): self.inner_entrada_frame.grid_columnconfigure(col, weight=1)
        if self.btn_calcular: self.btn_calcular.configure(state="normal")

    def _calcular_srtf_and_show_results(self): # Similar a RRView
        procesos_data_list = []
        try:
            for nombre, llegada_e, cpu_e in self.proceso_entries:
                llegada_str, duracion_str = llegada_e.get(), cpu_e.get()
                if not llegada_str or not duracion_str: print("Error: Campos de llegada/CPU vacíos."); return
                llegada, duracion = int(llegada_str), int(duracion_str)
                if llegada < 0 or duracion <= 0: print("Error: Llegada >= 0 y CPU > 0."); return
                procesos_data_list.append({"nombre": nombre, "llegada": llegada, "duracion_original": duracion})
        except ValueError: print("Error: Datos deben ser enteros."); return
        
        if not procesos_data_list: print("Error: No hay procesos."); return
        
        try:
            controlador_usar = SRTFController if not USAR_CONTROLADORES_MOCK else MockSRTFController
            resultado_simulacion = controlador_usar.simular_srtf(procesos_data_list) # SRTF no necesita quantum
            
            if resultado_simulacion is None: print("Error: Simulación SRTF no devolvió resultados."); return
        except Exception as e: print(f"Error en simulación SRTF: {e}"); traceback.print_exc(); return
        
        self.pack_forget()
        if self.results_view_instance: self.results_view_instance.destroy()
        # Pasar la ruta de fondo correcta para SRTF
        self.results_view_instance = ResultsView(self.master_window, resultado_simulacion, self._return_to_srtf_view, BG_IMAGE_SRTF_PATH)

    def _return_to_srtf_view(self): # Similar a RRView
        if self.results_view_instance: self.results_view_instance.destroy(); self.results_view_instance = None
        
        self.master_window.update_idletasks()
        self._cargar_fondo()
        self.pack(fill="both", expand=True)
        if self.background_label: self.background_label.lower()
        
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy(); self.entrada_procesos_scrollable_frame = None; self.inner_entrada_frame = None
        if self.btn_calcular: self.btn_calcular.configure(state="disabled")
        if self.cantidad_entry: self.cantidad_entry.delete(0, 'end')
        self.proceso_entries = []

    def destroy(self): # Similar a RRView
        if self.results_view_instance: self.results_view_instance.destroy()
        if self.background_label: self.background_label.destroy()
        if self.entrada_procesos_scrollable_frame: self.entrada_procesos_scrollable_frame.destroy()
        super().destroy()
