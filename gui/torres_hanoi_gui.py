import pygame
import sys
import time
from juegos.torres_hanoi import TorresHanoi

class TorresHanoiGUI:
    def __init__(self, discos=3, ancho=800, alto=600):
        pygame.init()
        self.discos = discos
        self.juego = TorresHanoi(discos)
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Torres de Hanoi")
        
        # Colores
        self.FONDO = (240, 240, 240)
        self.BASE = (139, 69, 19)  # Marrón
        self.POSTE = (160, 82, 45)  # Marrón más claro
        self.DISCOS = [
            (255, 0, 0),    # Rojo
            (0, 255, 0),    # Verde
            (0, 0, 255),    # Azul
            (255, 255, 0),  # Amarillo
            (255, 0, 255), # Magenta
            (0, 255, 255), # Cian
            (255, 128, 0), # Naranja
            (128, 0, 128)  # Púrpura
        ]
        self.TEXTO = (0, 0, 0)
        self.BOTON = (70, 130, 200)
        self.BOTON_HOVER = (100, 160, 230)
        
        # Dimensiones
        self.base_altura = 20
        self.poste_ancho = 20
        self.poste_altura = 300
        self.disco_altura = 30
        self.disco_ancho_base = 150
        self.disco_reduccion = 20
        
        # Posiciones de las torres
        self.torre_pos_x = [ancho//4, ancho//2, 3*ancho//4]
        self.base_y = alto - 50
        
        # Fuentes
        self.fuente = pygame.font.SysFont('Arial', 24)
        self.fuente_titulo = pygame.font.SysFont('Arial', 36, bold=True)
        
        # Estado del juego
        self.disco_seleccionado = None
        self.torre_origen = None
        self.resolviendo = False
        self.pasos_solucion = []
        self.paso_actual = 0
    
    def dibujar_torres(self):
        # Dibujar base
        pygame.draw.rect(self.ventana, self.BASE, 
                        (50, self.base_y, self.ancho-100, self.base_altura))
        
        # Dibujar postes
        for x in self.torre_pos_x:
            pygame.draw.rect(self.ventana, self.POSTE, 
                            (x - self.poste_ancho//2, self.base_y - self.poste_altura, 
                             self.poste_ancho, self.poste_altura))
        
        # Dibujar discos
        for torre_idx, torre in enumerate(self.juego.torres):
            for disco_idx, disco in enumerate(torre):
                ancho = self.disco_ancho_base - (self.disco_reduccion * (self.discos - disco))
                x = self.torre_pos_x[torre_idx] - ancho // 2
                y = self.base_y - self.base_altura - (disco_idx + 1) * self.disco_altura
                
                color = self.DISCOS[(disco - 1) % len(self.DISCOS)]
                pygame.draw.rect(self.ventana, color, (x, y, ancho, self.disco_altura))
                pygame.draw.rect(self.ventana, self.TEXTO, (x, y, ancho, self.disco_altura), 2)
    
    def dibujar_ui(self):
        # Dibujar información
        movimientos_texto = self.fuente.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})", 
            True, self.TEXTO)
        self.ventana.blit(movimientos_texto, (20, 20))
        
        if self.juego.esta_resuelto():
            felicitacion = self.fuente_titulo.render("¡Resuelto!", True, (0, 150, 0))
            self.ventana.blit(felicitacion, 
                            (self.ancho//2 - felicitacion.get_width()//2, 50))
        
        # Dibujar botones
        botones = [
            {"texto": "Reiniciar", "pos": (self.ancho - 220, 20), "accion": self.juego.reiniciar},
            {"texto": "Resolver", "pos": (self.ancho - 220, 60), "accion": self.resolver_automatico},
            {"texto": "Deshacer", "pos": (self.ancho - 220, 100), "accion": self.juego.deshacer_ultimo_movimiento}
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        for boton in botones:
            x, y = boton["pos"]
            hover = x <= mouse_pos[0] <= x + 150 and y <= mouse_pos[1] <= y + 30
            
            color = self.BOTON_HOVER if hover else self.BOTON
            pygame.draw.rect(self.ventana, color, (x, y, 150, 30))
            pygame.draw.rect(self.ventana, self.TEXTO, (x, y, 150, 30), 2)
            
            texto = self.fuente.render(boton["texto"], True, self.TEXTO)
            self.ventana.blit(texto, (x + 75 - texto.get_width()//2, y + 15 - texto.get_height()//2))
    
    def resolver_automatico(self):
        if not self.resolviendo:
            self.resolviendo = True
            self.pasos_solucion = []
            self.juego.reiniciar()
            self._generar_solucion(self.discos, 0, 2, 1)
            self.paso_actual = 0
    
    def _generar_solucion(self, n, origen, destino, auxiliar):
        if n == 0:
            return
        self._generar_solucion(n-1, origen, auxiliar, destino)
        self.pasos_solucion.append((origen, destino))
        self._generar_solucion(n-1, auxiliar, destino, origen)
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN and not self.resolviendo:
                # Verificar clic en botones
                mouse_pos = pygame.mouse.get_pos()
                botones = [
                    {"rect": pygame.Rect(self.ancho - 220, 20, 150, 30), "accion": self.juego.reiniciar},
                    {"rect": pygame.Rect(self.ancho - 220, 60, 150, 30), "accion": self.resolver_automatico},
                    {"rect": pygame.Rect(self.ancho - 220, 100, 150, 30), "accion": self.juego.deshacer_ultimo_movimiento}
                ]
                
                for boton in botones:
                    if boton["rect"].collidepoint(mouse_pos):
                        boton["accion"]()
                        return
                
                # Verificar clic en torres
                for torre_idx, x in enumerate(self.torre_pos_x):
                    if (x - 100 <= mouse_pos[0] <= x + 100 and 
                        self.base_y - self.poste_altura <= mouse_pos[1] <= self.base_y):
                        
                        if self.torre_origen is None:
                            if self.juego.torres[torre_idx]:
                                self.torre_origen = torre_idx
                        else:
                            if self.juego.mover_disco(self.torre_origen, torre_idx):
                                if self.juego.esta_resuelto():
                                    print("¡Felicidades! Has resuelto el puzzle.")
                            self.torre_origen = None
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:  # Tecla R para reiniciar
                    self.juego.reiniciar()
                    self.resolviendo = False
                elif evento.key == pygame.K_s:  # Tecla S para resolver
                    self.resolver_automatico()
                elif evento.key == pygame.K_u:  # Tecla U para deshacer
                    self.juego.deshacer_ultimo_movimiento()
    
    def actualizar_automatico(self):
        if self.resolviendo and self.paso_actual < len(self.pasos_solucion):
            origen, destino = self.pasos_solucion[self.paso_actual]
            self.juego.mover_disco(origen, destino)
            self.paso_actual += 1
            time.sleep(0.5)  # Pausa para visualización
        else:
            self.resolviendo = False
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        
        while True:
            self.manejar_eventos()
            
            if self.resolviendo:
                self.actualizar_automatico()
            
            self.ventana.fill(self.FONDO)
            self.dibujar_torres()
            self.dibujar_ui()
            pygame.display.flip()
            reloj.tick(30)

if __name__ == "__main__":
    juego = TorresHanoiGUI(discos=5)
    juego.ejecutar()