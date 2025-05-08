import pygame
import sys
import math
from pathlib import Path # Para pruebas directas en __main__

# --- MODIFICACIONES ---
from cliente.juegos.n_reinas import NReinas
from cliente.comunicacion.cliente_network import get_network_client
# --- FIN MODIFICACIONES ---

class NReinasGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init() # Necesario porque menu_gui hace pygame.quit()
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        
        # --- MODIFICACIONES ---
        self.network_client = get_network_client()
        self.intentos_nreinas = 0 # Contador de intentos de verificación
        # --- FIN MODIFICACIONES ---

        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")
        
        self.FONDO = (250, 240, 245)
        self.CELDA_CLARA = (255, 255, 255)
        self.CELDA_OSCURA = (230, 230, 250)
        self.BORDE = (220, 180, 220)
        self.TEXTO = (100, 80, 100)
        
        self.BOTON_VERDE = (180, 230, 180)
        self.BOTON_ROJO = (255, 180, 180)
        self.BOTON_AZUL = (180, 180, 230)
        self.BOTON_HOVER_COLOR = (220, 220, 220) # Renombrado para claridad
        self.REINA_COLOR = (255, 150, 180)
        self.REINA_CORONA = (255, 200, 220)
        
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        self.modo = "jugar" # "jugar", "ver_soluciones"
        self.solucion_actual_idx = 0 # Renombrado para claridad
        
        self.celda_hover = None
        self.boton_hover_texto = None # Renombrado para claridad
        self.hover_scale_anim = 1.0 # Renombrado para claridad
        self.target_scale_anim = 1.0 # Renombrado para claridad
    
    def dibujar_tablero(self):
        self.hover_scale_anim += (self.target_scale_anim - self.hover_scale_anim) * 0.1
        
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color_base = self.CELDA_CLARA if (fila + col) % 2 == 0 else self.CELDA_OSCURA
                
                celda_x_base = col * self.celda_ancho
                celda_y_base = fila * self.celda_alto
                celda_w_base = self.celda_ancho
                celda_h_base = self.celda_alto
                
                current_scale = 1.0
                color_draw = color_base
                celda_x_draw, celda_y_draw = celda_x_base, celda_y_base
                celda_w_draw, celda_h_draw = celda_w_base, celda_h_base

                if self.celda_hover == (fila, col):
                    current_scale = self.hover_scale_anim
                    celda_w_draw = int(celda_w_base * current_scale)
                    celda_h_draw = int(celda_h_base * current_scale)
                    celda_x_draw = celda_x_base - (celda_w_draw - celda_w_base) // 2
                    celda_y_draw = celda_y_base - (celda_h_draw - celda_h_base) // 2
                    color_draw = (min(color_base[0] + 20, 255), 
                                  min(color_base[1] + 20, 255), 
                                  min(color_base[2] + 20, 255))
                
                pygame.draw.rect(self.ventana, color_draw, (celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw))
                
                if self.juego.tablero[fila][col] == 1:
                    self.dibujar_reina(col, fila, current_scale) # Pasar current_scale para reina
                
                pygame.draw.rect(self.ventana, self.BORDE, (celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw), 2)
    
    def dibujar_reina(self, col, fila, scale=1.0):
        # Centro de la celda base (no la dibujada, para que la reina no se mueva erráticamente con el hover de la celda)
        centro_x = col * self.celda_ancho + self.celda_ancho // 2
        centro_y = fila * self.celda_alto + self.celda_alto // 2
        radio_base = min(self.celda_ancho, self.celda_alto) // 3
        radio_scaled = int(radio_base * scale) # Escalar el radio de la reina
        
        pygame.draw.circle(self.ventana, self.REINA_COLOR, (centro_x, centro_y), radio_scaled)
        pygame.draw.circle(self.ventana, self.REINA_CORONA, (centro_x, centro_y), int(radio_scaled * 0.6))
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2 # Ajustar ángulo para que un pico apunte arriba
            crown_x = centro_x + int(radio_scaled * 0.8 * math.cos(angle))
            crown_y = centro_y + int(radio_scaled * 0.8 * math.sin(angle))
            pygame.draw.circle(self.ventana, self.REINA_COLOR, (crown_x, crown_y), int(radio_scaled * 0.15))
    
    def dibujar_botones(self):
        botones_info = []
        if self.modo == "jugar":
            botones_info = [
                {"rect": pygame.Rect(10, self.alto - 40, 120, 30), "color": self.BOTON_VERDE, "texto": "Resolver"},
                {"rect": pygame.Rect(140, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Reiniciar"},
                {"rect": pygame.Rect(270, self.alto - 40, 120, 30), "color": self.BOTON_AZUL, "texto": "Verificar"}
            ]
        else: # modo ver_soluciones
            botones_info = [
                {"rect": pygame.Rect(10, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Anterior"},
                {"rect": pygame.Rect(170, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Siguiente"},
                {"rect": pygame.Rect(330, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Volver"}
            ]
            if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                texto_sol = self.fuente.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.TEXTO)
                self.ventana.blit(texto_sol, (460, self.alto - 35))
        
        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw = boton_data["color"]
            rect_draw = boton_data["rect"]

            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.BOTON_HOVER_COLOR
                rect_draw = pygame.Rect(boton_data["rect"].x - 2, boton_data["rect"].y - 2, 
                                        boton_data["rect"].width + 4, boton_data["rect"].height + 4)

            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=5)
            pygame.draw.rect(self.ventana, (150,150,150), rect_draw, 2, border_radius=5)
            
            texto = self.fuente.render(boton_data["texto"], True, self.TEXTO)
            self.ventana.blit(texto, 
                            (boton_data["rect"].centerx - texto.get_width()//2,
                             boton_data["rect"].centery - texto.get_height()//2))

    # --- MODIFICACIONES ---
    def _guardar_resultado_nreinas(self, exito: bool):
        print(f"[NReinasGUI] Guardando: N={self.tamaño}, Éxito={exito}, Intentos={self.intentos_nreinas}")

        def callback_guardado(response):
            if response and response.get("status") == "ok":
                print(f"[NReinasGUI] Puntuación guardada: {response.get('message')}")
            else:
                msg = response.get('message') if response else "Error desconocido"
                print(f"[NReinasGUI] Error al guardar puntuación: {msg}")
        
        self.network_client.save_n_reinas_score(
            n_value=self.tamaño,
            success=exito,
            attempts=self.intentos_nreinas,
            callback=callback_guardado
        )
    # --- FIN MODIFICACIONES ---

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        nuevo_hover_celda = None
        if mouse_pos[1] < self.alto - 50: # Si el mouse está sobre el tablero
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                nuevo_hover_celda = (fila, col)
        
        if nuevo_hover_celda != self.celda_hover:
            self.celda_hover = nuevo_hover_celda
            self.target_scale_anim = 1.1 if nuevo_hover_celda else 1.0
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False # Para salir del bucle ejecutar

            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if self.modo == "jugar" and y < self.alto - 50: # Clic en tablero
                    col = x // self.celda_ancho
                    fila = y // self.celda_alto
                    if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                        self.juego.tablero[fila][col] = 1 - self.juego.tablero[fila][col] # Toggle
                
                elif y >= self.alto - 50: # Clic en zona de botones
                    botones_jugar = [
                        {"r": pygame.Rect(10, self.alto - 40, 120, 30), "accion": "resolver"},
                        {"r": pygame.Rect(140, self.alto - 40, 120, 30), "accion": "reiniciar"},
                        {"r": pygame.Rect(270, self.alto - 40, 120, 30), "accion": "verificar"}
                    ]
                    botones_ver_sol = [
                        {"r": pygame.Rect(10, self.alto - 40, 150, 30), "accion": "anterior"},
                        {"r": pygame.Rect(170, self.alto - 40, 150, 30), "accion": "siguiente"},
                        {"r": pygame.Rect(330, self.alto - 40, 120, 30), "accion": "volver"}
                    ]
                    botones_actuales = botones_jugar if self.modo == "jugar" else botones_ver_sol

                    for boton_info in botones_actuales:
                        if boton_info["r"].collidepoint(x, y):
                            accion = boton_info["accion"]
                            if accion == "resolver":
                                if hasattr(self.juego, 'obtener_soluciones'):
                                    soluciones = self.juego.obtener_soluciones()
                                    if soluciones:
                                        self.modo = "ver_soluciones"
                                        self.solucion_actual_idx = 0
                                        self.juego.tablero = [fila_sol[:] for fila_sol in soluciones[self.solucion_actual_idx]]
                                        # Considerar si se guarda la primera solución encontrada automáticamente
                                        # self.intentos_nreinas += 1 # Si resolver cuenta como intento
                                        # self._guardar_resultado_nreinas(exito=True)
                            elif accion == "reiniciar":
                                if hasattr(self.juego, 'reiniciar'):
                                    self.juego.reiniciar()
                                    self.intentos_nreinas = 0 # Reiniciar contador de intentos
                            elif accion == "verificar":
                                self.intentos_nreinas += 1 # Incrementar intento
                                if hasattr(self.juego, 'es_solucion'):
                                    es_valida = self.juego.es_solucion()
                                    if es_valida:
                                        print("¡Correcto! Has encontrado una solución válida.")
                                    else:
                                        print("La configuración actual no es una solución válida.")
                                    self._guardar_resultado_nreinas(exito=es_valida) # Guardar
                            elif accion == "anterior":
                                if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                    self.solucion_actual_idx = (self.solucion_actual_idx - 1 + len(self.juego.soluciones)) % len(self.juego.soluciones)
                                    self.juego.tablero = [fila_sol[:] for fila_sol in self.juego.soluciones[self.solucion_actual_idx]]
                            elif accion == "siguiente":
                                if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                    self.solucion_actual_idx = (self.solucion_actual_idx + 1) % len(self.juego.soluciones)
                                    self.juego.tablero = [fila_sol[:] for fila_sol in self.juego.soluciones[self.solucion_actual_idx]]
                            elif accion == "volver":
                                self.modo = "jugar"
                                if hasattr(self.juego, 'reiniciar'):
                                    self.juego.reiniciar() # No reiniciar self.intentos_nreinas aquí, se mantiene
                            break # Acción de botón encontrada
        return True # Seguir ejecutando
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            self.ventana.fill(self.FONDO)
            self.dibujar_tablero()
            self.dibujar_botones()
            pygame.display.flip()
            reloj.tick(60)
        print("[NReinasGUI] Saliendo del juego.")

if __name__ == "__main__":
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2] 
    sys.path.append(str(PROJECT_ROOT_TEST))
    
    juego_gui = NReinasGUI(tamaño=8)
    juego_gui.ejecutar()
    pygame.quit()
    sys.exit()