# MAQUINADEARCADE/cliente/gui/recorrido_caballo_gui.py
import pygame
import sys
import os
from pathlib import Path
import json

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (RecorridoCaballo) ===
# ==============================================================================
VENTANA_ANCHO_CABALLO = 600
VENTANA_ALTO_CABALLO = 700
FPS_CABALLO = 60
ESPACIO_BOTONES_Y_CABALLO = 50
ESPACIO_SUGERENCIA_IA_Y_CABALLO = 60

NOMBRE_FUENTE_JUEGO_CABALLO = "nokiafc22.ttf"
TAMANO_FUENTE_NUMEROS_CABALLO = 22
TAMANO_FUENTE_BOTONES_CABALLO = 18
TAMANO_FUENTE_INFO_CABALLO = 16
TAMANO_FUENTE_IA_SUGERENCIA_CABALLO = 14

PALETAS_COLOR_CABALLO = {
    "pastel_juego": {
        "fondo": (245, 250, 240), "celda_clara": (255, 255, 255),
        "celda_oscura": (220, 240, 220), "borde_tablero": (180, 200, 180),
        "texto_numeros": (60, 80, 60), "texto_general": (70, 90, 70),
        "boton_resolver": (180, 230, 180), "boton_reiniciar": (255, 180, 180),
        "boton_verificar": (180, 180, 230), "boton_navegacion": (190, 190, 220),
        "boton_hover": (220, 220, 220),
        "boton_ia": (150, 220, 150)
    },
}
PALETA_ACTUAL_CABALLO = "pastel_juego"
COLORES = PALETAS_COLOR_CABALLO[PALETA_ACTUAL_CABALLO]

ANIMACION_CELDA_HOVER_INFLATE = 4
BORDE_GROSOR_CELDA_CABALLO = 1
BOTON_ANCHO_NORMAL_CABALLO = 100
BOTON_ANCHO_NAV_CABALLO = 150
BOTON_ALTO_CABALLO = 35
BOTON_BORDE_RADIO_CABALLO = 3
BOTON_BORDE_GROSOR_CABALLO = 2
BOTON_HOVER_INFLATE_CABALLO = 1

SCRIPT_DIR_CABALLO = Path(__file__).resolve().parent
RUTA_FUENTE_CABALLO_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_CABALLO:
    RUTA_FUENTE_CABALLO_COMPLETA = SCRIPT_DIR_CABALLO / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_CABALLO

from cliente.juegos.recorrido_caballo import RecorridoCaballo
from cliente.comunicacion.cliente_network import get_network_client
from cliente.comunicacion.ia_client import IAHelperThread

