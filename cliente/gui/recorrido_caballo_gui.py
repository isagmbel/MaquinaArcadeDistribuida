import pygame
import sys
import os # Para os.path.exists en la carga de fuentes
from pathlib import Path

# CONFIGURACIÓN DE APARIENCIA
# --- Fuentes ---
NOMBRE_FUENTE_JUEGO_CABALLO = "nokiafc22.ttf" # O "04B_03_.TTF", o None
TAMANO_FUENTE_NUMEROS_CABALLO = 22 # Para los números en el tablero
TAMANO_FUENTE_BOTONES_CABALLO = 18
TAMANO_FUENTE_INFO_CABALLO = 16

# --- Colores ---
PALETAS_COLOR_CABALLO = {
    "pastel_juego": {
        "fondo": (245, 250, 240), # Un verde muy pálido
        "celda_clara": (255, 255, 255),
        "celda_oscura": (220, 240, 220), # Verde pastel
        "borde_tablero": (180, 200, 180),
        "texto_numeros": (60, 80, 60),   # Verde oscuro
        "texto_general": (70, 90, 70),
        "boton_resolver": (180, 230, 180),
        "boton_reiniciar": (255, 180, 180),
        "boton_verificar": (180, 180, 230),
        "boton_navegacion": (190, 190, 220),
        "boton_hover": (220, 220, 220),
    }
}
PALETA_ACTUAL_CABALLO = "pastel_juego"
COLORES_CABALLO = PALETAS_COLOR_CABALLO[PALETA_ACTUAL_CABALLO]
# CONFIGURACIÓN DE APARIENCIA

#  RUTAS Y CLIENTE DE RED ---
SCRIPT_DIR_CABALLO = Path(__file__).resolve().parent
RUTA_FUENTE_CABALLO_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_CABALLO:
    RUTA_FUENTE_CABALLO_COMPLETA = SCRIPT_DIR_CABALLO / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_CABALLO

from cliente.juegos.recorrido_caballo import RecorridoCaballo
from cliente.comunicacion.cliente_network import get_network_client

