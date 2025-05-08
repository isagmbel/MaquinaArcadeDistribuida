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
        
        # Colores pastel
        self.FONDO = (250, 240, 245)  # Rosa pastel muy claro
        self.BASE = (210, 180, 140)   # Marrón pastel
        self.POSTE = (200, 170, 130)   # Marrón pastel más claro
        self.DISCOS = [
            (255, 182, 193),  # Rosa claro
            (180, 230, 180),  # Verde pastel
            (180, 180, 230),  # Azul pastel
            (255, 255, 180),  # Amarillo pastel
            (230, 180, 230), # Lila pastel
            (180, 230, 230),  # Turquesa pastel
            (255, 200, 180), # Melocotón pastel
            (220, 200, 220)  # Lavanda
        ]
        self.TEXTO = (100, 80, 100)    # Morado oscuro
        self.BOTON = (200, 200, 220)    # Gris lila pastel
        self.BOTON_HOVER = (220, 220, 240)  # Gris lila más claro
        
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
        self.hover_torre = None
        self.hover_boton = None
    
    def dibujar_torres(self):
        # Dibujar base
        pygame.draw.rect(self.ventana, self.BASE, 
                        (50, self.base_y, self.ancho-100, self.base_altura))
        
        # Dibujar postes con efecto hover
        for i, x in enumerate(self.torre_pos_x):
            color = (min(self.POSTE[0] + 20, 255), 
                    min(self.POSTE[1] + 20, 255), 
                    min(self.POSTE[2] + 20, 255)) if self.hover_torre == i else self.POSTE
            
            pygame.draw.rect(self.ventana, color, 
                            (x - self.poste_ancho//2, self.base_y - self.poste_altura, 
                             self.poste_ancho, self.poste_altura))
        
        # Dibujar discos con efecto hover
        for torre_idx, torre in enumerate(self.juego.torres):
            for disco_idx, disco in enumerate(torre):
                ancho = self.disco_ancho_base - (self.disco_reduccion * (self.discos - disco))
                x = self.torre_pos_x[torre_idx] - ancho // 2
                y = self.base_y - self.base_altura - (disco_idx + 1) * self.disco_altura
                
                color_idx = (disco - 1) % len(self.DISCOS)
                color = self.DISCOS[color_idx]
                
                # Efecto hover para discos en la torre seleccionada
                if self.torre_origen == torre_idx and disco_idx == len(torre) - 1:
                    pygame.draw.rect(self.ventana, 
                                    (min(color[0] + 30, 255),
                                    min(color[1] + 30, 255),
                                    min(color[2] + 30, 255)), 
                                    (x - 5, y - 5, ancho + 10, self.disco_altura + 10))
                
                pygame.draw.rect(self.ventana, color, (x, y, ancho, self.disco_altura))
                pygame.draw.rect(self.ventana, self.TEXTO, (x, y, ancho, self.disco_altura), 2)
    
    def dibujar_ui(self):
        # Dibujar información
        movimientos_texto = self.fuente.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})", 
            True, self.TEXTO)
        self.ventana.blit(movimientos_texto, (20, 20))
        
        if self.juego.esta_resuelto():
            felicitacion = self.fuente_titulo.render("¡Resuelto!", True, (100, 180, 100))
            self.ventana.blit(felicitacion, 
                            (self.ancho//2 - felicitacion.get_width()//2, 50))
        
        # Dibujar botones con efecto hover
        botones = [
            {"texto": "Reiniciar", "pos": (self.ancho - 220, 20), "accion": self.juego.reiniciar},
            {"texto": "Resolver", "pos": (self.ancho - 220, 60), "accion": self.resolver_automatico},
            {"texto": "Deshacer", "pos": (self.ancho - 220, 100), "accion": self.juego.deshacer_ultimo_movimiento}
        ]
        
        self.hover_boton = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton in botones:
            x, y = boton["pos"]
            rect = pygame.Rect(x, y, 150, 30)
            hover = rect.collidepoint(mouse_pos)
            
            if hover:
                self.hover_boton = boton["texto"]
            
            color = self.BOTON_HOVER if hover else self.BOTON
            pygame.draw.rect(self.ventana, color, rect)
            pygame.draw.rect(self.ventana, self.TEXTO, rect, 2)
            
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
        mouse_pos = pygame.mouse.get_pos()
        
        # Detectar hover en torres
        self.hover_torre = None
        for i, x in enumerate(self.torre_pos_x):
            if (x - 100 <= mouse_pos[0] <= x + 100 and 
                self.base_y - self.poste_altura <= mouse_pos[1] <= self.base_y):
                self.hover_torre = i
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN and not self.resolviendo:
                # Verificar clic en botones
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
                if self.hover_torre is not None:
                    if self.torre_origen is None:
                        if self.juego.torres[self.hover_torre]:
                            self.torre_origen = self.hover_torre
                    else:
                        if self.juego.mover_disco(self.torre_origen, self.hover_torre):
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