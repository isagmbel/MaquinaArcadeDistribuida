import pygame
import sys
import os
import importlib
from pathlib import Path

# --- CONFIGURACIÓN DE APARIENCIA ---

# --- Fuentes ---
NOMBRE_FUENTE_PERSONALIZADA = "nokiafc22.ttf"
# NOMBRE_FUENTE_PERSONALIZADA = "04B_03_.TTF"
# NOMBRE_FUENTE_PERSONALIZADA = None # Para usar la fuente por defecto de Pygame/Sistema

TAMANO_FUENTE_TITULO = 55
TAMANO_FUENTE_BOTON = 16 # Reducido para nokiafc22
TAMANO_FUENTE_DESC = 10  # Reducido para nokiafc22

# --- COLORES! ---
PALETAS_COLOR = {
    "rosa_pastel": {
        "fondo": (255, 239, 239),
        "titulo": (255, 105, 180), # Hot Pink
        "boton": (255, 192, 203),   # Pink
        "boton_hover": (255, 160, 180), # Lighter Hot Pink
        "texto_principal": (100, 70, 80), # Dark Pink/Brownish
        "borde_boton": (255, 105, 180),
        "sombra_boton": (220, 80, 150)
    },
    "rosa_pastel_suave": {
        "fondo": (255, 240, 245),
        "titulo": (255, 105, 180),  
                                  
        "boton": (255, 182, 193),   
        "boton_hover": (255, 192, 203), 
        "texto_principal": (85, 85, 85),  
                                        
        "borde_boton": (255, 105, 180), 
                                     
        "sombra_boton": (220, 160, 175) 
    },
    "azul_arcade": {
        "fondo": (20, 30, 40),      # Dark Blue/Black
        "titulo": (100, 200, 255),  # Bright Sky Blue
        "boton": (50, 80, 120),     # Medium Blue
        "boton_hover": (70, 100, 150), # Slightly Lighter Medium Blue
        "texto_principal": (200, 220, 255), # Very Light Blue
        "borde_boton": (100, 200, 255),
        "sombra_boton": (30, 50, 80)
    },
    "verde_bosque": {
        "fondo": (230, 245, 230),      # Very Light Green
        "titulo": (40, 100, 40),       # Dark Forest Green
        "boton": (120, 180, 120),     # Medium Leaf Green
        "boton_hover": (140, 200, 140), # Lighter Leaf Green
        "texto_principal": (30, 70, 30), # Very Dark Green
        "borde_boton": (60, 120, 60),    # Darker Green for border
        "sombra_boton": (90, 150, 90)
    },
    "naranja_calido": {
        "fondo": (255, 240, 220),      # Light Peach
        "titulo": (255, 120, 0),       # Bright Orange
        "boton": (255, 165, 80),      # Medium Orange
        "boton_hover": (255, 185, 100), # Lighter Medium Orange
        "texto_principal": (180, 80, 0), # Burnt Orange/Brown
        "borde_boton": (255, 140, 50),
        "sombra_boton": (230, 100, 0)
    },
    "morado_medianoche": {
        "fondo": (40, 30, 50),        # Very Dark Purple
        "titulo": (200, 150, 255),    # Lavender
        "boton": (90, 70, 110),       # Medium Dark Purple
        "boton_hover": (110, 90, 130),  # Lighter Medium Dark Purple
        "texto_principal": (230, 210, 255), # Very Light Lavender
        "borde_boton": (150, 120, 180),
        "sombra_boton": (70, 50, 90)
    },
    "gris_moderno": {
        "fondo": (220, 220, 220),      # Light Gray
        "titulo": (50, 50, 50),        # Dark Gray
        "boton": (150, 150, 150),     # Medium Gray
        "boton_hover": (170, 170, 170), # Lighter Medium Gray
        "texto_principal": (30, 30, 30), # Nearly Black
        "borde_boton": (100, 100, 100),  # Darker Gray for border
        "sombra_boton": (120, 120, 120)
    },
    "retro_gamer": {
        "fondo": (0, 0, 0),            # Black
        "titulo": (0, 255, 0),         # Bright Green (Estilo monitor antiguo)
        "boton": (50, 50, 50),         # Dark Grey
        "boton_hover": (80, 80, 80),   # Lighter Dark Grey
        "texto_principal": (0, 200, 0),  # Medium Green
        "borde_boton": (0, 150, 0),      # Darker Green
        "sombra_boton": (30, 30, 30)
    },
    "crema_elegante": {
        "fondo": (245, 245, 220),      # Beige/Cream
        "titulo": (139, 69, 19),       # SaddleBrown (Marrón oscuro)
        "boton": (210, 180, 140),     # Tan
        "boton_hover": (220, 190, 150), # Lighter Tan
        "texto_principal": (85, 50, 10), # Dark Brown
        "borde_boton": (160, 100, 40),   # Medium Brown
        "sombra_boton": (180, 150, 110)
    }
    # Añade más paletas aquí si quieres
}

