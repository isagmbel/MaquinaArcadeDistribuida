import pygame
import sys
from juegos.n_reinas import NReinas

class NReinasGUI:
    def __init__(self, tamaño=8, ancho=600, alto=600):
        pygame.init()
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")
        
        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.ROJO = (255, 0, 0)
        self.VERDE = (0, 255, 0)
        self.AZUL = (0, 0, 255)
        self.GRIS = (200, 200, 200)
        
        # Tamaño de cada celda
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = self.alto // self.tamaño
        
        # Fuente
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        # Estado del juego
        self.modo = "jugar"  # "jugar" o "ver_soluciones"
        self.solucion_actual = 0
    
    def dibujar_tablero(self):
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                # Alternar colores del tablero
                color = self.BLANCO if (fila + col) % 2 == 0 else self.GRIS
                pygame.draw.rect(
                    self.ventana, 
                    color, 
                    (col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto)
                )
                
                # Dibujar reina si existe
                if self.juego.tablero[fila][col] == 1:
                    self.dibujar_reina(col, fila)
                
                # Dibujar bordes
                pygame.draw.rect(
                    self.ventana, 
                    self.NEGRO, 
                    (col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto), 
                    1
                )
    
    def dibujar_reina(self, col, fila):
        # Centro de la celda
        centro_x = col * self.celda_ancho + self.celda_ancho // 2
        centro_y = fila * self.celda_alto + self.celda_alto // 2
        radio = min(self.celda_ancho, self.celda_alto) // 3
        
        # Dibujar la reina como un círculo
        pygame.draw.circle(self.ventana, self.ROJO, (centro_x, centro_y), radio)
        
        # Corona de la reina
        pygame.draw.circle(self.ventana, self.AZUL, (centro_x, centro_y), radio // 2, 2)
    
    def dibujar_botones(self):
        if self.modo == "jugar":
            # Botón de resolver
            pygame.draw.rect(self.ventana, self.VERDE, (10, self.alto - 40, 120, 30))
            texto = self.fuente.render("Resolver", True, self.NEGRO)
            self.ventana.blit(texto, (20, self.alto - 35))
            
            # Botón de reiniciar
            pygame.draw.rect(self.ventana, self.ROJO, (140, self.alto - 40, 120, 30))
            texto = self.fuente.render("Reiniciar", True, self.NEGRO)
            self.ventana.blit(texto, (150, self.alto - 35))
            
            # Botón de verificar
            pygame.draw.rect(self.ventana, self.AZUL, (270, self.alto - 40, 120, 30))
            texto = self.fuente.render("Verificar", True, self.NEGRO)
            self.ventana.blit(texto, (280, self.alto - 35))
        else:
            # Botón de anterior solución
            pygame.draw.rect(self.ventana, self.AZUL, (10, self.alto - 40, 150, 30))
            texto = self.fuente.render("Anterior", True, self.NEGRO)
            self.ventana.blit(texto, (20, self.alto - 35))
            
            # Botón de siguiente solución
            pygame.draw.rect(self.ventana, self.AZUL, (170, self.alto - 40, 150, 30))
            texto = self.fuente.render("Siguiente", True, self.NEGRO)
            self.ventana.blit(texto, (180, self.alto - 35))
            
            # Botón de volver
            pygame.draw.rect(self.ventana, self.ROJO, (330, self.alto - 40, 120, 30))
            texto = self.fuente.render("Volver", True, self.NEGRO)
            self.ventana.blit(texto, (350, self.alto - 35))
    
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                # Verificar si se hizo clic en el tablero (modo jugar)
                if self.modo == "jugar" and y < self.alto - 50:
                    col = x // self.celda_ancho
                    fila = y // self.celda_alto
                    
                    # Alternar reina en la posición
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
                            soluciones = self.juego.obtener_soluciones()
                            if soluciones:
                                self.modo = "ver_soluciones"
                                self.solucion_actual = 0
                                self.juego.tablero = [fila[:] for fila in soluciones[self.solucion_actual]]
                        
                        # Botón de reiniciar
                        elif 140 <= x <= 260:
                            self.juego.reiniciar()
                        
                        # Botón de verificar
                        elif 270 <= x <= 390:
                            if self.juego.es_solucion():
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
    
    def ejecutar(self):
        while True:
            self.manejar_eventos()
            self.ventana.fill(self.BLANCO)
            self.dibujar_tablero()
            self.dibujar_botones()
            pygame.display.flip()

if __name__ == "__main__":
    juego_gui = NReinasGUI(tamaño=8)
    juego_gui.ejecutar()