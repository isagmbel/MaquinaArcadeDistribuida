# MAQUINADEARCADE/cliente/gui/n_reinas_gui.py
import pygame
import sys
import math
import os
from pathlib import Path
import json

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (NReinas) ===
# ==============================================================================
VENTANA_ANCHO_NREINAS = 600
VENTANA_ALTO_NREINAS = 700
FPS_NREINAS = 60
ESPACIO_BOTONES_Y = 50
ESPACIO_SUGERENCIA_IA_Y = 60

NOMBRE_FUENTE_JUEGO_NREINAS = "nokiafc22.ttf"
TAMANO_FUENTE_BOTONES_NREINAS = 18
TAMANO_FUENTE_INFO_NREINAS = 16
TAMANO_FUENTE_IA_SUGERENCIA = 14

PALETAS_COLOR_NREINAS = {
    "pastel_juego": {
        "fondo": (250, 240, 245), "celda_clara": (255, 255, 255),
        "celda_oscura": (230, 230, 250), "borde_tablero": (200, 180, 200),
        "texto_general": (80, 60, 80), "boton_resolver": (180, 230, 180),
        "boton_reiniciar": (255, 180, 180), "boton_verificar": (180, 180, 230),
        "boton_navegacion": (190, 190, 220), "boton_hover": (220, 220, 220),
        "reina_cuerpo": (255, 120, 170), "reina_corona": (255, 180, 200),
        "boton_ia": (150, 220, 150)
    },
}
PALETA_ACTUAL_NREINAS = "pastel_juego"
COLORES = PALETAS_COLOR_NREINAS[PALETA_ACTUAL_NREINAS]

ANIMACION_CELDA_HOVER_FACTOR = 1.1
ANIMACION_CELDA_SUAVIDAD = 0.1
BORDE_GROSOR_CELDA = 2
BOTON_ANCHO_NORMAL = 120
BOTON_ANCHO_NAV = 150
BOTON_ALTO = 35
BOTON_BORDE_RADIO = 3
BOTON_BORDE_GROSOR = 2
BOTON_HOVER_INFLATE = 1

SCRIPT_DIR_NREINAS = Path(__file__).resolve().parent
RUTA_FUENTE_NREINAS_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_NREINAS:
    RUTA_FUENTE_NREINAS_COMPLETA = SCRIPT_DIR_NREINAS / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_NREINAS

from cliente.juegos.n_reinas import NReinas
from cliente.comunicacion.cliente_network import get_network_client
from cliente.comunicacion.ia_client import IAHelperThread