class RecorridoCaballoGUI:
    def __init__(self, tamaño=8, ancho=600, alto=650):
        pygame.init()
        self.tamaño = tamaño
        self.juego = RecorridoCaballo(tamaño)

        self.network_client = get_network_client()
        self.posicion_inicial_caballo = None 
        self.resultado_guardado_este_intento = False
        
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Recorrido del Caballo")
        
        # --- MODIFICACIONES: ASIGNAR COLORES Y FUENTES ---
        self.FONDO = COLORES_CABALLO["fondo"]
        self.CELDA_CLARA = COLORES_CABALLO["celda_clara"]
        self.CELDA_OSCURA = COLORES_CABALLO["celda_oscura"]
        self.BORDE_TABLERO = COLORES_CABALLO["borde_tablero"]
        self.TEXTO_NUMEROS_COLOR = COLORES_CABALLO["texto_numeros"]
        self.TEXTO_GENERAL_COLOR = COLORES_CABALLO["texto_general"]
        
        self.BOTON_RESOLVER_COLOR = COLORES_CABALLO["boton_resolver"]
        self.BOTON_REINICIAR_COLOR = COLORES_CABALLO["boton_reiniciar"]
        self.BOTON_VERIFICAR_COLOR = COLORES_CABALLO["boton_verificar"]
        self.BOTON_NAVEGACION_COLOR = COLORES_CABALLO["boton_navegacion"]
        self.BOTON_HOVER_COLOR = COLORES_CABALLO["boton_hover"]

        try:
            if RUTA_FUENTE_CABALLO_COMPLETA and os.path.exists(RUTA_FUENTE_CABALLO_COMPLETA):
                self.fuente_numeros = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_NUMEROS_CABALLO)
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_BOTONES_CABALLO)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_INFO_CABALLO)
            elif NOMBRE_FUENTE_JUEGO_CABALLO:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_CABALLO} no encontrada.")
            else:
                self.fuente_numeros = pygame.font.Font(None, TAMANO_FUENTE_NUMEROS_CABALLO)
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_CABALLO)
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_CABALLO)
        except Exception as e:
            print(f"Error cargando fuente para RecorridoCaballo ({e}). Usando SysFont.")
            self.fuente_numeros = pygame.font.SysFont('Arial', TAMANO_FUENTE_NUMEROS_CABALLO)
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_CABALLO)
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_CABALLO)
        # --- FIN MODIFICACIONES ---
        
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - 50) // self.tamaño
        
        self.modo = "jugar"
        self.solucion_actual_idx = 0 # Renombrado
        self.paso_actual_manual = 1 # Renombrado
        
        self.celda_hover = None
        self.boton_hover_texto = None # Renombrado
    
    def dibujar_tablero(self):
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color_base = self.CELDA_CLARA if (fila + col) % 2 == 0 else self.CELDA_OSCURA
                
                celda_x_base = col * self.celda_ancho
                celda_y_base = fila * self.celda_alto
                celda_w_base = self.celda_ancho
                celda_h_base = self.celda_alto
                
                color_draw = color_base
                rect_celda_draw = pygame.Rect(celda_x_base, celda_y_base, celda_w_base, celda_h_base)

                if self.celda_hover == (fila, col):
                    # Efecto hover simple: oscurecer/aclarar un poco
                    color_draw = tuple(max(0, min(255, c + 15 if sum(color_base) < 382 else c - 15)) for c in color_base) # Aclarar claras, oscurecer oscuras
                    rect_celda_draw = rect_celda_draw.inflate(4,4) # Pequeño agrandamiento

                pygame.draw.rect(self.ventana, color_draw, rect_celda_draw)
                
                valor = self.juego.tablero[fila][col]
                if valor != -1:
                    texto_render = self.fuente_numeros.render(str(valor), True, self.TEXTO_NUMEROS_COLOR)
                    self.ventana.blit(texto_render, 
                                    (celda_x_base + celda_w_base//2 - texto_render.get_width()//2,
                                     celda_y_base + celda_h_base//2 - texto_render.get_height()//2))
                
                pygame.draw.rect(self.ventana, self.BORDE_TABLERO, rect_celda_draw, 1) # Borde más fino
    
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

        if self.modo == "jugar":
            texto_paso = self.fuente_info.render(f"Paso: {self.paso_actual_manual}", True, self.TEXTO_GENERAL_COLOR)
            self.ventana.blit(texto_paso, (400, self.alto - 38))
        elif self.juego.soluciones:
            texto_sol = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.TEXTO_GENERAL_COLOR)
            self.ventana.blit(texto_sol, (460, self.alto - 38))
        
        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_actuales_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw = boton_data["color"]
            rect_draw = boton_data["rect"]

            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.BOTON_HOVER_COLOR
                rect_draw = pygame.Rect(boton_data["rect"].x - 1, boton_data["rect"].y - 1, 
                                        boton_data["rect"].width + 2, boton_data["rect"].height + 2)
            
            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=3)
            pygame.draw.rect(self.ventana, tuple(max(0, c-30) for c in color_draw), rect_draw, 2, border_radius=3)
            
            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.TEXTO_GENERAL_COLOR)
            self.ventana.blit(texto_render, 
                            (rect_draw.centerx - texto_render.get_width()//2,
                             rect_draw.centery - texto_render.get_height()//2))

    def _guardar_resultado_caballo(self, completitud: bool):
        if self.resultado_guardado_este_intento:
            return
        pos_inicial_str = str(self.posicion_inicial_caballo) if self.posicion_inicial_caballo else "No registrada"
        mov_realizados = self.paso_actual_manual -1 if self.paso_actual_manual > 0 else 0

        print(f"[RecorridoCaballoGUI] Guardando: Pos Ini={pos_inicial_str}, Movs={mov_realizados}, Completado={completitud}")
        def callback_guardado(response):
            status_msg = "Ok" if response and response.get("status") == "ok" else "Error"
            details = response.get('message') if response else "N/A"
            print(f"[RecorridoCaballoGUI] Guardado: {status_msg} - {details}")
        self.network_client.save_knights_tour_score(
            start_position=pos_inicial_str, moves_made=mov_realizados, completed=completitud, callback=callback_guardado
        )
        self.resultado_guardado_este_intento = True

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.celda_hover = None
        if mouse_pos[1] < self.alto - 50:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                self.celda_hover = (fila, col)
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    x_click, y_click = pygame.mouse.get_pos()
                    
                    if self.modo == "jugar" and y_click < self.alto - 50:
                        col_click = x_click // self.celda_ancho
                        fila_click = y_click // self.celda_alto
                        if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                            if self.juego.mover_caballo(fila_click, col_click, self.paso_actual_manual):
                                if self.paso_actual_manual == 1:
                                    self.posicion_inicial_caballo = (fila_click, col_click)
                                self.paso_actual_manual += 1
                                self.resultado_guardado_este_intento = False
                    
                    elif y_click >= self.alto - 50:
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
                                    self.resultado_guardado_este_intento = False
                                    soluciones = self.juego.encontrar_soluciones()
                                    if soluciones:
                                        self.modo = "ver_soluciones"
                                        self.solucion_actual_idx = 0
                                        self.juego.tablero = [f[:] for f in soluciones[self.solucion_actual_idx]]
                                elif accion == "reiniciar":
                                    self.juego.reiniciar()
                                    self.paso_actual_manual = 1
                                    self.posicion_inicial_caballo = None
                                    self.resultado_guardado_este_intento = False
                                elif accion == "verificar":
                                    es_valida = self.juego.es_solucion_valida()
                                    print("¡Recorrido Verificado!" if es_valida else "Recorrido Incorrecto.")
                                    self._guardar_resultado_caballo(completitud=es_valida)
                                elif accion == "anterior":
                                    if self.juego.soluciones:
                                        self.solucion_actual_idx = (self.solucion_actual_idx - 1 + len(self.juego.soluciones)) % len(self.juego.soluciones)
                                        self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
                                elif accion == "siguiente":
                                    if self.juego.soluciones:
                                        self.solucion_actual_idx = (self.solucion_actual_idx + 1) % len(self.juego.soluciones)
                                        self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
                                elif accion == "volver":
                                    self.modo = "jugar"
                                    self.juego.reiniciar()
                                    self.paso_actual_manual = 1
                                    self.posicion_inicial_caballo = None
                                    self.resultado_guardado_este_intento = False
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
        print("[RecorridoCaballoGUI] Saliendo del juego Recorrido del Caballo.")

if __name__ == "__main__":
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    
    juego_gui_caballo = RecorridoCaballoGUI(tamaño=6)
    juego_gui_caballo.ejecutar()
    pygame.quit()
    sys.exit()