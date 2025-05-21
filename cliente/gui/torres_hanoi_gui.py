# MAQUINADEARCADE/cliente/gui/torres_hanoi_gui.py
import pygame
import sys
import time
import os
from pathlib import Path
import json

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (TorresHanoi) ===
# ==============================================================================
VENTANA_ANCHO_HANOI = 800
VENTANA_ALTO_HANOI = 650
FPS_HANOI = 30

NOMBRE_FUENTE_JUEGO_HANOI = "nokiafc22.ttf"
TAMANO_FUENTE_INFO_HANOI = 20
TAMANO_FUENTE_BOTONES_HANOI = 18
TAMANO_FUENTE_TITULO_HANOI = 30
TAMANO_FUENTE_IA_SUGERENCIA_HANOI = 14

PALETAS_COLOR_HANOI = {
    "pastel_juego": {
        "fondo": (240, 245, 250), "base_torre": (200, 190, 170),
        "poste_torre": (180, 170, 150),
        "discos": [ (255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 255, 153),
                   (221, 160, 221), (175, 238, 238), (255, 218, 185), (211, 211, 211) ],
        "texto_info": (70, 70, 90), "texto_botones": (60, 60, 80),
        "boton_normal": (200, 200, 220), "boton_hover": (220, 220, 240),
        "texto_resuelto": (80, 160, 80),
        "boton_ia": (150, 220, 150)
    },
}
PALETA_ACTUAL_HANOI = "pastel_juego"
COLORES = PALETAS_COLOR_HANOI[PALETA_ACTUAL_HANOI]

BASE_TORRE_Y_OFFSET = 100
BASE_TORRE_ALTURA = 20
BASE_TORRE_MARGEN_X = 0.1
POSTE_ANCHO = 15
POSTE_ALTURA = 250
DISCO_ALTURA_UNIDAD = 25
DISCO_ANCHO_MAX = 140
DISCO_REDUCCION_ANCHO = 18
DISCO_BORDE_GROSOR = 2
DISCO_HOVER_INFLATE = 6
BOTON_ANCHO_HANOI = 150
BOTON_ALTO_HANOI = 35
BOTON_BORDE_RADIO_HANOI = 5
BOTON_BORDE_GROSOR_HANOI = 2
BOTON_HOVER_INFLATE_UI_HANOI = 2
BOTON_POS_X_HANOI = VENTANA_ANCHO_HANOI - 170
BOTON_ESPACIO_Y_HANOI = 40
RESOLVER_AUTO_DELAY_MS = 400
ESPACIO_SUGERENCIA_IA_Y_HANOI = 60

SCRIPT_DIR_HANOI = Path(__file__).resolve().parent
RUTA_FUENTE_HANOI_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_HANOI:
    RUTA_FUENTE_HANOI_COMPLETA = SCRIPT_DIR_HANOI / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_HANOI

from cliente.juegos.torres_hanoi import TorresHanoi
from cliente.comunicacion.cliente_network import get_network_client
from cliente.comunicacion.ia_client import IAHelperThread

