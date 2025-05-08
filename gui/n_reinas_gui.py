import pygame
import sys
import math
from juegos.n_reinas import NReinas

class NReinasGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init()
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")
        
        # Colores pastel
        self.FONDO = (250, 240, 245)  # Rosa pastel muy claro
        self.CELDA_CLARA = (255, 255, 255)  # Blanco
        self.CELDA_OSCURA = (230, 230, 250)  # Lila pastel
        self.BORDE = (220, 180, 220)  # Lila más oscuro
        self.TEXTO = (100, 80, 100)  # Morado oscuro
        
        # Colores para botones y reinas
        self.BOTON_VERDE = (180, 230, 180)  # Verde pastel
        self.BOTON_ROJO = (255, 180, 180)   # Rojo pastel
        self.BOTON_AZUL = (180, 180, 230)   # Azul pastel
        self.BOTON_HOVER = (220, 220, 220)  # Gris claro para hover
        self.REINA_COLOR = (255, 150, 180)  # Rosa fuerte
        self.REINA_CORONA = (255, 200, 220) # Rosa claro
        
        # Tamaño de cada celda
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        # Fuente
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        # Estado del juego
        self.modo = "jugar"
        self.solucion_actual = 0
        
        # Para el efecto hover
        self.celda_hover = None
        self.boton_hover = None
        self.hover_scale = 1.0  # Para animación suave
        self.target_scale = 1.0
    
    def dibujar_tablero(self):
        # Actualizar animación hover
        self.hover_scale += (self.target_scale - self.hover_scale) * 0.1
        
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                # Alternar colores del tablero
                color = self.CELDA_CLARA if (fila + col) % 2 == 0 else self.CELDA_OSCURA
                
                # Calcular posición y tamaño
                celda_x = col * self.celda_ancho
                celda_y = fila * self.celda_alto
                celda_w = self.celda_ancho
                celda_h = self.celda_alto
                
                # Aplicar efecto hover si es la celda bajo el mouse
                if self.celda_hover == (fila, col):
                    scale = self.hover_scale
                    celda_w = int(celda_w * scale)
                    celda_h = int(celda_h * scale)
                    celda_x = col * self.celda_ancho - (celda_w - self.celda_ancho) // 2
                    celda_y = fila * self.celda_alto - (celda_h - self.celda_alto) // 2
                    color = (min(color[0] + 20, 255), 
                            min(color[1] + 20, 255), 
                            min(color[2] + 20, 255))
                
                pygame.draw.rect(
                    self.ventana, 
                    color, 
                    (celda_x, celda_y, celda_w, celda_h)
                )
                
                # Dibujar reina si existe
                if self.juego.tablero[fila][col] == 1:
                    self.dibujar_reina(col, fila, scale if self.celda_hover == (fila, col) else 1.0)
                
                # Dibujar bordes (sin redondeo)
                pygame.draw.rect(
                    self.ventana, 
                    self.BORDE, 
                    (celda_x, celda_y, celda_w, celda_h), 
                    2
                )
    
    def dibujar_reina(self, col, fila, scale=1.0):
        # Centro de la celda
        centro_x = col * self.celda_ancho + self.celda_ancho // 2
        centro_y = fila * self.celda_alto + self.celda_alto // 2
        radio = min(self.celda_ancho, self.celda_alto) // 3 * scale
        
        # Dibujar la reina
        pygame.draw.circle(self.ventana, self.REINA_COLOR, (centro_x, centro_y), int(radio))
        
        # Corona de la reina
        pygame.draw.circle(self.ventana, self.REINA_CORONA, (centro_x, centro_y), int(radio * 0.6))
        
        # Puntitos de la corona
        for i in range(5):
            angle = i * (2 * math.pi / 5)
            crown_x = centro_x + int(radio * 0.8 * math.cos(angle))
            crown_y = centro_y + int(radio * 0.8 * math.sin(angle))
            pygame.draw.circle(self.ventana, self.REINA_COLOR, (crown_x, crown_y), int(radio * 0.15))
    
    def dibujar_botones(self):
        botones = []
        
        if self.modo == "jugar":
            # Definir botones para modo jugar
            botones = [
                {"rect": pygame.Rect(10, self.alto - 40, 120, 30), "color": self.BOTON_VERDE, "texto": "Resolver"},
                {"rect": pygame.Rect(140, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Reiniciar"},
                {"rect": pygame.Rect(270, self.alto - 40, 120, 30), "color": self.BOTON_AZUL, "texto": "Verificar"}
            ]
        else:
            # Definir botones para modo ver soluciones
            botones = [
                {"rect": pygame.Rect(10, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Anterior"},
                {"rect": pygame.Rect(170, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Siguiente"},
                {"rect": pygame.Rect(330, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Volver"}
            ]
            
            # Mostrar solución actual
            if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                texto_sol = self.fuente.render(f"Solución {self.solucion_actual + 1}/{len(self.juego.soluciones)}", True, self.TEXTO)
                self.ventana.blit(texto_sol, (460, self.alto - 35))
        
        # Dibujar botones con efecto hover
        self.boton_hover = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton in botones:
            hover = boton["rect"].collidepoint(mouse_pos)
            
            # Efecto hover
            if hover:
                self.boton_hover = boton["texto"]
                color = (
                    min(boton["color"][0] + 30, 255),
                    min(boton["color"][1] + 30, 255),
                    min(boton["color"][2] + 30, 255)
                )
            else:
                color = boton["color"]
            
            pygame.draw.rect(self.ventana, color, boton["rect"])
            pygame.draw.rect(self.ventana, (200, 200, 200), boton["rect"], 2)
            
            # Dibujar texto del botón
            texto = self.fuente.render(boton["texto"], True, self.TEXTO)
            self.ventana.blit(texto, 
                            (boton["rect"].x + boton["rect"].width//2 - texto.get_width()//2,
                             boton["rect"].y + boton["rect"].height//2 - texto.get_height()//2))
    
    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        nuevo_hover = None
        
        # Verificar hover en celdas del tablero
        if mouse_pos[1] < self.alto - 50:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                nuevo_hover = (fila, col)
        
        # Actualizar efecto hover
        if nuevo_hover != self.celda_hover:
            self.celda_hover = nuevo_hover
            self.target_scale = 1.1 if nuevo_hover else 1.0
        
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
                        if self.juego.tablero[fila][col] == 1:
                            self.juego.tablero[fila][col] = 0
                        else:
                            self.juego.tablero[fila][col] = 1
                
                # Verificar clics en botones
                elif y > self.alto - 50:
                    if self.modo == "jugar":
                        # Botón de resolver
                        if 10 <= x <= 130:
                            if hasattr(self.juego, 'obtener_soluciones'):
                                soluciones = self.juego.obtener_soluciones()
                                if soluciones:
                                    self.modo = "ver_soluciones"
                                    self.solucion_actual = 0
                                    self.juego.tablero = [fila[:] for fila in soluciones[self.solucion_actual]]
                        
                        # Botón de reiniciar
                        elif 140 <= x <= 260:
                            if hasattr(self.juego, 'reiniciar'):
                                self.juego.reiniciar()
                        
                        # Botón de verificar
                        elif 270 <= x <= 390:
                            if hasattr(self.juego, 'es_solucion'):
                                if self.juego.es_solucion():
                                    print("¡Correcto! Has encontrado una solución válida.")
                                else:
                                    print("La configuración actual no es una solución válida.")
                    
                    else:  # modo ver_soluciones
                        # Botón de anterior solución
                        if 10 <= x <= 160:
                            if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                self.solucion_actual = (self.solucion_actual - 1) % len(self.juego.soluciones)
                                self.juego.tablero = [fila[:] for fila in self.juego.soluciones[self.solucion_actual]]
                        
                        # Botón de siguiente solución
                        elif 170 <= x <= 320:
                            if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                self.solucion_actual = (self.solucion_actual + 1) % len(self.juego.soluciones)
                                self.juego.tablero = [fila[:] for fila in self.juego.soluciones[self.solucion_actual]]
                        
                        # Botón de volver
                        elif 330 <= x <= 450:
                            self.modo = "jugar"
                            if hasattr(self.juego, 'reiniciar'):
                                self.juego.reiniciar()
    
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
    juego_gui = NReinasGUI(tamaño=8)
    juego_gui.ejecutar()