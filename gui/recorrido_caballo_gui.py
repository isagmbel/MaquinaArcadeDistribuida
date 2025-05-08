import pygame
import sys
import os
from juegos.recorrido_caballo import RecorridoCaballo

class RecorridoCaballoGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init()
        self.tamaño = tamaño
        self.juego = RecorridoCaballo(tamaño)
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Recorrido del Caballo")
        
        # Colores pastel
        self.FONDO = (250, 240, 245)  # Rosa pastel muy claro
        self.CELDA_CLARA = (255, 255, 255)  # Blanco
        self.CELDA_OSCURA = (230, 230, 250)  # Lila pastel
        self.BORDE = (220, 180, 220)  # Lila más oscuro
        self.TEXTO = (100, 80, 100)  # Morado oscuro
        
        # Colores para botones
        self.BOTON_VERDE = (180, 230, 180)  # Verde pastel
        self.BOTON_ROJO = (255, 180, 180)   # Rojo pastel
        self.BOTON_AZUL = (180, 180, 230)   # Azul pastel
        self.BOTON_HOVER = (220, 220, 220)  # Gris claro para hover
        
        # Tamaño de cada celda
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        # Fuente
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        # Estado del juego
        self.modo = "jugar"
        self.solucion_actual = 0
        self.paso_actual = 1
        
        # Para el efecto hover
        self.celda_hover = None
        self.boton_hover = None
    
    def dibujar_tablero(self):
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                # Alternar colores del tablero
                color = self.CELDA_CLARA if (fila + col) % 2 == 0 else self.CELDA_OSCURA
                
                # Efecto hover - agrandar la celda
                hover_scale = 1.0
                if self.celda_hover == (fila, col):
                    hover_scale = 1.1
                    color = (min(color[0] + 20, 255), 
                            min(color[1] + 20, 255), 
                            min(color[2] + 20, 255))
                
                # Calcular posición con efecto hover
                celda_x = col * self.celda_ancho
                celda_y = fila * self.celda_alto
                celda_w = self.celda_ancho
                celda_h = self.celda_alto
                
                if hover_scale > 1.0:
                    celda_w = int(celda_w * hover_scale)
                    celda_h = int(celda_h * hover_scale)
                    celda_x = col * self.celda_ancho - (celda_w - self.celda_ancho) // 2
                    celda_y = fila * self.celda_alto - (celda_h - self.celda_alto) // 2
                
                pygame.draw.rect(
                    self.ventana, 
                    color, 
                    (celda_x, celda_y, celda_w, celda_h)
                )
                
                # Dibujar número si hay un movimiento
                valor = self.juego.tablero[fila][col]
                if valor != -1:
                    texto = self.fuente.render(str(valor), True, self.TEXTO)
                    self.ventana.blit(texto, 
                                    (col * self.celda_ancho + self.celda_ancho//2 - texto.get_width()//2,
                                     fila * self.celda_alto + self.celda_alto//2 - texto.get_height()//2))
                
                # Dibujar bordes
                pygame.draw.rect(
                    self.ventana, 
                    self.BORDE, 
                    (celda_x, celda_y, celda_w, celda_h), 
                    2
                )
    
    def dibujar_botones(self):
        botones = []
        
        if self.modo == "jugar":
            # Definir botones para modo jugar
            botones = [
                {"rect": pygame.Rect(10, self.alto - 40, 120, 30), "color": self.BOTON_VERDE, "texto": "Resolver"},
                {"rect": pygame.Rect(140, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Reiniciar"},
                {"rect": pygame.Rect(270, self.alto - 40, 120, 30), "color": self.BOTON_AZUL, "texto": "Verificar"}
            ]
            
            # Mostrar paso actual
            texto_paso = self.fuente.render(f"Paso: {self.paso_actual}", True, self.TEXTO)
            self.ventana.blit(texto_paso, (400, self.alto - 35))
        else:
            # Definir botones para modo ver soluciones
            botones = [
                {"rect": pygame.Rect(10, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Anterior"},
                {"rect": pygame.Rect(170, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Siguiente"},
                {"rect": pygame.Rect(330, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Volver"}
            ]
            
            # Mostrar solución actual
            texto_sol = self.fuente.render(f"Solución {self.solucion_actual + 1}/{len(self.juego.soluciones)}", True, self.TEXTO)
            self.ventana.blit(texto_sol, (460, self.alto - 35))
        
        # Dibujar botones con efecto hover
        self.boton_hover = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton in botones:
            hover = boton["rect"].collidepoint(mouse_pos)
            
            # Efecto hover - agrandar el botón
            if hover:
                self.boton_hover = boton["texto"]
                boton_rect = pygame.Rect(
                    boton["rect"].x - 5,
                    boton["rect"].y - 5,
                    boton["rect"].width + 10,
                    boton["rect"].height + 10
                )
                pygame.draw.rect(self.ventana, self.BOTON_HOVER, boton_rect, border_radius=5)
                pygame.draw.rect(self.ventana, (200, 200, 200), boton_rect, 2, border_radius=5)
            else:
                pygame.draw.rect(self.ventana, boton["color"], boton["rect"], border_radius=5)
                pygame.draw.rect(self.ventana, (200, 200, 200), boton["rect"], 2, border_radius=5)
            
            # Dibujar texto del botón
            texto = self.fuente.render(boton["texto"], True, self.TEXTO)
            self.ventana.blit(texto, 
                            (boton["rect"].x + boton["rect"].width//2 - texto.get_width()//2,
                             boton["rect"].y + boton["rect"].height//2 - texto.get_height()//2))
    
    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.celda_hover = None
        
        # Verificar hover en celdas del tablero
        if mouse_pos[1] < self.alto - 50:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                self.celda_hover = (fila, col)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Verificar clic en el tablero (modo jugar)
                if self.modo == "jugar" and y < self.alto - 50:
                    col = x // self.celda_ancho
                    fila = y // self.celda_alto
                    
                    if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                        if self.juego.mover_caballo(fila, col, self.paso_actual):
                            self.paso_actual += 1
                
                # Verificar clics en botones
                elif y > self.alto - 50:
                    if self.modo == "jugar":
                        # Botón de resolver
                        if 10 <= x <= 130:
                            soluciones = self.juego.encontrar_soluciones()
                            if soluciones:
                                self.modo = "ver_soluciones"
                                self.solucion_actual = 0
                                self.juego.tablero = [fila[:] for fila in soluciones[self.solucion_actual]]
                        
                        # Botón de reiniciar
                        elif 140 <= x <= 260:
                            self.juego.reiniciar()
                            self.paso_actual = 1
                        
                        # Botón de verificar
                        elif 270 <= x <= 390:
                            if self.juego.es_solucion_valida():
                                print("¡Correcto! Has encontrado una solución válida.")
                            else:
                                print("La configuración actual no es una solución válida.")
                    
                    else:  # modo ver_soluciones
                        # Botón de anterior solución
                        if 10 <= x <= 160:
                            self.solucion_actual = (self.solucion_actual - 1) % len(self.juego.soluciones)
                            self.juego.tablero = [fila[:] for fila in self.juego.soluciones[self.solucion_actual]]
                        
                        # Botón de siguiente solución
                        elif 170 <= x <= 320:
                            self.solucion_actual = (self.solucion_actual + 1) % len(self.juego.soluciones)
                            self.juego.tablero = [fila[:] for fila in self.juego.soluciones[self.solucion_actual]]
                        
                        # Botón de volver
                        elif 330 <= x <= 450:
                            self.modo = "jugar"
                            self.juego.reiniciar()
                            self.paso_actual = 1
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        
        while True:
            self.manejar_eventos()
            self.ventana.fill(self.FONDO)
            self.dibujar_tablero()
            self.dibujar_botones()
            pygame.display.flip()
            reloj.tick(60)

if __name__ == "__main__":
    juego_gui = RecorridoCaballoGUI(tamaño=8)
    juego_gui.ejecutar()