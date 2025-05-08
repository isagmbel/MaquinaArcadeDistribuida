import pygame
import sys
import os
import importlib
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN GENERAL Y DE APARIENCIA ===
# ==============================================================================

# --- Layout y Ventana ---
VENTANA_ANCHO = 800
VENTANA_ALTO = 600
FPS = 60

# --- Fuentes ---
# Cambia el nombre del archivo .ttf en cliente/gui/assets/fonts/
NOMBRE_FUENTE_PERSONALIZADA = "nokiafc22.ttf"
# NOMBRE_FUENTE_PERSONALIZADA = "04B_03_.TTF"
# NOMBRE_FUENTE_PERSONALIZADA = None # Para usar la fuente por defecto

TAMANO_FUENTE_TITULO = 55
TAMANO_FUENTE_BOTON = 16
TAMANO_FUENTE_DESC = 10

# --- Colores (Paletas) ---
PALETAS_COLOR = {
    "rosa_pastel": { # Definición original corregida
        "fondo": (255, 239, 239),
        "titulo": (255, 105, 180),
        "boton": (255, 192, 203),
        "boton_hover": (255, 160, 180),
        "texto_principal": (100, 70, 80),
        "borde_boton": (255, 105, 180),
        "sombra_boton": (220, 80, 150)
    },
    "rosa_pastel_suave": { # Paleta ajustada previamente
        "fondo": (255, 240, 245),
        "titulo": (219, 112, 147), # PaleVioletRed
        "boton": (255, 182, 193),   # LightPink
        "boton_hover": (255, 192, 203), # Pink
        "texto_principal": (85, 85, 85),  # Gris Oscuro
        "borde_boton": (219, 112, 147),
        "sombra_boton": (220, 160, 175)
    },
    "azul_arcade": {
        "fondo": (20, 30, 40), "titulo": (100, 200, 255), "boton": (50, 80, 120),
        "boton_hover": (70, 100, 150), "texto_principal": (200, 220, 255),
        "borde_boton": (100, 200, 255), "sombra_boton": (30, 50, 80)
    },
    "verde_bosque": {
        "fondo": (230, 245, 230), "titulo": (40, 100, 40), "boton": (120, 180, 120),
        "boton_hover": (140, 200, 140), "texto_principal": (30, 70, 30),
        "borde_boton": (60, 120, 60), "sombra_boton": (90, 150, 90)
    },
    "naranja_calido": {
         "fondo": (255, 240, 220), "titulo": (255, 120, 0), "boton": (255, 165, 80),
         "boton_hover": (255, 185, 100), "texto_principal": (180, 80, 0),
         "borde_boton": (255, 140, 50), "sombra_boton": (230, 100, 0)
    },
    "morado_medianoche": {
        "fondo": (40, 30, 50), "titulo": (200, 150, 255), "boton": (90, 70, 110),
        "boton_hover": (110, 90, 130), "texto_principal": (230, 210, 255),
        "borde_boton": (150, 120, 180), "sombra_boton": (70, 50, 90)
    },
    "gris_moderno": {
        "fondo": (220, 220, 220), "titulo": (50, 50, 50), "boton": (150, 150, 150),
        "boton_hover": (170, 170, 170), "texto_principal": (30, 30, 30),
        "borde_boton": (100, 100, 100), "sombra_boton": (120, 120, 120)
    },
    "retro_gamer": {
         "fondo": (0, 0, 0), "titulo": (0, 255, 0), "boton": (50, 50, 50),
         "boton_hover": (80, 80, 80), "texto_principal": (0, 200, 0),
         "borde_boton": (0, 150, 0), "sombra_boton": (30, 30, 30)
     },
    "crema_elegante": {
         "fondo": (245, 245, 220), "titulo": (139, 69, 19), "boton": (210, 180, 140),
         "boton_hover": (220, 190, 150), "texto_principal": (85, 50, 10),
         "borde_boton": (160, 100, 40), "sombra_boton": (180, 150, 110)
    }
}

PALETA_ACTUAL = "rosa_pastel_suave" # <--- SELECCIONA LA PALETA AQUÍ
COLORES = PALETAS_COLOR[PALETA_ACTUAL]

# --- Elementos UI ---
TITULO_TEXTO = "Arcade"
TITULO_Y = 50
# TITULO_SOMBRA_OFFSET = (2, 2) # Descomentar si se quiere sombra en el título