class TorresHanoiGUI:
    def __init__(self, discos=3, ancho=VENTANA_ANCHO_HANOI, alto=VENTANA_ALTO_HANOI):
        pygame.init()
        self.discos = discos
        self.juego = TorresHanoi(discos)
        self.network_client = get_network_client()
        self.resultado_hanoi_guardado = False
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Torres de Hanoi")
        self._asignar_colores()
        self._cargar_fuentes()
        self.torre_pos_x_coords = [ancho // 4, ancho // 2, 3 * ancho // 4]
        self.base_y_coord = alto - BASE_TORRE_Y_OFFSET
        self.disco_seleccionado_val = None
        self.torre_origen_idx = None
        self.resolviendo_auto = False
        self.pasos_solucion_auto = []
        self.paso_actual_auto = 0
        self.hover_torre_idx = None
        self.hover_boton_texto = None
        self.ia_helper_thread = None
        self.ia_suggestion_text = None
        self.ia_suggestion_surface = None
        self.ia_suggestion_rect = None
        self.botones_rects_para_clic = {}

    def _asignar_colores(self):
        self.color_fondo = COLORES["fondo"]
        self.color_base_torre = COLORES["base_torre"]
        self.color_poste_torre = COLORES["poste_torre"]
        self.colores_discos = COLORES["discos"]
        self.color_texto_info = COLORES["texto_info"]
        self.color_texto_botones = COLORES["texto_botones"]
        self.color_boton_normal = COLORES["boton_normal"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_texto_resuelto = COLORES["texto_resuelto"]
        self.color_boton_ia = COLORES["boton_ia"]

    def _cargar_fuentes(self):
        try:
            if RUTA_FUENTE_HANOI_COMPLETA and os.path.exists(RUTA_FUENTE_HANOI_COMPLETA):
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_TITULO_HANOI)
                self.fuente_ia_sugerencia = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_IA_SUGERENCIA_HANOI)
            elif NOMBRE_FUENTE_JUEGO_HANOI:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_HANOI} no encontrada.")
            else:
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.Font(None, TAMANO_FUENTE_TITULO_HANOI)
                self.fuente_ia_sugerencia = pygame.font.Font(None, TAMANO_FUENTE_IA_SUGERENCIA_HANOI)
        except Exception as e:
            print(f"Error cargando fuente para TorresHanoi ({e}). Usando SysFont.")
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_HANOI)
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_HANOI)
            self.fuente_titulo_juego = pygame.font.SysFont('Arial', TAMANO_FUENTE_TITULO_HANOI, bold=True)
            self.fuente_ia_sugerencia = pygame.font.SysFont('Arial', TAMANO_FUENTE_IA_SUGERENCIA_HANOI)

    def dibujar_gui_completa(self):
        self.ventana.fill(self.color_fondo)
        self._dibujar_torres_y_discos()
        self._dibujar_ui_info()
        self._dibujar_ia_sugerencia()
        pygame.display.flip()

    def _dibujar_torres_y_discos(self):
        base_ancho = self.ancho * (1 - 2 * BASE_TORRE_MARGEN_X)
        pygame.draw.rect(self.ventana, self.color_base_torre,
                         (self.ancho * BASE_TORRE_MARGEN_X, self.base_y_coord, base_ancho, BASE_TORRE_ALTURA),
                         border_radius=3)
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            color_poste = self.color_poste_torre
            if self.hover_torre_idx == i and not self.resolviendo_auto:
                color_poste = tuple(max(0, min(255, c + 20)) for c in self.color_poste_torre)
            pygame.draw.rect(self.ventana, color_poste,
                            (x_coord - POSTE_ANCHO // 2, self.base_y_coord - POSTE_ALTURA,
                             POSTE_ANCHO, POSTE_ALTURA), border_top_left_radius=5, border_top_right_radius=5)
        for torre_idx, torre_discos in enumerate(self.juego.torres):
            for disco_idx_en_torre, valor_disco in enumerate(torre_discos):
                ancho_disco = DISCO_ANCHO_MAX - (DISCO_REDUCCION_ANCHO * (self.discos - valor_disco))
                x_disco = self.torre_pos_x_coords[torre_idx] - ancho_disco // 2
                y_disco_actual = self.base_y_coord - (disco_idx_en_torre + 1) * DISCO_ALTURA_UNIDAD
                rect_disco = pygame.Rect(x_disco, y_disco_actual, ancho_disco, DISCO_ALTURA_UNIDAD)
                color_idx_disco = (valor_disco - 1) % len(self.colores_discos)
                color_disco_base = self.colores_discos[color_idx_disco]
                rect_disco_dibujo = rect_disco
                color_disco_dibujo = color_disco_base
                if self.torre_origen_idx == torre_idx and disco_idx_en_torre == len(torre_discos) - 1 and not self.resolviendo_auto:
                    rect_disco_dibujo = rect_disco.move(0, -10)
                    color_disco_dibujo = tuple(max(0, min(255, c + 30)) for c in color_disco_base)
                    pygame.draw.rect(self.ventana, color_disco_dibujo, rect_disco_dibujo.inflate(DISCO_HOVER_INFLATE, DISCO_HOVER_INFLATE//2), border_radius=3)
                else:
                    pygame.draw.rect(self.ventana, color_disco_dibujo, rect_disco_dibujo, border_radius=3)
                
                border_color_disco = tuple(max(0, c - 50) for c in color_disco_base)
                pygame.draw.rect(self.ventana, border_color_disco, rect_disco_dibujo, DISCO_BORDE_GROSOR, border_radius=3)

    def _dibujar_ui_info(self):
        self.botones_rects_para_clic.clear()
        movimientos_texto_render = self.fuente_info.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})",
            True, self.color_texto_info)
        self.ventana.blit(movimientos_texto_render, (20, 20))
        if self.juego.esta_resuelto():
            if not self.resultado_hanoi_guardado: self._guardar_resultado_hanoi(exito=True)
            felicitacion_render = self.fuente_titulo_juego.render("¡Resuelto!", True, self.color_texto_resuelto)
            self.ventana.blit(felicitacion_render, felicitacion_render.get_rect(center=(self.ancho // 2, 80)))

        botones_definiciones = [
            {"texto": "Reiniciar", "accion_str": "reiniciar", "color_base": self.color_boton_normal},
            {"texto": "Resolver", "accion_str": "resolver_auto", "color_base": self.color_boton_normal},
            {"texto": "Deshacer", "accion_str": "deshacer", "color_base": self.color_boton_normal},
            {"texto": "IA Pista", "accion_str": "ia_pista", "color_base": self.color_boton_ia}
        ]
        self.hover_boton_texto = None
        mouse_pos = pygame.mouse.get_pos()
        for i, boton_data in enumerate(botones_definiciones):
            y_b = 30 + i * BOTON_ESPACIO_Y_HANOI
            rect_original = pygame.Rect(BOTON_POS_X_HANOI, y_b, BOTON_ANCHO_HANOI, BOTON_ALTO_HANOI)
            self.botones_rects_para_clic[boton_data["accion_str"]] = rect_original
            rect_dibujo = rect_original.copy()
            color_dibujo = boton_data["color_base"]
            if not self.resolviendo_auto and rect_original.collidepoint(mouse_pos) :
                self.hover_boton_texto = boton_data["texto"]
                color_dibujo = self.color_boton_hover
                rect_dibujo = rect_original.inflate(BOTON_HOVER_INFLATE_UI_HANOI * 2, BOTON_HOVER_INFLATE_UI_HANOI * 2)
            pygame.draw.rect(self.ventana, color_dibujo, rect_dibujo, border_radius=BOTON_BORDE_RADIO_HANOI)
            border_color_darker = tuple(max(0, c - 30) for c in color_dibujo)
            pygame.draw.rect(self.ventana, border_color_darker, rect_dibujo, BOTON_BORDE_GROSOR_HANOI, border_radius=BOTON_BORDE_RADIO_HANOI)
            texto_b_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto_botones)
            self.ventana.blit(texto_b_render, texto_b_render.get_rect(center=rect_dibujo.center))

    def _dibujar_ia_sugerencia(self):
        if self.ia_suggestion_surface and self.ia_suggestion_rect:
            pygame.draw.rect(self.ventana, self.color_fondo, self.ia_suggestion_rect.inflate(10,5))
            self.ventana.blit(self.ia_suggestion_surface, self.ia_suggestion_rect)

    def accion_deshacer_wrapper(self):
        self.juego.deshacer_ultimo_movimiento()
        self.resultado_hanoi_guardado = False
        self.ia_suggestion_text = None; self.ia_suggestion_surface = None

    def _guardar_resultado_hanoi(self, exito: bool):
        if self.resultado_hanoi_guardado and exito: return
        print(f"[TorresHanoiGUI] Guardando: Discos={self.discos}, Movs={self.juego.movimientos}, Éxito={exito}")
        def callback_guardado(response):
            status_msg = "Ok" if response and response.get("status") == "ok" else "Error"
            details = response.get('message') if response else "N/A"
            print(f"[TorresHanoiGUI] Guardado: {status_msg} - {details}")
        self.network_client.save_torres_hanoi_score(
            num_disks=self.discos, moves_made=self.juego.movimientos, success=exito, callback=callback_guardado
        )
        if exito: self.resultado_hanoi_guardado = True

    def accion_reiniciar(self):
        self.juego.reiniciar()
        self.resolviendo_auto = False; self.resultado_hanoi_guardado = False
        self.torre_origen_idx = None; self.disco_seleccionado_val = None
        self.ia_suggestion_text = None; self.ia_suggestion_surface = None

    def accion_resolver_auto(self):
        if not self.resolviendo_auto:
            self.accion_reiniciar()
            self.resolviendo_auto = True; self.pasos_solucion_auto = []
            self._generar_solucion_hanoi(self.discos, 0, 2, 1); self.paso_actual_auto = 0
            self.ia_suggestion_text = None; self.ia_suggestion_surface = None

    def _generar_solucion_hanoi(self, n_discos, origen_idx, destino_idx, aux_idx):
        if n_discos == 0: return
        self._generar_solucion_hanoi(n_discos - 1, origen_idx, aux_idx, destino_idx)
        self.pasos_solucion_auto.append((origen_idx, destino_idx))
        self._generar_solucion_hanoi(n_discos - 1, aux_idx, destino_idx, origen_idx)

    def get_game_state_json(self):
        state = {
            "num_disks": self.discos, "towers": self.juego.torres,
            "moves_made": self.juego.movimientos, "min_moves_solution": self.juego.solucion_minima,
            "selected_disk_value": self.disco_seleccionado_val, "source_tower_index": self.torre_origen_idx,
            "is_solved": self.juego.esta_resuelto(), "is_auto_solving": self.resolviendo_auto
        }
        return json.dumps(state)

    def handle_ia_suggestion(self, suggestion_text_raw):
        print(f"[IA Hanoi] Sugerencia cruda recibida: {suggestion_text_raw}")
        self.ia_suggestion_text = suggestion_text_raw
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(self.ia_suggestion_text, True, self.color_texto_info)
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(centerx=self.ancho // 2, bottom=self.alto - 15)
        else:
            self.ia_suggestion_surface = None; self.ia_suggestion_rect = None

    def solicitar_sugerencia_ia(self):
        if self.resolviendo_auto: self.ia_suggestion_text = "IA: No disponible en modo auto."
        elif self.ia_helper_thread and self.ia_helper_thread.is_alive():
            print("[IA Hanoi] Ya hay una consulta a la IA en progreso.")
            self.ia_suggestion_text = "IA: Consulta previa en progreso..."
        else:
            estado_json_str_val = self.get_game_state_json()
            print(f"[IA Hanoi] Solicitando sugerencia con estado: {estado_json_str_val}")
            self.ia_helper_thread = IAHelperThread(
                juego="torres_hanoi",
                estado_json_str=estado_json_str_val, # CORREGIDO AQUÍ
                callback=self.handle_ia_suggestion
            )
            self.ia_helper_thread.start()
            self.ia_suggestion_text = "IA: Consultando..."
        if self.ia_suggestion_text:
            self.ia_suggestion_surface = self.fuente_ia_sugerencia.render(self.ia_suggestion_text, True, self.color_texto_info)
            self.ia_suggestion_rect = self.ia_suggestion_surface.get_rect(centerx=self.ancho // 2, bottom=self.alto - 15)

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hover_torre_idx = None
        if not self.resolviendo_auto:
            for i, x_coord in enumerate(self.torre_pos_x_coords):
                torre_rect_detect = pygame.Rect(x_coord - DISCO_ANCHO_MAX // 1.5,
                                                self.base_y_coord - POSTE_ALTURA - DISCO_ALTURA_UNIDAD * self.discos,
                                                DISCO_ANCHO_MAX * 1.33,
                                                POSTE_ALTURA + DISCO_ALTURA_UNIDAD * self.discos + BASE_TORRE_ALTURA)
                if torre_rect_detect.collidepoint(mouse_pos): self.hover_torre_idx = i; break
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._manejar_clic(mouse_pos): return True
            if evento.type == pygame.KEYDOWN:
                if self._manejar_teclado(evento.key): return True
        return True

    def _ejecutar_accion_boton(self, accion_str):
        if self.resolviendo_auto and accion_str not in ["reiniciar"]: return
        if accion_str == "reiniciar": self.accion_reiniciar()
        elif accion_str == "resolver_auto": self.accion_resolver_auto()
        elif accion_str == "deshacer": self.accion_deshacer_wrapper()
        elif accion_str == "ia_pista": self.solicitar_sugerencia_ia()

    def _manejar_clic(self, pos_clic):
        for accion_str, rect_obj in self.botones_rects_para_clic.items():
            if rect_obj.collidepoint(pos_clic):
                self._ejecutar_accion_boton(accion_str)
                return True
        if not self.resolviendo_auto and self.hover_torre_idx is not None:
            if self.torre_origen_idx is None:
                if self.juego.torres[self.hover_torre_idx]:
                    self.torre_origen_idx = self.hover_torre_idx
                    self.disco_seleccionado_val = self.juego.torres[self.hover_torre_idx][-1]
            else:
                moved = self.juego.mover_disco(self.torre_origen_idx, self.hover_torre_idx)
                if moved: self.resultado_hanoi_guardado = False; self.ia_suggestion_text = None; self.ia_suggestion_surface = None
                self.torre_origen_idx = None; self.disco_seleccionado_val = None
            return True
        if not self.resolviendo_auto: self.torre_origen_idx = None; self.disco_seleccionado_val = None
        return False

    def _manejar_teclado(self, key):
        if self.resolviendo_auto: return False
        if key == pygame.K_r: self.accion_reiniciar(); return True
        elif key == pygame.K_s: self.accion_resolver_auto(); return True
        elif key == pygame.K_u: self.accion_deshacer_wrapper(); return True
        elif key == pygame.K_i: self.solicitar_sugerencia_ia(); return True
        return False

    def actualizar_resolucion_automatica(self):
        if self.resolviendo_auto and self.paso_actual_auto < len(self.pasos_solucion_auto):
            origen_idx, destino_idx = self.pasos_solucion_auto[self.paso_actual_auto]
            movido = self.juego.mover_disco(origen_idx, destino_idx)
            if movido: self.paso_actual_auto += 1
            pygame.time.delay(RESOLVER_AUTO_DELAY_MS)
        elif self.resolviendo_auto and self.paso_actual_auto >= len(self.pasos_solucion_auto):
            self.resolviendo_auto = False
            if self.juego.esta_resuelto() and not self.resultado_hanoi_guardado: self._guardar_resultado_hanoi(exito=True)

    def ejecutar(self):
        print(f"[TorresHanoiGUI] Iniciando juego para {self.discos} discos...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break
            if self.resolviendo_auto: self.actualizar_resolucion_automatica()
            self.dibujar_gui_completa()
            reloj.tick(FPS_HANOI)
        print("[TorresHanoiGUI] Saliendo del juego Torres de Hanoi.")

if __name__ == "__main__":
    print("Ejecutando TorresHanoiGUI directamente para pruebas...")
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG: Project root {PROJECT_ROOT_TEST} in sys.path.")
    juego_gui_hanoi = TorresHanoiGUI(discos=3)
    juego_gui_hanoi.ejecutar()
    pygame.quit()
    sys.exit()