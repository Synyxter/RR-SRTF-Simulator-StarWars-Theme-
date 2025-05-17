import os


# Obtener la ruta absoluta del directorio donde se encuentra este archivo (config.py)
# Esto ayuda a construir rutas absolutas a otros archivos, como los assets.
try:
    # __file__ es la ruta al script actual. os.path.dirname obtiene el directorio.
    # os.path.abspath convierte una ruta relativa en absoluta.
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback si __file__ no está definido (por ejemplo, en algunos entornos interactivos)
    # En este caso, se asume que el directorio de trabajo actual es la base.
    BASE_DIR = os.path.abspath(".")
    print("ADVERTENCIA (config.py): __file__ no definido. Usando CWD como BASE_DIR.")

# Construir la ruta al directorio de 'assets'
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# --- Nombres de Archivo de Assets ---
# Define aquí los nombres de tus archivos de imagen para facilitar su cambio si es necesario.
BG_IMAGE_RR_FILENAME = "backgroundstarwars.jpg"
BG_IMAGE_SRTF_FILENAME = "backgroundstarwars2.jpg" # O el que prefieras para SRTF
ICON_VOLVER_RR_FILENAME = "icon_volver.png" # Ícono para el botón "volver" en la vista RR
ICON_VOLVER_SRTF_FILENAME = "icon_volver.png" # Ícono para el botón "volver" en la vista SRTF
APP_ICON_FILENAME = "logolinuxstarwars.ico" # Ícono para la ventana de la aplicación (debe ser .ico para Windows)

# --- Rutas Completas a los Assets ---
# Construye las rutas completas a cada asset.
# .replace("\\", "/") asegura que las rutas usen slashes hacia adelante, lo cual es más compatible entre OS.
BG_IMAGE_RR_PATH = os.path.join(ASSETS_DIR, BG_IMAGE_RR_FILENAME).replace("\\", "/")
BG_IMAGE_SRTF_PATH = os.path.join(ASSETS_DIR, BG_IMAGE_SRTF_FILENAME).replace("\\", "/")
ICON_VOLVER_RR_PATH = os.path.join(ASSETS_DIR, ICON_VOLVER_RR_FILENAME).replace("\\", "/")
ICON_VOLVER_SRTF_PATH = os.path.join(ASSETS_DIR, ICON_VOLVER_SRTF_FILENAME).replace("\\", "/")
APP_ICON_PATH = os.path.join(ASSETS_DIR, APP_ICON_FILENAME).replace("\\", "/")

# --- Colores de la Aplicación ---
# Define los colores aquí para mantener la consistencia y facilitar cambios.
COLOR_ROJO = "#FF0000"
COLOR_AMARILLO = "#FFFF00"
COLOR_ROJO_OSCURO = "#AA0000"
COLOR_AMARILLO_OSCURO = "#B8860B" # DarkGoldenrod

COLOR_VERDE = "#32CD32"  # Lime Green
COLOR_VERDE_OSCURO = "#006400" # Dark Green

COLOR_FONDO_PRINCIPAL = "#000000" # Negro, usado como fondo base de las vistas
COLOR_FONDO_SECUNDARIO = "#1A1A1A" # Gris oscuro, para elementos como tablas o frames internos
COLOR_FONDO_GANTT = "#000000" # Fondo específico para el área del diagrama de Gantt
COLOR_TEXTO_BLANCO = "#FFFFFF"

# --- Constantes de la Simulación ---
MIN_PROCESOS_RR = 3 # Mínimo de procesos para Round Robin
MAX_PROCESOS_RR = 20 # Máximo de procesos para Round Robin
MIN_PROCESOS_SRTF = 3 # Mínimo de procesos para SRTF
MAX_PROCESOS_SRTF = 20 # Máximo de procesos para SRTF