PALETA_ACTUAL = "rosa_pastel_suave" # Cambia esto a "azul_arcade" u otra que definas

COLORES = PALETAS_COLOR[PALETA_ACTUAL]

# --- FIN CONFIGURACIÓN DE APARIENCIA ---


# Obtener la ruta al directorio donde está este script (menu_gui.py)
SCRIPT_DIR = Path(__file__).resolve().parent
RUTA_FUENTE_COMPLETA = None
if NOMBRE_FUENTE_PERSONALIZADA:
    RUTA_FUENTE_COMPLETA = SCRIPT_DIR / "assets" / "fonts" / NOMBRE_FUENTE_PERSONALIZADA

class MenuGUI:
    def __init__(self, ancho=800, alto=600):
        pygame.init()

        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Arcade")

        # Asignar colores desde la configuración global
        self.FONDO = COLORES["fondo"]
        self.TITULO_COLOR = COLORES["titulo"]
        self.BOTON_COLOR = COLORES["boton"]
        self.BOTON_HOVER_COLOR = COLORES["boton_hover"]
        self.TEXTO_COLOR = COLORES["texto_principal"]
        self.BORDE_BOTON_COLOR = COLORES["borde_boton"]
        self.SOMBRA_BOTON_COLOR = COLORES["sombra_boton"]

        # Cargar Fuentes
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
                self.fuente_titulo = pygame.font.SysFont('Arial', TAMANO_FUENTE_TITULO, bold=True)
                self.fuente_boton = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTON)
                self.fuente_desc = pygame.font.SysFont('Arial', TAMANO_FUENTE_DESC)
                print("Usando SysFont 'Arial' como último recurso.")
            except Exception as e_sys:
                print(f"Error crítico: No se pudo cargar ninguna fuente ({e_sys}).")
                raise

        # Juegos disponibles
        self.juegos = [
            {
                "nombre": "N Reinas",
                "modulo": "cliente.gui.n_reinas_gui",
                "clase": "NReinasGUI",
                "descripcion": "Coloca N reinas sin amenazas",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoReinas.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            },
            {
                "nombre": "Recorrido Caballo",
                "modulo": "cliente.gui.recorrido_caballo_gui",
                "clase": "RecorridoCaballoGUI",
                "descripcion": "Paseo completo del caballo",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoCaballo.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            },
            {
                "nombre": "Torres Hanoi",
                "modulo": "cliente.gui.torres_hanoi_gui",
                "clase": "TorresHanoiGUI",
                "descripcion": "Mueve los discos entre torres",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoHanoi.png"),
                "scale": 1.0, "target_scale": 1.0, "imagen_base_escalada": None
            }
        ]

        # Configuración de botones
        self.boton_size = 180
        self.espacio_botones = 30
        self.total_width = (len(self.juegos) * self.boton_size + (len(self.juegos) - 1) * self.espacio_botones)

        # Cargar y escalar imágenes base
        for juego in self.juegos:
            try:
                if os.path.exists(juego["imagen_path"]):
                    imagen_original = pygame.image.load(juego["imagen_path"])
                    if imagen_original.get_alpha() is not None:
                       imagen_original = imagen_original.convert_alpha()
                    else:
                       imagen_original = imagen_original.convert()
                    juego["imagen_base_escalada"] = pygame.transform.smoothscale(
                        imagen_original, (self.boton_size, self.boton_size)
                    )
                else:
                    print(f"Advertencia: No se encontró la imagen {juego['imagen_path']}")
            except Exception as e:
                print(f"Error al cargar imagen {juego['imagen_path']}: {e}")

    def dibujar_menu(self):
        self.ventana.fill(self.FONDO)
        
        titulo_principal = self.fuente_titulo.render("Arcade", True, self.TITULO_COLOR)
        self.ventana.blit(titulo_principal, (self.ancho // 2 - titulo_principal.get_width() // 2, 50))

        mouse_pos = pygame.mouse.get_pos()
        start_x = (self.ancho - self.total_width) // 2

        for i, juego in enumerate(self.juegos):
            juego["scale"] += (juego["target_scale"] - juego["scale"]) * 0.1

            current_scaled_size = int(self.boton_size * juego["scale"])
            base_boton_x = start_x + i * (self.boton_size + self.espacio_botones)
            base_boton_y = 180

            boton_rect = pygame.Rect(
                base_boton_x - (current_scaled_size - self.boton_size) // 2,
                base_boton_y - (current_scaled_size - self.boton_size) // 2,
                current_scaled_size,
                current_scaled_size
            )

            hover = boton_rect.collidepoint(mouse_pos)
            juego["target_scale"] = 1.1 if hover else 1.0 # Reducido el hover para que no sea tan grande

            if hover:
                shadow_rect = boton_rect.move(3, 3) # Sombra más sutil
                # No usar border_radius para la sombra si el botón principal no lo tiene
                pygame.draw.rect(self.ventana, self.SOMBRA_BOTON_COLOR, shadow_rect)

            color_boton_actual = self.BOTON_HOVER_COLOR if hover else self.BOTON_COLOR
            # No usar border_radius para el fondo del botón
            pygame.draw.rect(self.ventana, color_boton_actual, boton_rect)

            if juego["imagen_base_escalada"]:
                imagen_a_renderizar = pygame.transform.smoothscale(
                    juego["imagen_base_escalada"],
                    (boton_rect.width, boton_rect.height)
                )
                self.ventana.blit(imagen_a_renderizar, boton_rect.topleft)

            # No usar border_radius para el borde del botón
            pygame.draw.rect(self.ventana, self.BORDE_BOTON_COLOR, boton_rect, 3) # Grosor del borde 3

            nombre_texto = self.fuente_boton.render(juego["nombre"], True, self.TEXTO_COLOR)
            nombre_x = base_boton_x + self.boton_size // 2 - nombre_texto.get_width() // 2
            nombre_y = base_boton_y + self.boton_size + 10 
            self.ventana.blit(nombre_texto, (nombre_x, nombre_y))

            desc_texto = self.fuente_desc.render(juego["descripcion"], True, self.TEXTO_COLOR)
            desc_x = base_boton_x + self.boton_size // 2 - desc_texto.get_width() // 2
            desc_y = nombre_y + nombre_texto.get_height() + 5 # Reducido espacio
            self.ventana.blit(desc_texto, (desc_x, desc_y))

    def lanzar_juego(self, juego_seleccionado):
        print(f"Lanzando juego: {juego_seleccionado['nombre']}")
        pygame.quit() 

        try:
            modulo = importlib.import_module(juego_seleccionado["modulo"])
            clase_juego = getattr(modulo, juego_seleccionado["clase"])
            instancia_juego = clase_juego() 
            instancia_juego.ejecutar()

            print(f"Juego {juego_seleccionado['nombre']} terminado. Volviendo al menú...")
            pygame.init() 
            self.__init__(self.ancho, self.alto) 

        except Exception as e: 
            print(f"Error durante la ejecución del juego {juego_seleccionado['nombre']} o al volver: {e}")
            try:
                pygame.init()
                self.__init__(self.ancho, self.alto)
            except Exception as e_recovery:
                print(f"Error crítico al intentar recuperar el menú: {e_recovery}")
                pygame.quit()
                sys.exit("No se pudo recuperar el menú.")

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False 

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: 
                    mouse_pos = pygame.mouse.get_pos()
                    start_x = (self.ancho - self.total_width) // 2
                    for i, juego in enumerate(self.juegos):
                        current_scaled_size = int(self.boton_size * juego["scale"])
                        base_boton_x = start_x + i * (self.boton_size + self.espacio_botones)
                        base_boton_y = 180
                        clickable_rect = pygame.Rect(
                            base_boton_x - (current_scaled_size - self.boton_size) // 2,
                            base_boton_y - (current_scaled_size - self.boton_size) // 2,
                            current_scaled_size, current_scaled_size
                        )
                        if clickable_rect.collidepoint(mouse_pos):
                            self.lanzar_juego(juego)
                            return True 
        return True

    def ejecutar(self):
        reloj = pygame.time.Clock()
        running = True
        while running:
            if not self.manejar_eventos(): 
                running = False
                break 
            self.dibujar_menu()
            pygame.display.flip()
            reloj.tick(60)
        print("Saliendo de MenuGUI...")
        pygame.quit()

if __name__ == "__main__":
    menu = MenuGUI()
    menu.ejecutar()
    sys.exit()