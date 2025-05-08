import pygame
import sys
import os
import importlib
# import subprocess # No se usa
# import math # No se usa
from pathlib import Path

# Obtener la ruta al directorio donde está este script (menu_gui.py)
SCRIPT_DIR = Path(__file__).resolve().parent

class MenuGUI:
    def __init__(self, ancho=800, alto=600):
        pygame.init()

        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Arcade")

        # Colores en rosa pastel
        self.FONDO = (255, 239, 239)
        self.TITULO = (255, 105, 180)
        self.BOTON = (255, 192, 203)
        self.BOTON_HOVER = (255, 160, 180)
        self.TEXTO = (139, 69, 19)
        self.BORDE_BOTON = (255, 105, 180)

        # Fuentes
        try:
            self.fuente_titulo = pygame.font.Font(None, 60)
            self.fuente_boton = pygame.font.Font(None, 24)
            self.fuente_desc = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"Error cargando fuente por defecto: {e}. Usando SysFont.")
            self.fuente_titulo = pygame.font.SysFont('Arial', 60, bold=True)
            self.fuente_boton = pygame.font.SysFont('Arial', 24)
            self.fuente_desc = pygame.font.SysFont('Arial', 16)

        # Juegos disponibles
        self.juegos = [
            {
                "nombre": "N Reinas",
                "modulo": "cliente.gui.n_reinas_gui",
                "clase": "NReinasGUI",
                "descripcion": "Coloca N reinas sin amenazas",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoReinas.png"),
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_base_escalada": None # Imagen escalada al tamaño base del botón
            },
            {
                "nombre": "Recorrido Caballo",
                "modulo": "cliente.gui.recorrido_caballo_gui",
                "clase": "RecorridoCaballoGUI",
                "descripcion": "Paseo completo del caballo",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoCaballo.png"),
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_base_escalada": None
            },
            {
                "nombre": "Torres Hanoi",
                "modulo": "cliente.gui.torres_hanoi_gui",
                "clase": "TorresHanoiGUI",
                "descripcion": "Mueve los discos entre torres",
                "imagen_path": str(SCRIPT_DIR / "assets" / "images" / "iconoHanoi.png"),
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_base_escalada": None
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
                    # Convertir para mejor rendimiento y manejo de alfa (opcional pero recomendado)
                    if imagen_original.get_alpha() is not None:
                       imagen_original = imagen_original.convert_alpha()
                    else:
                       imagen_original = imagen_original.convert()

                    # Escalar la imagen al tamaño base del botón para usarla como referencia
                    juego["imagen_base_escalada"] = pygame.transform.smoothscale(
                        imagen_original,
                        (self.boton_size, self.boton_size) # Escalar al tamaño completo del botón base
                    )
                else:
                    print(f"Advertencia: No se encontró la imagen {juego['imagen_path']}")
                    # Podrías crear un placeholder aquí si lo deseas
            except Exception as e:
                print(f"Error al cargar imagen {juego['imagen_path']}: {e}")

    def dibujar_menu(self):
        self.ventana.fill(self.FONDO)

        # Dibujar título
        titulo_sombra = self.fuente_titulo.render("Arcade", True, (255, 150, 180))
        self.ventana.blit(titulo_sombra, (self.ancho // 2 - titulo_sombra.get_width() // 2 + 3, 53))
        titulo_principal = self.fuente_titulo.render("Arcade", True, self.TITULO)
        self.ventana.blit(titulo_principal, (self.ancho // 2 - titulo_principal.get_width() // 2, 50))

        mouse_pos = pygame.mouse.get_pos()
        start_x = (self.ancho - self.total_width) // 2

        for i, juego in enumerate(self.juegos):
            juego["scale"] += (juego["target_scale"] - juego["scale"]) * 0.1 # Animación suave

            current_scaled_size = int(self.boton_size * juego["scale"])
            
            # Posición base del botón (esquina superior izquierda antes de la animación de centrado)
            base_boton_x = start_x + i * (self.boton_size + self.espacio_botones)
            base_boton_y = 180

            # Rect del botón, ajustado para que el escalado sea desde el centro
            boton_rect = pygame.Rect(
                base_boton_x - (current_scaled_size - self.boton_size) // 2,
                base_boton_y - (current_scaled_size - self.boton_size) // 2,
                current_scaled_size,
                current_scaled_size
            )

            hover = boton_rect.collidepoint(mouse_pos)
            juego["target_scale"] = 1.1 if hover else 1.0

            # Dibujar sombra si está en hover
            if hover:
                shadow_rect = boton_rect.move(5, 5) # Desplazar para la sombra
                pygame.draw.rect(self.ventana, (255, 200, 200), shadow_rect, border_radius=15)

            # Dibujar el fondo del botón
            color_boton = self.BOTON_HOVER if hover else self.BOTON
            pygame.draw.rect(self.ventana, color_boton, boton_rect, border_radius=15)

            # Dibujar la imagen del juego para que LLENE el botón animado
            if juego["imagen_base_escalada"]:
                # Reescalar la imagen base al tamaño actual del botón
                imagen_a_renderizar = pygame.transform.smoothscale(
                    juego["imagen_base_escalada"],
                    (boton_rect.width, boton_rect.height)
                )
                self.ventana.blit(imagen_a_renderizar, boton_rect.topleft) # Blit en la esquina del botón

            # Dibujar el borde del botón encima de la imagen
            pygame.draw.rect(self.ventana, self.BORDE_BOTON, boton_rect, 3, border_radius=15)

            # Dibujar nombre del juego
            nombre_texto = self.fuente_boton.render(juego["nombre"], True, self.TEXTO)
            nombre_x = base_boton_x + self.boton_size // 2 - nombre_texto.get_width() // 2
            nombre_y = base_boton_y + self.boton_size + 5 # Debajo del tamaño original del botón
            self.ventana.blit(nombre_texto, (nombre_x, nombre_y))

            # Dibujar descripción
            desc_texto = self.fuente_desc.render(juego["descripcion"], True, self.TEXTO)
            desc_x = base_boton_x + self.boton_size // 2 - desc_texto.get_width() // 2
            desc_y = nombre_y + nombre_texto.get_height() + 5
            self.ventana.blit(desc_texto, (desc_x, desc_y))

    def lanzar_juego(self, juego_seleccionado):
        print(f"Lanzando juego: {juego_seleccionado['nombre']}")
        # pygame.quit() # No es ideal si quieres volver al menú fluidamente.
                      # Los juegos deberían manejar su propio bucle y retornar.
                      # Si los juegos hacen pygame.quit(), tendrás que reinicializar Pygame aquí.
        
        # Guardar estado actual de la pantalla del menú si es necesario, o simplemente ocultarla
        # current_screen_surface = self.ventana.copy() # Si quisieras restaurarla tal cual

        try:
            modulo = importlib.import_module(juego_seleccionado["modulo"])
            clase_juego = getattr(modulo, juego_seleccionado["clase"])
            
            # Pasar la ventana actual a los juegos puede ser una opción para evitar re-inits de pygame
            # instancia_juego = clase_juego(self.ventana) 
            instancia_juego = clase_juego() # Asumiendo que el juego inicializa su propia pantalla o la recibe
            instancia_juego.ejecutar() # El juego toma el control

            # Al regresar del juego:
            print(f"Juego {juego_seleccionado['nombre']} terminado. Volviendo al menú.")
            # Si los juegos no hacen pygame.quit(), el display de Pygame del menú debería seguir activo.
            # Puede que necesites re-establecer el caption o re-dibujar algo específico.
            # Si el juego modificó el modo de video, necesitas restaurarlo:
            self.ventana = pygame.display.set_mode((self.ancho, self.alto))
            pygame.display.set_caption("Arcade")
            # Vuelve a cargar fuentes si el juego las desinicializó o hizo pygame.quit()
            try:
                self.fuente_titulo = pygame.font.Font(None, 60)
                self.fuente_boton = pygame.font.Font(None, 24)
                self.fuente_desc = pygame.font.Font(None, 16)
            except: # Manejo básico por si acaso
                self.fuente_titulo = pygame.font.SysFont('Arial', 60, bold=True)
                self.fuente_boton = pygame.font.SysFont('Arial', 24)
                self.fuente_desc = pygame.font.SysFont('Arial', 16)


        except ImportError as e:
            print(f"Error de importación al lanzar {juego_seleccionado['nombre']}: {e}")
            print(f"PYTHONPATH: {sys.path}") # Ayuda a depurar problemas de importación
        except AttributeError as e:
            print(f"Error de atributo (¿clase no encontrada?) al lanzar {juego_seleccionado['nombre']}: {e}")
        except Exception as e:
            print(f"Error general al lanzar {juego_seleccionado['nombre']}: {e}")
            # Considera no hacer self.__init__() aquí, puede ocultar el error original
            # Si hay un error crítico, es mejor que el programa falle y muestre el traceback.
            # Para una mejor UX, podrías mostrar un mensaje de error en la GUI.

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Botón izquierdo del ratón
                    mouse_pos = pygame.mouse.get_pos()
                    start_x = (self.ancho - self.total_width) // 2

                    for i, juego in enumerate(self.juegos):
                        # El rect de colisión debe ser el mismo que se usa para dibujar el botón
                        current_scaled_size = int(self.boton_size * juego["scale"])
                        base_boton_x = start_x + i * (self.boton_size + self.espacio_botones)
                        base_boton_y = 180
                        
                        clickable_rect = pygame.Rect(
                            base_boton_x - (current_scaled_size - self.boton_size) // 2,
                            base_boton_y - (current_scaled_size - self.boton_size) // 2,
                            current_scaled_size,
                            current_scaled_size
                        )

                        if clickable_rect.collidepoint(mouse_pos):
                            self.lanzar_juego(juego)
                            return # Salir del bucle una vez que se lanza un juego

    def ejecutar(self):
        reloj = pygame.time.Clock()
        running = True
        while running:
            self.manejar_eventos() # manejar_eventos puede llamar a sys.exit()
            self.dibujar_menu()
            pygame.display.flip()
            reloj.tick(60)
        
        pygame.quit() # Asegurarse de que Pygame se cierre si el bucle termina por otra razón

if __name__ == "__main__":
    # Este bloque es para probar menu_gui.py directamente.
    # Si ejecutas desde MAQUINADEARCADE/main.py, este bloque no se ejecuta.
    # Para pruebas directas, podrías necesitar ajustar sys.path aquí:
    # ROOT_DIR_FOR_TEST = Path(__file__).resolve().parents[2] # Ir 2 niveles arriba a MAQUINADEARCADE
    # sys.path.append(str(ROOT_DIR_FOR_TEST))
    
    menu = MenuGUI()
    menu.ejecutar()