class RecorridoCaballoGUI:
    def __init__(self, tamaño=8, ancho=VENTANA_ANCHO_CABALLO, alto=VENTANA_ALTO_CABALLO):
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

        self._asignar_colores()
        self._cargar_fuentes()

        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y_CABALLO - ESPACIO_SUGERENCIA_IA_Y_CABALLO) // self.tamaño

        self.modo = "jugar"
        self.solucion_actual_idx = 0
        self.paso_actual_manual = 1
        self.celda_hover = None
        self.boton_hover_texto = None

        self.ia_helper_thread = None
        self.ia_suggestion_text = None
        self.ia_suggestion_surface = None
        self.ia_suggestion_rect = None
        self.botones_rects_para_clic = {}


    def _asignar_colores(self):
        self.color_fondo = COLORES["fondo"]
        self.color_celda_clara = COLORES["celda_clara"]
        self.color_celda_oscura = COLORES["celda_oscura"]
        self.color_borde_tablero = COLORES["borde_tablero"]
        self.color_texto_numeros = COLORES["texto_numeros"]
        self.color_texto_general = COLORES["texto_general"]
        self.color_boton_resolver = COLORES["boton_resolver"]
        self.color_boton_reiniciar = COLORES["boton_reiniciar"]
        self.color_boton_verificar = COLORES["boton_verificar"]
        self.color_boton_navegacion = COLORES["boton_navegacion"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_boton_ia = COLORES["boton_ia"]

    def _cargar_fuentes(self):
        try:
            if RUTA_FUENTE_CABALLO_COMPLETA and os.path.exists(RUTA_FUENTE_CABALLO_COMPLETA):
                self.fuente_numeros = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_NUMEROS_CABALLO)
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_BOTONES_CABALLO)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_INFO_CABALLO)
                self.fuente_ia_sugerencia = pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA, TAMANO_FUENTE_IA_SUGERENCIA_CABALLO)
            elif NOMBRE_FUENTE_JUEGO_CABALLO:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_CABALLO} no encontrada.")
            else:
                self.fuente_numeros = pygame.font.Font(None, TAMANO_FUENTE_NUMEROS_CABALLO)
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_CABALLO)
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_CABALLO)
                self.fuente_ia_sugerencia = pygame.font.Font(None, TAMANO_FUENTE_IA_SUGERENCIA_CABALLO)
        except Exception as e:
            print(f"Error cargando fuente para RecorridoCaballo ({e}). Usando SysFont.")
            self.fuente_numeros = pygame.font.SysFont('Arial', TAMANO_FUENTE_NUMEROS_CABALLO)
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_CABALLO)
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_CABALLO)
            self.fuente_ia_sugerencia = pygame.font.SysFont('Arial', TAMANO_FUENTE_IA_SUGERENCIA_CABALLO)

    def dibujar_gui_completa(self):
        self.ventana.fill(self.color_fondo)
        self._dibujar_tablero()
        self._dibujar_botones()
        self._dibujar_ia_sugerencia()
        pygame.display.flip()

    def _dibujar_tablero(self):
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color_base = self.color_celda_clara if (fila + col) % 2 == 0 else self.color_celda_oscura
                rect_base = pygame.Rect(col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto)
                color_draw = color_base
                rect_draw = rect_base
                if self.celda_hover == (fila, col):
                    color_draw = tuple(max(0, min(255, c + 15 if sum(color_base) < 382 else c - 15)) for c in color_base)
                    rect_draw = rect_base.inflate(ANIMACION_CELDA_HOVER_INFLATE, ANIMACION_CELDA_HOVER_INFLATE)
                pygame.draw.rect(self.ventana, color_draw, rect_draw)
                valor = self.juego.tablero[fila][col]
                if valor != -1:
                    texto_render = self.fuente_numeros.render(str(valor), True, self.color_texto_numeros)
                    self.ventana.blit(texto_render, texto_render.get_rect(center=rect_base.center))
                pygame.draw.rect(self.ventana, self.color_borde_tablero, rect_draw, BORDE_GROSOR_CELDA_CABALLO)

    def _dibujar_botones(self):
        self.botones_rects_para_clic.clear()
        y_botones_base = self.alto - ESPACIO_BOTONES_Y_CABALLO - (BOTON_ALTO_CABALLO // 2) - ESPACIO_SUGERENCIA_IA_Y_CABALLO
        button_spacing = 10
        
        botones_defs_jugar_data = [
            ("Resolver", "resolver", self.color_boton_resolver),
            ("Reiniciar", "reiniciar", self.color_boton_reiniciar),
            ("Verificar", "verificar", self.color_boton_verificar),
            ("IA Pista", "ia_pista", self.color_boton_ia)
        ]
        botones_defs_ver_sol_data = [
            ("Anterior", "anterior", self.color_boton_navegacion, BOTON_ANCHO_NAV_CABALLO),
            ("Siguiente", "siguiente", self.color_boton_navegacion, BOTON_ANCHO_NAV_CABALLO),
            ("Volver", "volver", self.color_boton_reiniciar, BOTON_ANCHO_NORMAL_CABALLO)
        ]

        botones_actuales_display_data = []
        current_x = 10
        if self.modo == "jugar":
            for texto, accion, color in botones_defs_jugar_data:
                botones_actuales_display_data.append({
                    "texto": texto, "accion": accion, "color": color, 
                    "rect_original": pygame.Rect(current_x, y_botones_base, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO)
                })
                self.botones_rects_para_clic[accion] = botones_actuales_display_data[-1]["rect_original"]
                current_x += BOTON_ANCHO_NORMAL_CABALLO + button_spacing
            
            texto_paso = self.fuente_info.render(f"Paso: {self.paso_actual_manual}", True, self.color_texto_general)
            self.ventana.blit(texto_paso, (current_x + 10, y_botones_base + (BOTON_ALTO_CABALLO // 2 - texto_paso.get_height() // 2)))
        
        else: # modo == "ver_soluciones"
            for texto, accion, color, ancho in botones_defs_ver_sol_data:
                botones_actuales_display_data.append({
                    "texto": texto, "accion": accion, "color": color,
                    "rect_original": pygame.Rect(current_x, y_botones_base, ancho, BOTON_ALTO_CABALLO)
                })
                self.botones_rects_para_clic[accion] = botones_actuales_display_data[-1]["rect_original"]
                current_x += ancho + button_spacing

            if self.juego.soluciones:
                texto_sol = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.color_texto_general)
                self.ventana.blit(texto_sol, (current_x + 10, y_botones_base + (BOTON_ALTO_CABALLO // 2 - texto_sol.get_height() // 2)))

        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for boton_data in botones_actuales_display_data:
            rect_original = boton_data["rect_original"]
            rect_dibujo = rect_original.copy()
            color_dibujo = boton_data["color"]

            if rect_original.collidepoint(mouse_pos):
                self.boton_hover_texto = boton_data["texto"]
                color_dibujo = self.color_boton_hover
                rect_dibujo = rect_original.inflate(BOTON_HOVER_INFLATE_CABALLO * 2, BOTON_HOVER_INFLATE_CABALLO * 2)

            pygame.draw.rect(self.ventana, color_dibujo, rect_dibujo, border_radius=BOTON_BORDE_RADIO_CABALLO)
            border_color_darker = tuple(max(0, c - 30) for c in color_dibujo)
            pygame.draw.rect(self.ventana, border_color_darker, rect_dibujo, BOTON_BORDE_GROSOR_CABALLO, border_radius=BOTON_BORDE_RADIO_CABALLO)
            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto_general)
            self.ventana.blit(texto_render, texto_render.get_rect(center=rect_dibujo.center))

    def _dibujar_ia_sugerencia(self):
        if self.ia_suggestion_surface and self.ia_suggestion_rect:
            pygame.draw.rect(self.ventana, self.color_fondo, self.ia_suggestion_rect.inflate(10,5))
            self.ventana.blit(self.ia_suggestion_surface, self.ia_suggestion_rect)

    def _guardar_resultado_caballo(self, completitud: bool):
        if self.resultado_guardado_este_intento: return
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

    def get_game_state_json(self):
        current_knight_pos = None
        last_move_number = self.paso_actual_manual - 1
        if last_move_number > 0:
            for r_idx, row_val in enumerate(self.juego.tablero):
                for c_idx, cell_val in enumerate(row_val):
                    if cell_val == last_move_number:
                        current_knight_pos = (r_idx, c_idx)
                        break
                if current_knight_pos: break
        state = {
            "board_size": self.tamaño,
            "board": self.juego.tablero,
            "current_step_to_place": self.paso_actual_manual,
            "start_position": self.posicion_inicial_caballo,
            "current_knight_position": current_knight_pos,
            "is_path_started": self.paso_actual_manual > 1
        }
        return json.dumps(state)

    def handle_ia_suggestion(self, suggestion_text_raw):
        print(f"[IA Caballo] Sugerencia cruda recibida: {suggestion_text_raw}")
        self.ia_suggestion_text = suggestion_text_raw
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(
                self.ia_suggestion_text, True, self.color_texto_general
            )
            y_buttons_bottom = self.alto - ESPACIO_BOTONES_Y_CABALLO - (BOTON_ALTO_CABALLO // 2) - ESPACIO_SUGERENCIA_IA_Y_CABALLO + BOTON_ALTO_CABALLO
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(
                centerx=self.ancho // 2,
                top= y_buttons_bottom + 10
            )
        else:
            self.ia_suggestion_surface = None
            self.ia_suggestion_rect = None

    def solicitar_sugerencia_ia(self):
        if self.ia_helper_thread and self.ia_helper_thread.is_alive():
            print("[IA Caballo] Ya hay una consulta a la IA en progreso.")
            self.ia_suggestion_text = "IA: Consulta previa en progreso..."
        else:
            estado_json_str_val = self.get_game_state_json()
            print(f"[IA Caballo] Solicitando sugerencia con estado: {estado_json_str_val}")
            self.ia_helper_thread = IAHelperThread(
                juego="recorrido_caballo",
                estado_json_str=estado_json_str_val, # CORREGIDO AQUÍ
                callback=self.handle_ia_suggestion
            )
            self.ia_helper_thread.start()
            self.ia_suggestion_text = "IA: Consultando..."
        
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(self.ia_suggestion_text, True, self.color_texto_general)
            y_buttons_bottom = self.alto - ESPACIO_BOTONES_Y_CABALLO - (BOTON_ALTO_CABALLO // 2) - ESPACIO_SUGERENCIA_IA_Y_CABALLO + BOTON_ALTO_CABALLO
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(
                centerx=self.ancho // 2,
                top=y_buttons_bottom + 10
            )

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.celda_hover = None
        if mouse_pos[1] < self.celda_alto * self.tamaño :
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                self.celda_hover = (fila, col)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                 if self._manejar_clic(evento.pos): return True
        return True

    def _manejar_clic(self, pos_clic):
        x_click, y_click = pos_clic
        if self.modo == "jugar" and y_click < self.celda_alto * self.tamaño:
            col_click = x_click // self.celda_ancho
            fila_click = y_click // self.celda_alto
            if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                if self.juego.mover_caballo(fila_click, col_click, self.paso_actual_manual):
                    if self.paso_actual_manual == 1: self.posicion_inicial_caballo = (fila_click, col_click)
                    self.paso_actual_manual += 1
                    self.resultado_guardado_este_intento = False
                    self.ia_suggestion_text = None; self.ia_suggestion_surface = None
                    return True
        
        for accion, rect_obj in self.botones_rects_para_clic.items():
            if rect_obj.collidepoint(pos_clic):
                self._ejecutar_accion_boton(accion)
                return True
        return False

    def _ejecutar_accion_boton(self, accion):
        if accion == "resolver":
            self.resultado_guardado_este_intento = False
            soluciones = self.juego.encontrar_soluciones()
            if soluciones:
                self.modo = "ver_soluciones"; self.solucion_actual_idx = 0
                self.juego.tablero = [f[:] for f in soluciones[self.solucion_actual_idx]]
            self.ia_suggestion_text = None; self.ia_suggestion_surface = None
        elif accion == "reiniciar":
            self.juego.reiniciar(); self.paso_actual_manual = 1; self.posicion_inicial_caballo = None
            self.resultado_guardado_este_intento = False; self.modo = "jugar"
            self.ia_suggestion_text = None; self.ia_suggestion_surface = None
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
            self.modo = "jugar"; self.juego.reiniciar(); self.paso_actual_manual = 1
            self.posicion_inicial_caballo = None; self.resultado_guardado_este_intento = False
            self.ia_suggestion_text = None; self.ia_suggestion_surface = None
        elif accion == "ia_pista":
            self.solicitar_sugerencia_ia()

    def ejecutar(self):
        print(f"[RecorridoCaballoGUI] Iniciando juego para tamaño {self.tamaño}x{self.tamaño}...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break
            self.dibujar_gui_completa()
            reloj.tick(FPS_CABALLO)
        print("[RecorridoCaballoGUI] Saliendo del juego Recorrido del Caballo.")

if __name__ == "__main__":
    print("Ejecutando RecorridoCaballoGUI directamente para pruebas...")
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG: Project root {PROJECT_ROOT_TEST} in sys.path.")
    juego_gui_caballo = RecorridoCaballoGUI(tamaño=6)
    juego_gui_caballo.ejecutar()
    pygame.quit()
    sys.exit()