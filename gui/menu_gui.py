import pygame
import sys
import os
import importlib
import subprocess
import math

class MenuGUI:
    def __init__(self, ancho=800, alto=600):
        pygame.init()
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Arcade")
        
        # Colores en rosa pastel
        self.FONDO = (255, 239, 239)  # Rosa pastel muy claro
        self.TITULO = (255, 105, 180)  # Rosa fuerte
        self.BOTON = (255, 192, 203)   # Rosa pastel clásico
        self.BOTON_HOVER = (255, 160, 180)  # Rosa pastel más intenso
        self.TEXTO = (139, 69, 19)     # Marrón oscuro para contraste
        self.BORDE_BOTON = (255, 105, 180)  # Rosa fuerte para bordes
        
        # Fuentes
        try:
            self.fuente_titulo = pygame.font.Font(None, 60)
            self.fuente_boton = pygame.font.Font(None, 24)  # Reducido para nombres debajo
            self.fuente_desc = pygame.font.Font(None, 16)    # Reducido para descripción
        except:
            self.fuente_titulo = pygame.font.SysFont('Arial', 60, bold=True)
            self.fuente_boton = pygame.font.SysFont('Arial', 24)
            self.fuente_desc = pygame.font.SysFont('Arial', 16)
        
        # Juegos disponibles (con rutas de imágenes)
        self.juegos = [
            {
                "nombre": "N Reinas",
                "modulo": "gui.n_reinas_gui",
                "clase": "NReinasGUI",
                "descripcion": "Coloca N reinas sin amenazas",
                "imagen": "assets/images/iconoReinas.png",  # Ruta de la imagen
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_cargada": None  # Aquí se guardará la superficie de pygame
            },
            {
                "nombre": "Recorrido Caballo",
                "modulo": "gui.recorrido_caballo_gui",
                "clase": "RecorridoCaballoGUI",
                "descripcion": "Paseo completo del caballo",
                "imagen": "assets/images/iconoCaballo.png",
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_cargada": None
            },
            {
                "nombre": "Torres Hanoi",
                "modulo": "gui.torres_hanoi_gui",
                "clase": "TorresHanoiGUI",
                "descripcion": "Mueve los discos entre torres",
                "imagen": "assets/images/iconoHanoi.png",
                "scale": 1.0,
                "target_scale": 1.0,
                "imagen_cargada": None
            }
        ]
        

        # Configuración de botones
        self.boton_size = 180  # Aumentado para mejor visualización
        self.espacio_botones = 30
        self.total_width = (len(self.juegos) * self.boton_size + (len(self.juegos)-1) * self.espacio_botones)
    

        # Cargar imágenes (manejo de errores si no existen)
        for juego in self.juegos:
            try:
                if os.path.exists(juego["imagen"]):
                    imagen = pygame.image.load(juego["imagen"])
                    # Escalar la imagen para que quepa en el botón (dejando margen)
                    juego["imagen_cargada"] = pygame.transform.scale(
                        imagen, 
                        (self.boton_size - 30, self.boton_size - 30)
                    )
                else:
                    print(f"Advertencia: No se encontró la imagen {juego['imagen']}")
                    juego["imagen_cargada"] = None
            except Exception as e:
                print(f"Error al cargar imagen {juego['imagen']}: {e}")
                juego["imagen_cargada"] = None
        
    def dibujar_menu(self):
        # Dibujar fondo
        self.ventana.fill(self.FONDO)
        
        # Dibujar título con efecto cute
        titulo = self.fuente_titulo.render("Arcade", True, (255, 150, 180))  # Sombra
        self.ventana.blit(titulo, (self.ancho//2 - titulo.get_width()//2 + 3, 53))
        titulo = self.fuente_titulo.render("Arcade", True, self.TITULO)
        self.ventana.blit(titulo, (self.ancho//2 - titulo.get_width()//2, 50))
        
        # Dibujar botones de juegos en horizontal
        mouse_pos = pygame.mouse.get_pos()
        start_x = (self.ancho - self.total_width) // 2
        
        for i, juego in enumerate(self.juegos):
            # Animación suave de escalado
            juego["scale"] += (juego["target_scale"] - juego["scale"]) * 0.1
            
            # Calcular posición y tamaño del botón con animación
            scaled_size = int(self.boton_size * juego["scale"])
            boton_x = start_x + i * (self.boton_size + self.espacio_botones)
            boton_y = 180  # Subido un poco para dejar espacio
            boton_rect = pygame.Rect(
                boton_x - (scaled_size - self.boton_size) // 2,
                boton_y - (scaled_size - self.boton_size) // 2,
                scaled_size,
                scaled_size
            )
            
            # Verificar hover y actualizar target_scale
            hover = boton_rect.collidepoint(mouse_pos)
            juego["target_scale"] = 1.1 if hover else 1.0
            
            # Dibujar el botón con bordes redondeados y sombra cuando está hover
            if hover:
                shadow_rect = pygame.Rect(
                    boton_rect.x + 5,
                    boton_rect.y + 5,
                    boton_rect.width,
                    boton_rect.height
                )
                pygame.draw.rect(self.ventana, (255, 200, 200), shadow_rect, border_radius=15)
            
            color = self.BOTON_HOVER if hover else self.BOTON
            pygame.draw.rect(self.ventana, color, boton_rect, border_radius=15)
            pygame.draw.rect(self.ventana, self.BORDE_BOTON, boton_rect, 3, border_radius=15)
            
            # Dibujar la imagen del juego (centrada en el botón)
            if juego["imagen_cargada"]:
                img_rect = juego["imagen_cargada"].get_rect()
                img_x = boton_x + (self.boton_size - img_rect.width) // 2
                img_y = boton_y + (self.boton_size - img_rect.height) // 2 - 10  # Ajuste vertical
                
                # Ajustar posición durante la animación de hover
                if juego["scale"] != 1.0:
                    offset = (self.boton_size * (juego["scale"] - 1)) // 2
                    img_x -= offset
                    img_y -= offset
                
                self.ventana.blit(juego["imagen_cargada"], (img_x, img_y))
            
            # Dibujar el nombre del juego (debajo del botón)
            nombre = self.fuente_boton.render(juego["nombre"], True, self.TEXTO)
            nombre_x = boton_x + self.boton_size//2 - nombre.get_width()//2
            nombre_y = boton_y + self.boton_size + 5  # Justo debajo del botón
            self.ventana.blit(nombre, (nombre_x, nombre_y))
            
            # Dibujar la descripción (debajo del nombre)
            desc = self.fuente_desc.render(juego["descripcion"], True, self.TEXTO)
            desc_x = boton_x + self.boton_size//2 - desc.get_width()//2
            desc_y = nombre_y + nombre.get_height() + 5
            self.ventana.blit(desc, (desc_x, desc_y))
    
    def lanzar_juego(self, juego):
        # Cerrar la ventana actual
        pygame.quit()
        
        try:
            # Importar el módulo y la clase del juego
            modulo = importlib.import_module(juego["modulo"])
            clase = getattr(modulo, juego["clase"])
            
            # Crear y ejecutar el juego
            instancia = clase()
            instancia.ejecutar()
        except Exception as e:
            print(f"Error al lanzar el juego {juego['nombre']}: {e}")
            # Reiniciar el menú en caso de error
            self.__init__()
            self.ejecutar()
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                start_x = (self.ancho - self.total_width) // 2
                
                for i, juego in enumerate(self.juegos):
                    boton_x = start_x + i * (self.boton_size + self.espacio_botones)
                    boton_y = 180
                    boton_rect = pygame.Rect(boton_x, boton_y, self.boton_size, self.boton_size)
                    
                    # Verificar clic considerando el escalado actual
                    scaled_rect = pygame.Rect(
                        boton_x - (self.boton_size * (juego["scale"] - 1)) // 2,
                        boton_y - (self.boton_size * (juego["scale"] - 1)) // 2,
                        self.boton_size * juego["scale"],
                        self.boton_size * juego["scale"]
                    )
                    
                    if scaled_rect.collidepoint(mouse_pos):
                        self.lanzar_juego(juego)
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        
        while True:
            self.manejar_eventos()
            self.dibujar_menu()
            pygame.display.flip()
            reloj.tick(60)


if __name__ == "__main__":
    menu = MenuGUI()
    menu.ejecutar()