BOTON_BASE_Y = 180
BOTON_SIZE = 180 # Tamaño base del botón cuadrado
ESPACIO_BOTONES = 30
BOTON_HOVER_SCALE_FACTOR = 1.1 # Factor de escala al hacer hover (1.1 = 110%)
ANIMACION_SUAVIDAD = 0.1 # Factor para animación de escala (más bajo = más suave/lento)
SOMBRA_OFFSET = (3, 3)
BORDE_GROSOR = 3
ESPACIO_BOTON_NOMBRE = 10 # Espacio vertical entre botón y nombre
ESPACIO_NOMBRE_DESC = 5   # Espacio vertical entre nombre y descripción

# ==============================================================================
# === INICIALIZACIÓN Y RUTAS ===
# ==============================================================================

SCRIPT_DIR = Path(__file__).resolve().parent
RUTA_FUENTE_COMPLETA = None
if NOMBRE_FUENTE_PERSONALIZADA:
    RUTA_FUENTE_COMPLETA = SCRIPT_DIR / "assets" / "fonts" / NOMBRE_FUENTE_PERSONALIZADA

# ==============================================================================
# === CLASE PRINCIPAL DEL MENÚ ===
# ==============================================================================

class MenuGUI:
    # === Inicialización de la Clase ===
    def __init__(self, ancho=VENTANA_ANCHO, alto=VENTANA_ALTO):
        pygame.init()
        self.ancho = ancho
        self.alto = alto

        # --- Ventana ---
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(TITULO_TEXTO) # Usar constante

        # --- Colores (asignados desde la paleta global) ---
        self.color_fondo = COLORES["fondo"]
        self.color_titulo = COLORES["titulo"]
        self.color_boton = COLORES["boton"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_texto = COLORES["texto_principal"]
        self.color_borde_boton = COLORES["borde_boton"]
        self.color_sombra_boton = COLORES["sombra_boton"]

        # --- Carga de Fuentes ---
        self._cargar_fuentes()

        # --- Datos de Juegos ---
        self._definir_juegos()

        # --- Configuración de Layout ---
        self.boton_size = BOTON_SIZE
        self.espacio_botones = ESPACIO_BOTONES
        self.total_ancho_botones = (len(self.juegos) * self.boton_size +
                                   (len(self.juegos) - 1) * self.espacio_botones)
        self.botones_start_x = (self.ancho - self.total_ancho_botones) // 2
        self.botones_base_y = BOTON_BASE_Y

        # --- Carga de Imágenes ---
        self._cargar_imagenes_juegos()

    # === Métodos Auxiliares de Inicialización ===
    def _cargar_fuentes(self):
        """Carga las fuentes definidas en la configuración global."""
        try:
            if RUTA_FUENTE_COMPLETA and os.path.exists(RUTA_FUENTE_COMPLETA):
                print(f"Cargando fuente personalizada: {RUTA_FUENTE_COMPLETA}")
                self.fuente_titulo = pygame.font.Font(RUTA_FUENTE_COMPLETA, TAMANO_FUENTE_TITULO)
                self.fuente_boton = pygame.font.Font(RUTA_FUENTE_COMPLETA, TAMANO_FUENTE_BOTON)
                self.fuente_desc = pygame.font.Font(RUTA_FUENTE_COMPLETA, TAMANO_FUENTE_DESC)
            elif NOMBRE_FUENTE_PERSONALIZADA:
                print(f"Advertencia: Fuente '{NOMBRE_FUENTE_PERSONALIZADA}' no encontrada. Usando defecto.")
                raise pygame.error("Fuente personalizada no encontrada")
            else:
                print("Usando fuente por defecto de Pygame (None).")
                self.fuente_titulo = pygame.font.Font(None, TAMANO_FUENTE_TITULO)
                self.fuente_boton = pygame.font.Font(None, TAMANO_FUENTE_BOTON)
                self.fuente_desc = pygame.font.Font(None, TAMANO_FUENTE_DESC)
        except Exception as e_custom:
            print(f"Error cargando fuente ({e_custom}). Intentando SysFont.")
            try:
                # Usar tamaños globales también para SysFont
                self.fuente_titulo = pygame.font.SysFont('Arial', TAMANO_FUENTE_TITULO, bold=True)
                self.fuente_boton = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTON)
                self.fuente_desc = pygame.font.SysFont('Arial', TAMANO_FUENTE_DESC)
                print("Usando SysFont 'Arial' como último recurso.")
            except Exception as e_sys:
                print(f"Error crítico: No se pudo cargar ninguna fuente ({e_sys}).")
                raise

    def _definir_juegos(self):
        """Define la lista de juegos disponibles y sus propiedades."""
        self.juegos = [
            {
                "nombre": "N Reinas", "modulo": "cliente.gui.n_reinas_gui", "clase": "NReinasGUI",
                "descripcion": "Coloca N reinas sin amenazas",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoReinas.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            },
            {
                "nombre": "Recorrido Caballo", "modulo": "cliente.gui.recorrido_caballo_gui", "clase": "RecorridoCaballoGUI",
                "descripcion": "Paseo completo del caballo",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoCaballo.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            },
            {
                "nombre": "Torres Hanoi", "modulo": "cliente.gui.torres_hanoi_gui", "clase": "TorresHanoiGUI",
                "descripcion": "Mueve los discos entre torres",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoHanoi.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            }
        ]

    def _cargar_imagenes_juegos(self):
        """Carga y escala las imágenes base para los botones de los juegos."""
        for juego in self.juegos:
            try:
                if os.path.exists(juego["imagen_path"]):
                    imagen_original = pygame.image.load(juego["imagen_path"])
                    if imagen_original.get_alpha() is not None:
                       imagen_original = imagen_original.convert_alpha()
                    else:
                       imagen_original = imagen_original.convert()
                    # Escalar al tamaño base del botón
                    juego["imagen_base_escalada"] = pygame.transform.smoothscale(
                        imagen_original, (self.boton_size, self.boton_size)
                    )
                else:
                    print(f"Advertencia: No se encontró la imagen {juego['imagen_path']}")
            except Exception as e:
                print(f"Error al cargar imagen {juego['imagen_path']}: {e}")

    # === Lógica de Dibujado ===
    def dibujar_menu(self):
        """Dibuja todos los elementos del menú en la ventana."""
        self.ventana.fill(self.color_fondo)
        self._dibujar_titulo()
        self._dibujar_botones_juegos()

    def _dibujar_titulo(self):
        """Dibuja el título principal del menú."""
        # Descomentar para añadir sombra si se desea
        # if "TITULO_SOMBRA_OFFSET" in globals():
        #    titulo_sombra = self.fuente_titulo.render(TITULO_TEXTO, True, self.color_sombra_boton) # Usar color de sombra?
        #    sombra_x = self.ancho // 2 - titulo_sombra.get_width() // 2 + TITULO_SOMBRA_OFFSET[0]
        #    sombra_y = TITULO_Y + TITULO_SOMBRA_OFFSET[1]
        #    self.ventana.blit(titulo_sombra, (sombra_x, sombra_y))

        titulo_principal = self.fuente_titulo.render(TITULO_TEXTO, True, self.color_titulo)
        titulo_x = self.ancho // 2 - titulo_principal.get_width() // 2
        self.ventana.blit(titulo_principal, (titulo_x, TITULO_Y))

    def _dibujar_botones_juegos(self):
        """Dibuja los botones interactivos para cada juego."""
        mouse_pos = pygame.mouse.get_pos()

        for i, juego in enumerate(self.juegos):
            # --- Animación de escala ---
            juego["scale"] += (juego["target_scale"] - juego["scale"]) * ANIMACION_SUAVIDAD
            current_scaled_size = int(self.boton_size * juego["scale"])

            # --- Cálculo de posición ---
            base_boton_x = self.botones_start_x + i * (self.boton_size + self.espacio_botones)
            # Rect del botón final, centrado respecto a su posición base
            boton_rect = pygame.Rect(
                base_boton_x - (current_scaled_size - self.boton_size) // 2,
                self.botones_base_y - (current_scaled_size - self.boton_size) // 2,
                current_scaled_size,
                current_scaled_size
            )

            # --- Estado Hover ---
            hover = boton_rect.collidepoint(mouse_pos)
            juego["target_scale"] = BOTON_HOVER_SCALE_FACTOR if hover else 1.0

            # --- Dibujar Sombra (si hover) ---
            if hover:
                shadow_rect = boton_rect.move(SOMBRA_OFFSET[0], SOMBRA_OFFSET[1])
                pygame.draw.rect(self.ventana, self.color_sombra_boton, shadow_rect)

            # --- Dibujar Fondo del Botón ---
            color_boton_actual = self.color_boton_hover if hover else self.color_boton
            pygame.draw.rect(self.ventana, color_boton_actual, boton_rect)

            # --- Dibujar Imagen del Juego ---
            if juego["imagen_base_escalada"]:
                imagen_a_renderizar = pygame.transform.smoothscale(
                    juego["imagen_base_escalada"],
                    (boton_rect.width, boton_rect.height)
                )
                self.ventana.blit(imagen_a_renderizar, boton_rect.topleft)

            # --- Dibujar Borde del Botón ---
            pygame.draw.rect(self.ventana, self.color_borde_boton, boton_rect, BORDE_GROSOR)

            # --- Dibujar Texto (Nombre y Descripción) ---
            nombre_texto_surf = self.fuente_boton.render(juego["nombre"], True, self.color_texto)
            nombre_x = base_boton_x + self.boton_size // 2 - nombre_texto_surf.get_width() // 2
            nombre_y = self.botones_base_y + self.boton_size + ESPACIO_BOTON_NOMBRE
            self.ventana.blit(nombre_texto_surf, (nombre_x, nombre_y))

            desc_texto_surf = self.fuente_desc.render(juego["descripcion"], True, self.color_texto)
            desc_x = base_boton_x + self.boton_size // 2 - desc_texto_surf.get_width() // 2
            desc_y = nombre_y + nombre_texto_surf.get_height() + ESPACIO_NOMBRE_DESC
            self.ventana.blit(desc_texto_surf, (desc_x, desc_y))

    # === Lanzamiento de Juegos ===
    def lanzar_juego(self, juego_seleccionado):
        """Cierra el menú actual, lanza el juego seleccionado y reinicia el menú al volver."""
        print(f"Lanzando juego: {juego_seleccionado['nombre']}")
        pygame.quit() # Liberar recursos de Pygame del menú

        try:
            modulo = importlib.import_module(juego_seleccionado["modulo"])
            clase_juego = getattr(modulo, juego_seleccionado["clase"])
            instancia_juego = clase_juego()
            instancia_juego.ejecutar() # El juego toma el control

            print(f"Juego {juego_seleccionado['nombre']} terminado. Volviendo al menú...")
            # Re-inicializar Pygame y el menú completo para volver limpiamente
            pygame.init()
            self.__init__(self.ancho, self.alto) # Llama a todo el __init__ de nuevo

        except Exception as e:
            print(f"Error durante la ejecución del juego {juego_seleccionado['nombre']} o al volver: {e}")
            # Intento de recuperación reinicializando el menú
            try:
                pygame.init()
                self.__init__(self.ancho, self.alto)
            except Exception as e_recovery:
                print(f"Error crítico al intentar recuperar el menú: {e_recovery}")
                pygame.quit()
                sys.exit("No se pudo recuperar el menú.")

    # === Manejo de Eventos ===
    def manejar_eventos(self):
        """Procesa los eventos de Pygame (input, cierre). Retorna False si se debe salir."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False # Señal para salir

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Clic izquierdo
                    if self._manejar_clic_boton(evento.pos):
                        return True # Indica que se manejó un clic de lanzamiento

        return True # Continuar ejecutando

    def _manejar_clic_boton(self, mouse_pos):
        """Verifica si el clic fue en un botón de juego y lo lanza."""
        for i, juego in enumerate(self.juegos):
            # Re-calcular el rect del botón con su escala actual para detección precisa
            current_scaled_size = int(self.boton_size * juego["scale"])
            base_boton_x = self.botones_start_x + i * (self.boton_size + self.espacio_botones)
            clickable_rect = pygame.Rect(
                base_boton_x - (current_scaled_size - self.boton_size) // 2,
                self.botones_base_y - (current_scaled_size - self.boton_size) // 2,
                current_scaled_size, current_scaled_size
            )
            if clickable_rect.collidepoint(mouse_pos):
                self.lanzar_juego(juego)
                return True # Clic manejado
        return False # Clic no fue en un botón

    # === Bucle Principal ===
    def ejecutar(self):
        """Inicia y mantiene el bucle principal del menú."""
        reloj = pygame.time.Clock()
        running = True
        while running:
            # Manejar eventos (puede retornar False para salir)
            if not self.manejar_eventos():
                running = False
                break

            # Dibujar estado actual
            self.dibujar_menu()

            # Actualizar pantalla
            pygame.display.flip()

            # Controlar FPS
            reloj.tick(FPS)

        print("Saliendo de MenuGUI...")
        pygame.quit()

# ==============================================================================
# === Bloque de Ejecución Directa (para pruebas) ===
# ==============================================================================
if __name__ == "__main__":
    # Este bloque solo se ejecuta si se corre 'python menu_gui.py' directamente.
    # Si es importado por main.py, este bloque no se ejecuta.
    print("Ejecutando MenuGUI directamente para pruebas...")

    # Asegurarse de que el directorio raíz está en sys.path para que las
    # importaciones en lanzar_juego() funcionen.
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2] # MAQUINADEARCADE
    if str(PROJECT_ROOT_TEST) not in sys.path:
       sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG (direct execution): Project root {PROJECT_ROOT_TEST} added to sys.path.")

    menu = MenuGUI()
    menu.ejecutar() # Inicia el bucle del menú
    sys.exit() # Salir del script cuando ejecutar() termine