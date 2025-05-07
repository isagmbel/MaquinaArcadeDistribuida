import sys
import os
# Añade el directorio raíz del proyecto al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pygame
import sys
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
        
        # Colores
        self.BLANCO = (255, 255, 255)
        self.NEGRO = (0, 0, 0)
        self.VERDE = (0, 200, 0)
        self.ROJO = (200, 0, 0)
        self.AZUL = (0, 0, 200)
        self.GRIS = (200, 200, 200)
        self.AMARILLO = (255, 255, 0)
        
        # Tamaño de cada celda
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        # Fuente
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        # Estado del juego
        self.modo = "jugar"  # "jugar" o "ver_soluciones"
        self.solucion_actual = 0
        self.paso_actual = 1
    
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
                
                # Dibujar número si hay un movimiento
                valor = self.juego.tablero[fila][col]
                if valor != -1:
                    texto = self.fuente.render(str(valor), True, self.NEGRO)
                    self.ventana.blit(texto, 
                                    (col * self.celda_ancho + self.celda_ancho//2 - texto.get_width()//2,
                                     fila * self.celda_alto + self.celda_alto//2 - texto.get_height()//2))
                
                # Dibujar bordes
                pygame.draw.rect(
                    self.ventana, 
                    self.NEGRO, 
                    (col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto), 
                    1
                )
    
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
            
            # Mostrar paso actual
            texto_paso = self.fuente.render(f"Paso: {self.paso_actual}", True, self.NEGRO)
            self.ventana.blit(texto_paso, (400, self.alto - 35))
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
            
            # Mostrar solución actual
            texto_sol = self.fuente.render(f"Solución {self.solucion_actual + 1}/{len(self.juego.soluciones)}", True, self.NEGRO)
            self.ventana.blit(texto_sol, (460, self.alto - 35))
    
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
        while True:
            self.manejar_eventos()
            self.ventana.fill(self.BLANCO)
            self.dibujar_tablero()
            self.dibujar_botones()
            pygame.display.flip()

if __name__ == "__main__":
    juego_gui = RecorridoCaballoGUI(tamaño=8)
    juego_gui.ejecutar()