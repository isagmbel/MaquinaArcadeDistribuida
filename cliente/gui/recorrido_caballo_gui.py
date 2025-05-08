import pygame
import sys
# import os # No se usa directamente aquí
from pathlib import Path # Para pruebas directas en __main__

# --- MODIFICACIONES ---
# Importar lógica del juego desde el paquete cliente
from cliente.juegos.recorrido_caballo import RecorridoCaballo
# Importar cliente de red
from cliente.comunicacion.cliente_network import get_network_client
# --- FIN MODIFICACIONES ---

class RecorridoCaballoGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init() # Necesario porque menu_gui hace pygame.quit()
        self.tamaño = tamaño
        self.juego = RecorridoCaballo(tamaño)

        # --- MODIFICACIONES ---
        self.network_client = get_network_client()
        self.posicion_inicial_caballo = None # Para guardar la primera casilla clicada
        self.resultado_guardado_este_intento = False # Para evitar guardados múltiples por verificación
        # --- FIN MODIFICACIONES ---
        
        # Configuración de la ventana
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Recorrido del Caballo")
        
        # Colores pastel
        self.FONDO = (250, 240, 245)
        self.CELDA_CLARA = (255, 255, 255)
        self.CELDA_OSCURA = (230, 230, 250)
        self.BORDE = (220, 180, 220)
        self.TEXTO = (100, 80, 100)
        
        self.BOTON_VERDE = (180, 230, 180)
        self.BOTON_ROJO = (255, 180, 180)
        self.BOTON_AZUL = (180, 180, 230)
        self.BOTON_HOVER = (220, 220, 220)
        
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        self.fuente = pygame.font.SysFont('Arial', 24)
        
        self.modo = "jugar"
        self.solucion_actual = 0
        self.paso_actual = 1
        
        self.celda_hover = None
        self.boton_hover = None
    
    def dibujar_tablero(self):
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color = self.CELDA_CLARA if (fila + col) % 2 == 0 else self.CELDA_OSCURA
                hover_scale = 1.0
                if self.celda_hover == (fila, col):
                    hover_scale = 1.1
                    color = (min(color[0] + 20, 255), 
                            min(color[1] + 20, 255), 
                            min(color[2] + 20, 255))
                
                celda_x_base = col * self.celda_ancho
                celda_y_base = fila * self.celda_alto
                celda_w_base = self.celda_ancho
                celda_h_base = self.celda_alto
                
                celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw = celda_x_base, celda_y_base, celda_w_base, celda_h_base

                if hover_scale > 1.0:
                    celda_w_draw = int(celda_w_base * hover_scale)
                    celda_h_draw = int(celda_h_base * hover_scale)
                    celda_x_draw = celda_x_base - (celda_w_draw - celda_w_base) // 2
                    celda_y_draw = celda_y_base - (celda_h_draw - celda_h_base) // 2
                
                pygame.draw.rect(self.ventana, color, (celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw))
                
                valor = self.juego.tablero[fila][col]
                if valor != -1:
                    texto = self.fuente.render(str(valor), True, self.TEXTO)
                    self.ventana.blit(texto, 
                                    (celda_x_base + celda_w_base//2 - texto.get_width()//2,
                                     celda_y_base + celda_h_base//2 - texto.get_height()//2))
                
                pygame.draw.rect(self.ventana, self.BORDE, (celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw), 2)
    
    def dibujar_botones(self):
        botones_info = []
        if self.modo == "jugar":
            botones_info = [
                {"rect": pygame.Rect(10, self.alto - 40, 120, 30), "color": self.BOTON_VERDE, "texto": "Resolver"},
                {"rect": pygame.Rect(140, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Reiniciar"},
                {"rect": pygame.Rect(270, self.alto - 40, 120, 30), "color": self.BOTON_AZUL, "texto": "Verificar"}
            ]
            texto_paso = self.fuente.render(f"Paso: {self.paso_actual}", True, self.TEXTO)
            self.ventana.blit(texto_paso, (400, self.alto - 35))
        else: # modo ver_soluciones
            botones_info = [
                {"rect": pygame.Rect(10, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Anterior"},
                {"rect": pygame.Rect(170, self.alto - 40, 150, 30), "color": self.BOTON_AZUL, "texto": "Siguiente"},
                {"rect": pygame.Rect(330, self.alto - 40, 120, 30), "color": self.BOTON_ROJO, "texto": "Volver"}
            ]
            if self.juego.soluciones:
                 texto_sol = self.fuente.render(f"Solución {self.solucion_actual + 1}/{len(self.juego.soluciones)}", True, self.TEXTO)
                 self.ventana.blit(texto_sol, (460, self.alto - 35))
        
        self.boton_hover = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            rect_draw = boton_data["rect"]
            color_draw = boton_data["color"]

            if hover:
                self.boton_hover = boton_data["texto"]
                rect_draw = pygame.Rect(boton_data["rect"].x - 2, boton_data["rect"].y - 2, 
                                        boton_data["rect"].width + 4, boton_data["rect"].height + 4)
                color_draw = self.BOTON_HOVER
            
            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=5)
            pygame.draw.rect(self.ventana, (150,150,150), rect_draw, 2, border_radius=5) # Borde más oscuro
            
            texto = self.fuente.render(boton_data["texto"], True, self.TEXTO)
            self.ventana.blit(texto, 
                            (boton_data["rect"].centerx - texto.get_width()//2,
                             boton_data["rect"].centery - texto.get_height()//2))

    # --- MODIFICACIONES ---
    def _guardar_resultado_caballo(self, completitud: bool):
        if self.resultado_guardado_este_intento:
            print("[RecorridoCaballoGUI] Resultado ya guardado para este intento/verificación.")
            return

        if self.posicion_inicial_caballo is None and self.paso_actual > 1:
            # Intentar inferir la primera posición si no se guardó (ej. si se cargó una solución)
            # Esto es una heurística, idealmente se captura al primer clic.
            for r in range(self.tamaño):
                for c in range(self.tamaño):
                    if self.juego.tablero[r][c] == 1:
                        self.posicion_inicial_caballo = (r,c)
                        break
                if self.posicion_inicial_caballo:
                    break
        
        pos_inicial_str = str(self.posicion_inicial_caballo) if self.posicion_inicial_caballo else "No definida"
        mov_realizados = self.paso_actual -1 if self.paso_actual > 0 else 0 # Movimientos completados

        print(f"[RecorridoCaballoGUI] Guardando: Posición Inicial={pos_inicial_str}, Movimientos={mov_realizados}, Completado={completitud}")

        def callback_guardado(response):
            if response and response.get("status") == "ok":
                print(f"[RecorridoCaballoGUI] Puntuación guardada: {response.get('message')}")
            else:
                msg = response.get('message') if response else "Error desconocido"
                print(f"[RecorridoCaballoGUI] Error al guardar puntuación: {msg}")

        self.network_client.save_knights_tour_score(
            start_position=pos_inicial_str,
            moves_made=mov_realizados,
            completed=completitud,
            callback=callback_guardado
        )
        self.resultado_guardado_este_intento = True # Marcar como guardado para este intento
    # --- FIN MODIFICACIONES ---

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.celda_hover = None
        if mouse_pos[1] < self.alto - 50: # Si el mouse está sobre el tablero
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                self.celda_hover = (fila, col)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False # Para salir del bucle ejecutar

            if evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                
                if self.modo == "jugar" and y < self.alto - 50: # Clic en tablero
                    col = x // self.celda_ancho
                    fila = y // self.celda_alto
                    if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                        if self.juego.mover_caballo(fila, col, self.paso_actual):
                            if self.paso_actual == 1: # Primer movimiento
                                self.posicion_inicial_caballo = (fila, col)
                            self.paso_actual += 1
                            self.resultado_guardado_este_intento = False # Permitir nuevo guardado si verifica
                
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
                                self.resultado_guardado_este_intento = False # Resetear para posible guardado de la solución
                                soluciones = self.juego.encontrar_soluciones()
                                if soluciones:
                                    self.modo = "ver_soluciones"
                                    self.solucion_actual = 0
                                    self.juego.tablero = [fila_sol[:] for fila_sol in soluciones[self.solucion_actual]]
                                    # Considerar si se guarda la solución encontrada automáticamente.
                                    # self._guardar_resultado_caballo(completitud=True)
                            elif accion == "reiniciar":
                                self.juego.reiniciar()
                                self.paso_actual = 1
                                self.posicion_inicial_caballo = None
                                self.resultado_guardado_este_intento = False
                            elif accion == "verificar":
                                es_valida = self.juego.es_solucion_valida()
                                if es_valida:
                                    print("¡Correcto! Has encontrado una solución válida.")
                                else:
                                    print("La configuración actual no es una solución válida.")
                                self._guardar_resultado_caballo(completitud=es_valida)
                            elif accion == "anterior":
                                if self.juego.soluciones:
                                    self.solucion_actual = (self.solucion_actual - 1 + len(self.juego.soluciones)) % len(self.juego.soluciones)
                                    self.juego.tablero = [fila_sol[:] for fila_sol in self.juego.soluciones[self.solucion_actual]]
                            elif accion == "siguiente":
                                if self.juego.soluciones:
                                    self.solucion_actual = (self.solucion_actual + 1) % len(self.juego.soluciones)
                                    self.juego.tablero = [fila_sol[:] for fila_sol in self.juego.soluciones[self.solucion_actual]]
                            elif accion == "volver":
                                self.modo = "jugar"
                                self.juego.reiniciar()
                                self.paso_actual = 1
                                self.posicion_inicial_caballo = None
                                self.resultado_guardado_este_intento = False
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
        print("[RecorridoCaballoGUI] Saliendo del juego.")
        # No hacer pygame.quit() aquí, el menú lo maneja o se encarga de reinit.

if __name__ == "__main__":
    # Para probar RecorridoCaballoGUI directamente
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2] # MAQUINADEARCADE
    sys.path.append(str(PROJECT_ROOT_TEST))
    
    # Para que el servidor de prueba funcione, necesitarías iniciarlo en otro hilo
    # o ejecutarlo por separado. Por simplicidad, aquí solo se prueba la GUI.
    
    juego_gui = RecorridoCaballoGUI(tamaño=6) # Probar con 6x6
    juego_gui.ejecutar()
    pygame.quit()
    sys.exit()