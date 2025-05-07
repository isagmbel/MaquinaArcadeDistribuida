import pygame
import sys
import os
import importlib
import subprocess

class MenuGUI:
    def __init__(self, ancho=800, alto=600):
        pygame.init()
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Arcade Machine")
        
        # Colores
        self.FONDO = (40, 44, 52)
        self.TITULO = (255, 255, 255)
        self.BOTON = (86, 182, 194)
        self.BOTON_HOVER = (120, 210, 220)
        self.TEXTO = (0, 0, 0)
        
        # Fuentes
        self.fuente_titulo = pygame.font.SysFont('Arial', 48, bold=True)
        self.fuente_boton = pygame.font.SysFont('Arial', 28)
        
        # Juegos disponibles
        self.juegos = [
            {
                "nombre": "N Reinas",
                "modulo": "gui.n_reinas_gui",
                "clase": "NReinasGUI",
                "descripcion": "Coloca N reinas en un tablero sin que se amenacen"
            },
            {
                "nombre": "Recorrido del Caballo",
                "modulo": "gui.recorrido_caballo_gui",
                "clase": "RecorridoCaballoGUI",
                "descripcion": "Recorre todo el tablero con un caballo sin repetir casillas"
            },
            {
                "nombre": "Torres de Hanoi",
                "modulo": "gui.torres_hanoi_gui",
                "clase": "TorresHanoiGUI",
                "descripcion": "Mueve todos los discos de una torre a otra"
            }
        ]
    
    def dibujar_menu(self):
        # Dibujar fondo
        self.ventana.fill(self.FONDO)
        
        # Dibujar título
        titulo = self.fuente_titulo.render("Arcade Machine", True, self.TITULO)
        self.ventana.blit(titulo, (self.ancho//2 - titulo.get_width()//2, 50))
        
        # Dibujar botones de juegos
        mouse_pos = pygame.mouse.get_pos()
        
        for i, juego in enumerate(self.juegos):
            # Calcular posición del botón
            boton_x = self.ancho//2 - 200
            boton_y = 150 + i * 120
            boton_rect = pygame.Rect(boton_x, boton_y, 400, 80)
            
            # Verificar si el ratón está sobre el botón
            hover = boton_rect.collidepoint(mouse_pos)
            color = self.BOTON_HOVER if hover else self.BOTON
            
            # Dibujar el botón
            pygame.draw.rect(self.ventana, color, boton_rect)
            pygame.draw.rect(self.ventana, self.TITULO, boton_rect, 2)
            
            # Dibujar el nombre del juego
            nombre = self.fuente_boton.render(juego["nombre"], True, self.TEXTO)
            self.ventana.blit(nombre, (boton_x + 200 - nombre.get_width()//2, boton_y + 20 - nombre.get_height()//2))
            
            # Dibujar la descripción
            desc = pygame.font.SysFont('Arial', 16).render(juego["descripcion"], True, self.TEXTO)
            self.ventana.blit(desc, (boton_x + 200 - desc.get_width()//2, boton_y + 50))
    
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
                
                # Verificar clics en los botones de juegos
                for i, juego in enumerate(self.juegos):
                    boton_x = self.ancho//2 - 200
                    boton_y = 150 + i * 120
                    boton_rect = pygame.Rect(boton_x, boton_y, 400, 80)
                    
                    if boton_rect.collidepoint(mouse_pos):
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