class NReinasGUI:
    def __init__(self, tamaño=8, ancho=VENTANA_ANCHO_NREINAS, alto=VENTANA_ALTO_NREINAS):
        pygame.init()
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        self.network_client = get_network_client()
        self.intentos_nreinas = 0

        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")

        self._asignar_colores()
        self._cargar_fuentes()

        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y - ESPACIO_SUGERENCIA_IA_Y) // self.tamaño

        self.modo = "jugar"
        self.solucion_actual_idx = 0
        self.celda_hover = None
        self.boton_hover_texto = None
        self.hover_scale_anim = 1.0
        self.target_scale_anim = 1.0

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
        self.color_texto = COLORES["texto_general"]
        self.color_boton_resolver = COLORES["boton_resolver"]
        self.color_boton_reiniciar = COLORES["boton_reiniciar"]
        self.color_boton_verificar = COLORES["boton_verificar"]
        self.color_boton_navegacion = COLORES["boton_navegacion"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_reina_cuerpo = COLORES["reina_cuerpo"]
        self.color_reina_corona = COLORES["reina_corona"]
        self.color_boton_ia = COLORES["boton_ia"]

    def _cargar_fuentes(self):
        try:
            if RUTA_FUENTE_NREINAS_COMPLETA and os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA):
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_INFO_NREINAS)
                self.fuente_ia_sugerencia = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_IA_SUGERENCIA)
            elif NOMBRE_FUENTE_JUEGO_NREINAS:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_NREINAS} no encontrada.")
            else:
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_NREINAS)
                self.fuente_ia_sugerencia = pygame.font.Font(None, TAMANO_FUENTE_IA_SUGERENCIA)
        except Exception as e:
            print(f"Error cargando fuente para NReinas ({e}). Usando SysFont.")
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_NREINAS)
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_NREINAS)
            self.fuente_ia_sugerencia = pygame.font.SysFont('Arial', TAMANO_FUENTE_IA_SUGERENCIA)

    def dibujar_gui_completa(self):
        self.ventana.fill(self.color_fondo)
        self._dibujar_tablero()
        self._dibujar_botones()
        self._dibujar_ia_sugerencia()
        pygame.display.flip()

    def _dibujar_tablero(self):
        self.hover_scale_anim += (self.target_scale_anim - self.hover_scale_anim) * ANIMACION_CELDA_SUAVIDAD
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color_base = self.color_celda_clara if (fila + col) % 2 == 0 else self.color_celda_oscura
                rect_base = pygame.Rect(col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto)
                current_scale = 1.0
                color_draw = color_base
                rect_draw = rect_base
                if self.celda_hover == (fila, col):
                    current_scale = self.hover_scale_anim
                    rect_draw = rect_base.inflate(
                        int(self.celda_ancho * (current_scale - 1)),
                        int(self.celda_alto * (current_scale - 1))
                    )
                    rect_draw.center = rect_base.center
                    color_draw = tuple(max(0, min(255, c + 20)) for c in color_base)
                pygame.draw.rect(self.ventana, color_draw, rect_draw)
                if self.juego.tablero[fila][col] == 1:
                    self._dibujar_reina(rect_base.centerx, rect_base.centery, current_scale)
                pygame.draw.rect(self.ventana, self.color_borde_tablero, rect_draw, BORDE_GROSOR_CELDA)

    def _dibujar_reina(self, centro_x, centro_y, scale=1.0):
        radio_base = min(self.celda_ancho, self.celda_alto) // 3
        radio_scaled = int(radio_base * scale)
        if radio_scaled < 1: radio_scaled = 1
        pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (centro_x, centro_y), radio_scaled)
        corona_radius = int(radio_scaled * 0.6)
        if corona_radius < 1: corona_radius = 1
        pygame.draw.circle(self.ventana, self.color_reina_corona, (centro_x, centro_y), corona_radius)
        pico_radius = int(radio_scaled * 0.15)
        if pico_radius < 1: pico_radius = 1
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            crown_x = centro_x + int(radio_scaled * 0.8 * math.cos(angle))
            crown_y = centro_y + int(radio_scaled * 0.8 * math.sin(angle))
            pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (crown_x, crown_y), pico_radius)

    def _dibujar_botones(self):
        self.botones_rects_para_clic.clear()
        y_botones_base = self.alto - ESPACIO_BOTONES_Y - (BOTON_ALTO // 2) - ESPACIO_SUGERENCIA_IA_Y

        botones_defs_jugar = [
            {"texto": "Resolver", "accion": "resolver", "color": self.color_boton_resolver, "ancho": BOTON_ANCHO_NORMAL, "offset_x": 10},
            {"texto": "Reiniciar", "accion": "reiniciar", "color": self.color_boton_reiniciar, "ancho": BOTON_ANCHO_NORMAL, "offset_x": 140},
            {"texto": "Verificar", "accion": "verificar", "color": self.color_boton_verificar, "ancho": BOTON_ANCHO_NORMAL, "offset_x": 270},
            {"texto": "IA Pista", "accion": "ia_pista", "color": self.color_boton_ia, "ancho": BOTON_ANCHO_NORMAL, "offset_x": 400}
        ]
        botones_defs_ver_sol = [
            {"texto": "Anterior", "accion": "anterior", "color": self.color_boton_navegacion, "ancho": BOTON_ANCHO_NAV, "offset_x": 10},
            {"texto": "Siguiente", "accion": "siguiente", "color": self.color_boton_navegacion, "ancho": BOTON_ANCHO_NAV, "offset_x": 170},
            {"texto": "Volver", "accion": "volver", "color": self.color_boton_reiniciar, "ancho": BOTON_ANCHO_NORMAL, "offset_x": 330}
        ]
        
        botones_actuales_defs = botones_defs_jugar if self.modo == "jugar" else botones_defs_ver_sol

        if self.modo == "ver_soluciones" and hasattr(self.juego, 'soluciones') and self.juego.soluciones:
            texto_sol_render = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.color_texto)
            self.ventana.blit(texto_sol_render, (self.ancho - texto_sol_render.get_width() - 10, y_botones_base + (BOTON_ALTO // 2 - texto_sol_render.get_height() // 2)))

        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for boton_data in botones_actuales_defs:
            rect_original = pygame.Rect(boton_data["offset_x"], y_botones_base, boton_data["ancho"], BOTON_ALTO)
            self.botones_rects_para_clic[boton_data["accion"]] = rect_original

            rect_dibujo = rect_original.copy()
            color_dibujo = boton_data["color"]
            
            if rect_original.collidepoint(mouse_pos):
                self.boton_hover_texto = boton_data["texto"]
                color_dibujo = self.color_boton_hover
                rect_dibujo = rect_original.inflate(BOTON_HOVER_INFLATE * 2, BOTON_HOVER_INFLATE * 2)

            pygame.draw.rect(self.ventana, color_dibujo, rect_dibujo, border_radius=BOTON_BORDE_RADIO)
            border_color_darker = tuple(max(0, c - 30) for c in color_dibujo)
            pygame.draw.rect(self.ventana, border_color_darker, rect_dibujo, BOTON_BORDE_GROSOR, border_radius=BOTON_BORDE_RADIO)
            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto)
            self.ventana.blit(texto_render, texto_render.get_rect(center=rect_dibujo.center))

    def _dibujar_ia_sugerencia(self):
        if self.ia_suggestion_surface and self.ia_suggestion_rect:
            pygame.draw.rect(self.ventana, self.color_fondo, self.ia_suggestion_rect.inflate(10,5))
            self.ventana.blit(self.ia_suggestion_surface, self.ia_suggestion_rect)

    def _guardar_resultado_nreinas(self, exito: bool):
        print(f"[NReinasGUI] Guardando: N={self.tamaño}, Éxito={exito}, Intentos={self.intentos_nreinas}")
        def callback_guardado(response):
            status = "Ok" if response and response.get("status") == "ok" else "Error"
            msg = response.get('message', 'N/A') if response else "Sin respuesta"
            print(f"[NReinasGUI] Guardado: {status} - {msg}")
        self.network_client.save_n_reinas_score(
            n_value=self.tamaño, success=exito, attempts=self.intentos_nreinas, callback=callback_guardado
        )

    def get_game_state_json(self):
        state = {
            "board_size": self.tamaño,
            "board": self.juego.tablero,
            "current_mode": self.modo,
            "num_reinas_colocadas": sum(row.count(1) for row in self.juego.tablero)
        }
        return json.dumps(state)

    def handle_ia_suggestion(self, suggestion_text_raw):
        print(f"[IA NReinas] Sugerencia cruda recibida: {suggestion_text_raw}")
        self.ia_suggestion_text = suggestion_text_raw # Mostrar directamente
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(
                self.ia_suggestion_text, True, self.color_texto
            )
            y_buttons_bottom = self.alto - ESPACIO_BOTONES_Y - (BOTON_ALTO // 2) - ESPACIO_SUGERENCIA_IA_Y + BOTON_ALTO
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(
                centerx=self.ancho // 2,
                top= y_buttons_bottom + 10
            )
        else:
            self.ia_suggestion_surface = None
            self.ia_suggestion_rect = None

    def solicitar_sugerencia_ia(self):
        if self.ia_helper_thread and self.ia_helper_thread.is_alive():
            print("[IA NReinas] Ya hay una consulta a la IA en progreso.")
            self.ia_suggestion_text = "IA: Consulta previa en progreso..."
        else:
            estado_json_str_val = self.get_game_state_json() # Renombrado para evitar conflicto
            print(f"[IA NReinas] Solicitando sugerencia con estado: {estado_json_str_val}")
            self.ia_helper_thread = IAHelperThread(
                juego="n_reinas",
                estado_json_str=estado_json_str_val, # CORREGIDO AQUÍ
                callback=self.handle_ia_suggestion
            )
            self.ia_helper_thread.start()
            self.ia_suggestion_text = "IA: Consultando..."
        
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(self.ia_suggestion_text, True, self.color_texto)
            y_buttons_bottom = self.alto - ESPACIO_BOTONES_Y - (BOTON_ALTO // 2) - ESPACIO_SUGERENCIA_IA_Y + BOTON_ALTO
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(
                centerx=self.ancho // 2,
                top=y_buttons_bottom + 10
            )

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        nuevo_hover_celda = None
        if mouse_pos[1] < self.celda_alto * self.tamaño :
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                nuevo_hover_celda = (fila, col)
        if nuevo_hover_celda != self.celda_hover:
            self.celda_hover = nuevo_hover_celda
            self.target_scale_anim = ANIMACION_CELDA_HOVER_FACTOR if nuevo_hover_celda else 1.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._manejar_clic(evento.pos):
                    return True
        return True

    def _manejar_clic(self, pos_clic):
        x_click, y_click = pos_clic
        if self.modo == "jugar" and y_click < self.celda_alto * self.tamaño:
            col_click = x_click // self.celda_ancho
            fila_click = y_click // self.celda_alto
            if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                self.juego.tablero[fila_click][col_click] = 1 - self.juego.tablero[fila_click][col_click]
                self.ia_suggestion_text = None
                self.ia_suggestion_surface = None
                return True
        
        for accion, rect_obj in self.botones_rects_para_clic.items():
            if rect_obj.collidepoint(pos_clic):
                self._ejecutar_accion_boton(accion)
                return True
        return False

    def _ejecutar_accion_boton(self, accion):
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
                self.modo = "jugar"
                self.ia_suggestion_text = None
                self.ia_suggestion_surface = None
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
            self.ia_suggestion_text = None
            self.ia_suggestion_surface = None
        elif accion == "ia_pista":
            self.solicitar_sugerencia_ia()

    def ejecutar(self):
        print(f"[NReinasGUI] Iniciando juego para N={self.tamaño}...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break
            self.dibujar_gui_completa()
            reloj.tick(FPS_NREINAS)
        print("[NReinasGUI] Saliendo del juego N Reinas.")

if __name__ == "__main__":
    print("Ejecutando NReinasGUI directamente para pruebas...")
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG: Project root {PROJECT_ROOT_TEST} in sys.path.")
    juego_gui_nreinas = NReinasGUI(tamaño=8)
    juego_gui_nreinas.ejecutar()
    pygame.quit()
    sys.exit()