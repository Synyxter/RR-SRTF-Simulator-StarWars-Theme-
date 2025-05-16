# app/gui/rr_view.py

import customtkinter as ctk
from PIL import Image

# from app.controllers.rr_controller import RRController

class RRView(ctk.CTkFrame):
    def __init__(self, master, volver_callback):
        super().__init__(master)
        self.volver_callback = volver_callback
        self.proceso_entries = []
        self.quantum_entry = None
        self.resultados_frame = None
        self.background_img = None

        self._cargar_fondo()
        self._load_titulo()
        self._crear_boton_volver()
        self._crear_formulario()

        self.pack(fill="both", expand=True)

    def _cargar_fondo(self):
        img_path = "app/assets/backgroundstarwars.jpg"
        imagen = Image.open(img_path)
        self.background_img = ctk.CTkImage(light_image=imagen, size=(1280, 720))
        fondo = ctk.CTkLabel(self, image=self.background_img, text="")
        fondo.place(x=0, y=0, relwidth=1, relheight=1)
        
    def _load_titulo(self):
        titulo = ctk.CTkLabel(self, text="Algoritmo Round Robin", font=("Star Jedi", 28), text_color="red")
        titulo.pack(pady=10)

    def _crear_boton_volver(self):
        icono = ctk.CTkImage(Image.open("app/assets/icon_volver.png"), size=(30, 30))
        boton_volver = ctk.CTkButton(
            self,
            image=icono,
            text=" Volver",
            command=self.volver_callback,
            fg_color="transparent",
            border_color="red",
            border_width=2,
            text_color="red",
            hover_color="black",
            font=ctk.CTkFont(family="space age", size=14)
        )
        boton_volver.place(x=30, y=20)

    def _crear_formulario(self):
        formulario_frame = ctk.CTkFrame(self, fg_color="transparent")
        formulario_frame.place(relx=0.5, rely=0.18, anchor="n")

        label = ctk.CTkLabel(formulario_frame, text="Cantidad de procesos (entre 4 y 6):", font=("space age", 14))
        label.pack(pady=5)
        self.cantidad_entry = ctk.CTkEntry(formulario_frame, width=120)
        self.cantidad_entry.pack(pady=5)

        label_q = ctk.CTkLabel(formulario_frame, text="Quantum (entre 1 y 4):", font=("space age", 14))
        label_q.pack(pady=5)
        self.quantum_entry = ctk.CTkEntry(formulario_frame, width=120)
        self.quantum_entry.pack(pady=5)

        generar_btn = ctk.CTkButton(
            formulario_frame, text="Generar Tabla", command=self._generar_tabla, border_width=2, fg_color="transparent", font=("spage age", 13), border_color="red", text_color="yellow"
        )
        generar_btn.pack(pady=10)

    def _generar_tabla(self):
        cantidad = int(self.cantidad_entry.get())
        if cantidad < 4 or cantidad > 6:
            return

        if self.resultados_frame:
            self.resultados_frame.destroy()

        self.resultados_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.resultados_frame.place(relx=0.5, rely=0.4, anchor="n")

        self.proceso_entries = []

        header = ["Proceso", "Llegada", "CPU"]
        for i, h in enumerate(header):
            ctk.CTkLabel(self.resultados_frame, text=h, font=("Arial", 14)).grid(row=0, column=i, padx=5, pady=5)

        for i in range(cantidad):
            fila = []
            proceso = chr(65 + i)  # A, B, C, ...
            ctk.CTkLabel(self.resultados_frame, text=proceso).grid(row=i+1, column=0, padx=5, pady=5)

            entrada_llegada = ctk.CTkEntry(self.resultados_frame, width=70)
            entrada_llegada.grid(row=i+1, column=1, padx=5, pady=5)
            entrada_cpu = ctk.CTkEntry(self.resultados_frame, width=70)
            entrada_cpu.grid(row=i+1, column=2, padx=5, pady=5)

            fila.append(proceso)
            fila.append(entrada_llegada)
            fila.append(entrada_cpu)
            self.proceso_entries.append(fila)

        btn_calcular = ctk.CTkButton(
            self.resultados_frame,
            text="Calcular RR",
            command=self._calcular_rr,
            border_width=2,
            fg_color="transparent",
            border_color="green",
            text_color="green"
        )
        btn_calcular.grid(row=cantidad + 2, columnspan=3, pady=10)

    def _calcular_rr(self):
        procesos = []
        for fila in self.proceso_entries:
            nombre = fila[0]
            llegada = int(fila[1].get())
            duracion = int(fila[2].get())
            procesos.append({"nombre": nombre, "llegada": llegada, "duracion": duracion})

        quantum = int(self.quantum_entry.get())
        resultado = RRController.simular_rr(procesos, quantum)

        self._mostrar_resultados(resultado)

    def _mostrar_resultados(self, datos):
        resultado_frame = ctk.CTkFrame(self, fg_color="black")
        resultado_frame.place(relx=0.5, rely=0.8, anchor="center")

        headers = ["Proceso", "Llegada", "CPU", "Comienzo", "Final", "Espera", "Turnaround"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(resultado_frame, text=h, text_color="yellow").grid(row=0, column=i, padx=5, pady=5)

        for j, proceso in enumerate(datos):
            for i, key in enumerate(["proceso", "llegada", "cpu", "comienzo", "final", "espera", "turnaround"]):
                valor = proceso[key]
                ctk.CTkLabel(resultado_frame, text=str(valor), text_color="white").grid(row=j+1, column=i, padx=5, pady=3)
