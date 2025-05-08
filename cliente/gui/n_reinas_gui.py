import pygame
import sys
import math # Sigue siendo necesario para dibujar la reina
import os # Para os.path.exists en la carga de fuentes
from pathlib import Path

# CONFIGURACIÓN DE APARIENCIA
# Fuentes 
NOMBRE_FUENTE_JUEGO_NREINAS = "nokiafc22.ttf" # O "04B_03_.TTF", o None
TAMANO_FUENTE_BOTONES_NREINAS = 18
TAMANO_FUENTE_INFO_NREINAS = 16

# --- Colores (Paleta específica para NReinas o una general) ---
PALETAS_COLOR_NREINAS = {
    "pastel_juego": {
        "fondo": (250, 240, 245),
        "celda_clara": (255, 255, 255),
        "celda_oscura": (230, 230, 250),
        "borde_tablero": (200, 180, 200), # Más suave
        "texto_general": (80, 60, 80),    # Más oscuro para contraste
        "boton_resolver": (180, 230, 180),
        "boton_reiniciar": (255, 180, 180),
        "boton_verificar": (180, 180, 230),
        "boton_navegacion": (190, 190, 220), # Para Anterior/Siguiente/Volver
        "boton_hover": (220, 220, 220),
        "reina_cuerpo": (255, 120, 170), # Más vibrante
        "reina_corona": (255, 180, 200)
    }
    # mas paletas
}
PALETA_ACTUAL_NREINAS = "pastel_juego"
COLORES_NREINAS = PALETAS_COLOR_NREINAS[PALETA_ACTUAL_NREINAS]
# CONFIGURACIÓN DE APARIENCIA 

# RUTAS Y CLIENTE DE RED
SCRIPT_DIR_NREINAS = Path(__file__).resolve().parent
RUTA_FUENTE_NREINAS_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_NREINAS:
    RUTA_FUENTE_NREINAS_COMPLETA = SCRIPT_DIR_NREINAS / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_NREINAS

from cliente.juegos.n_reinas import NReinas
from cliente.comunicacion.cliente_network import get_network_client


class NReinasGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init()
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        
        self.network_client = get_network_client()
        self.intentos_nreinas = 0

        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")
        
        # --- MODIFICACIONES: ASIGNAR COLORES Y FUENTES ---
        self.FONDO = COLORES_NREINAS["fondo"]
        self.CELDA_CLARA = COLORES_NREINAS["celda_clara"]
        self.CELDA_OSCURA = COLORES_NREINAS["celda_oscura"]
        self.BORDE_TABLERO = COLORES_NREINAS["borde_tablero"]
        self.TEXTO_COLOR = COLORES_NREINAS["texto_general"]
        
        self.BOTON_RESOLVER_COLOR = COLORES_NREINAS["boton_resolver"]
        self.BOTON_REINICIAR_COLOR = COLORES_NREINAS["boton_reiniciar"]
        self.BOTON_VERIFICAR_COLOR = COLORES_NREINAS["boton_verificar"]
        self.BOTON_NAVEGACION_COLOR = COLORES_NREINAS["boton_navegacion"]
        self.BOTON_HOVER_COLOR = COLORES_NREINAS["boton_hover"]
        self.REINA_COLOR = COLORES_NREINAS["reina_cuerpo"]
        self.REINA_CORONA_COLOR = COLORES_NREINAS["reina_corona"]

        try:
            if RUTA_FUENTE_NREINAS_COMPLETA and os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA):
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_INFO_NREINAS)
            elif NOMBRE_FUENTE_JUEGO_NREINAS:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_NREINAS} no encontrada.")
            else: # Fuente por defecto de Pygame
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_NREINAS)
        except Exception as e:
            print(f"Error cargando fuente para NReinas ({e}). Usando SysFont.")
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_NREINAS)
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_NREINAS)
        # --- FIN MODIFICACIONES ---
        
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño # 50px para botones
        
        self.modo = "jugar" 
        self.solucion_actual_idx = 0
        
        self.celda_hover = None
        self.boton_hover_texto = None
        self.hover_scale_anim = 1.0
        self.target_scale_anim = 1.0
    
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
                    self.dibujar_reina(col, fila, current_scale)
                
                pygame.draw.rect(self.ventana, self.BORDE_TABLERO, (celda_x_draw, celda_y_draw, celda_w_draw, celda_h_draw), 2)
    
    def dibujar_reina(self, col, fila, scale=1.0):
        centro_x = col * self.celda_ancho + self.celda_ancho // 2
        centro_y = fila * self.celda_alto + self.celda_alto // 2
        radio_base = min(self.celda_ancho, self.celda_alto) // 3
        radio_scaled = int(radio_base * scale)
        
        pygame.draw.circle(self.ventana, self.REINA_COLOR, (centro_x, centro_y), radio_scaled)
        pygame.draw.circle(self.ventana, self.REINA_CORONA_COLOR, (centro_x, centro_y), int(radio_scaled * 0.6))
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2 
            crown_x = centro_x + int(radio_scaled * 0.8 * math.cos(angle))
            crown_y = centro_y + int(radio_scaled * 0.8 * math.sin(angle))
            pygame.draw.circle(self.ventana, self.REINA_COLOR, (crown_x, crown_y), int(radio_scaled * 0.15))
    
    def dibujar_botones(self):
        botones_info_jugar = [
            {"rect": pygame.Rect(10, self.alto - 45, 120, 35), "color": self.BOTON_RESOLVER_COLOR, "texto": "Resolver"},
            {"rect": pygame.Rect(140, self.alto - 45, 120, 35), "color": self.BOTON_REINICIAR_COLOR, "texto": "Reiniciar"},
            {"rect": pygame.Rect(270, self.alto - 45, 120, 35), "color": self.BOTON_VERIFICAR_COLOR, "texto": "Verificar"}
        ]
        botones_info_ver_sol = [
            {"rect": pygame.Rect(10, self.alto - 45, 150, 35), "color": self.BOTON_NAVEGACION_COLOR, "texto": "Anterior"},
            {"rect": pygame.Rect(170, self.alto - 45, 150, 35), "color": self.BOTON_NAVEGACION_COLOR, "texto": "Siguiente"},
            {"rect": pygame.Rect(330, self.alto - 45, 120, 35), "color": self.BOTON_REINICIAR_COLOR, "texto": "Volver"}
        ]
        
        botones_actuales_info = botones_info_jugar if self.modo == "jugar" else botones_info_ver_sol
            
        if self.modo == "ver_soluciones" and hasattr(self.juego, 'soluciones') and self.juego.soluciones:
            texto_sol = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.TEXTO_COLOR)
            self.ventana.blit(texto_sol, (460, self.alto - 38)) # Ajustar Y
        
        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_actuales_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw = boton_data["color"]
            rect_draw = boton_data["rect"]

            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.BOTON_HOVER_COLOR
                # Efecto de "presionado" sutil o cambio de tamaño
                rect_draw = pygame.Rect(boton_data["rect"].x - 1, boton_data["rect"].y - 1, 
                                        boton_data["rect"].width + 2, boton_data["rect"].height + 2)

            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=3) # Borde redondeado para botones
            pygame.draw.rect(self.ventana, tuple(max(0, c-30) for c in color_draw), rect_draw, 2, border_radius=3) # Borde más oscuro
            
            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.TEXTO_COLOR)
            self.ventana.blit(texto_render, 
                            (rect_draw.centerx - texto_render.get_width()//2,
                             rect_draw.centery - texto_render.get_height()//2))

    def _guardar_resultado_nreinas(self, exito: bool):
        print(f"[NReinasGUI] Guardando: N={self.tamaño}, Éxito={exito}, Intentos={self.intentos_nreinas}")
        def callback_guardado(response):
            if response and response.get("status") == "ok":
                print(f"[NReinasGUI] Puntuación guardada: {response.get('message')}")
            else:
                msg = response.get('message') if response else "Error desconocido"
                print(f"[NReinasGUI] Error al guardar puntuación: {msg}")
        self.network_client.save_n_reinas_score(
            n_value=self.tamaño, success=exito, attempts=self.intentos_nreinas, callback=callback_guardado
        )

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        nuevo_hover_celda = None
        if mouse_pos[1] < self.alto - 50:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                nuevo_hover_celda = (fila, col)
        
        if nuevo_hover_celda != self.celda_hover:
            self.celda_hover = nuevo_hover_celda
            self.target_scale_anim = 1.1 if nuevo_hover_celda else 1.0
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False 

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Botón izquierdo
                    x_click, y_click = pygame.mouse.get_pos()
                    
                    if self.modo == "jugar" and y_click < self.alto - 50:
                        col_click = x_click // self.celda_ancho
                        fila_click = y_click // self.celda_alto
                        if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                            self.juego.tablero[fila_click][col_click] = 1 - self.juego.tablero[fila_click][col_click]
                    
                    elif y_click >= self.alto - 50: # Zona de botones
                        botones_jugar_defs = [
                            {"rect": pygame.Rect(10, self.alto - 45, 120, 35), "accion": "resolver"},
                            {"rect": pygame.Rect(140, self.alto - 45, 120, 35), "accion": "reiniciar"},
                            {"rect": pygame.Rect(270, self.alto - 45, 120, 35), "accion": "verificar"}
                        ]
                        botones_ver_sol_defs = [
                            {"rect": pygame.Rect(10, self.alto - 45, 150, 35), "accion": "anterior"},
                            {"rect": pygame.Rect(170, self.alto - 45, 150, 35), "accion": "siguiente"},
                            {"rect": pygame.Rect(330, self.alto - 45, 120, 35), "accion": "volver"}
                        ]
                        botones_actuales_defs = botones_jugar_defs if self.modo == "jugar" else botones_ver_sol_defs

                        for boton_def in botones_actuales_defs:
                            if boton_def["rect"].collidepoint(x_click, y_click):
                                accion = boton_def["accion"]
                                if accion == "resolver":
                                    if hasattr(self.juego, 'obtener_soluciones'):
                                        soluciones = self.juego.obtener_soluciones()
                                        if soluciones:
                                            self.modo = "ver_soluciones"
                                            self.solucion_actual_idx = 0
                                            self.juego.tablero = [f[:] for f in soluciones[self.solucion_actual_idx]]
                                elif accion == "reiniciar":
                                    if hasattr(self.juego, 'reiniciar'):
                                        self.juego.reiniciar()
                                        self.intentos_nreinas = 0
                                elif accion == "verificar":
                                    self.intentos_nreinas += 1
                                    if hasattr(self.juego, 'es_solucion'):
                                        es_valida = self.juego.es_solucion()
                                        print("¡Solución Verificada!" if es_valida else "Solución Incorrecta.")
                                        self._guardar_resultado_nreinas(exito=es_valida)
                                elif accion == "anterior":
                                    if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                        self.solucion_actual_idx = (self.solucion_actual_idx - 1 + len(self.juego.soluciones)) % len(self.juego.soluciones)
                                        self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
                                elif accion == "siguiente":
                                    if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                                        self.solucion_actual_idx = (self.solucion_actual_idx + 1) % len(self.juego.soluciones)
                                        self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
                                elif accion == "volver":
                                    self.modo = "jugar"
                                    if hasattr(self.juego, 'reiniciar'):
                                        self.juego.reiniciar()
                                break 
        return True
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break

            self.ventana.fill(self.FONDO)
            self.dibujar_tablero()
            self.dibujar_botones()
            pygame.display.flip()
            reloj.tick(60)
        print("[NReinasGUI] Saliendo del juego N Reinas.")
        # pygame.quit() # Dejar que el menú lo maneje o que el script __main__ lo haga

if __name__ == "__main__":
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2] 
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    
    juego_gui_nreinas = NReinasGUI(tamaño=8)
    juego_gui_nreinas.ejecutar()
    pygame.quit()
    sys.exit()