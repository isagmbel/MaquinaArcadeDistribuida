import pygame
import sys
import time 
import os
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (TorresHanoi) ===
# ==============================================================================
VENTANA_ANCHO_HANOI = 800
VENTANA_ALTO_HANOI = 650 
FPS_HANOI = 30
NOMBRE_FUENTE_JUEGO_HANOI = "nokiafc22.ttf"
TAMANO_FUENTE_INFO_HANOI = 20
TAMANO_FUENTE_BOTONES_HANOI = 16 
TAMANO_FUENTE_TITULO_HANOI = 30
TAMANO_FUENTE_FEEDBACK_HANOI = 18

PALETAS_COLOR_HANOI = {
    "pastel_juego": {
        "fondo": (240, 245, 250), "base_torre": (200, 190, 170),
        "poste_torre": (180, 170, 150),
        "discos": [ (255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 255, 153),
                   (221, 160, 221), (175, 238, 238), (255, 218, 185), (211, 211, 211) ],
        "texto_info": (70, 70, 90), "texto_botones": (60, 60, 80),
        "boton_normal": (200, 200, 220), "boton_hover": (220, 220, 240),
        "boton_deshacer_especial": (220, 180, 180),
        "boton_navegacion": (190, 190, 220), # Para "Volver al Menú"
        "texto_resuelto": (80, 160, 80),
        "feedback_fondo": (220, 220, 220, 200),
        "texto_feedback": (50, 50, 70)
    },
    # ... (tu otra paleta si la tienes) ...
}
PALETA_ACTUAL_HANOI = "pastel_juego" 
COLORES = PALETAS_COLOR_HANOI[PALETA_ACTUAL_HANOI]

BASE_TORRE_Y_OFFSET = 70 
BASE_TORRE_ALTURA = 20
POSTE_ANCHO = 15
POSTE_ALTURA = 280 
DISCO_ALTURA_UNIDAD = 25
DISCO_ANCHO_MAX = 150 
DISCO_REDUCCION_ANCHO = 20 
DISCO_BORDE_GROSOR = 2
DISCO_HOVER_INFLATE = 6 
BOTON_ALTO_HANOI = 35
BOTON_BORDE_RADIO_HANOI = 5
BOTON_BORDE_GROSOR_HANOI = 2
RESOLVER_AUTO_DELAY_MS = 300
ESPACIO_SUPERIOR_INFO = 60 
ESPACIO_LATERAL_BOTONES = 180 
ESPACIO_FEEDBACK_Y_HANOI = 40 

# ==============================================================================
# === CLASE TorresHanoi (Lógica del Juego) ===
# ==============================================================================
class TorresHanoi: # (Misma clase que te pasé antes, la incluyo por completitud)
    def __init__(self, discos=3):
        self.discos = discos
        self.torres = [[i for i in range(discos, 0, -1)], [], []]
        self.movimientos = 0
        self.solucion_minima = (2 ** discos) - 1
        self.historial_movimientos_juego = [] 

    def mover_disco(self, origen_idx, destino_idx): 
        if self.es_movimiento_valido(origen_idx, destino_idx):
            disco = self.torres[origen_idx].pop()
            self.torres[destino_idx].append(disco)
            self.movimientos += 1
            self.historial_movimientos_juego.append((origen_idx, destino_idx)) 
            return True, "" 
        elif not self.torres[origen_idx]:
            return False, "Torre origen vacía."
        elif self.torres[destino_idx] and self.torres[origen_idx][-1] > self.torres[destino_idx][-1]:
            return False, "Disco grande sobre pequeño." # Mensaje más corto
        else:
            return False, "Movimiento inválido."

    def es_movimiento_valido(self, origen_idx, destino_idx):
        if not (0 <= origen_idx <= 2 and 0 <= destino_idx <= 2): return False
        if not self.torres[origen_idx]: return False 
        if not self.torres[destino_idx]: return True 
        return self.torres[origen_idx][-1] < self.torres[destino_idx][-1]

    def esta_resuelto(self):
        return not self.torres[0] and not self.torres[1] and len(self.torres[2]) == self.discos

    def reiniciar(self):
        self.torres = [[i for i in range(self.discos, 0, -1)], [], []]
        self.movimientos = 0
        self.historial_movimientos_juego = []

    def _generar_pasos_solucion(self, n_discos, origen_idx, destino_idx, aux_idx, pasos_lista):
        if n_discos == 0: return
        self._generar_pasos_solucion(n_discos - 1, origen_idx, aux_idx, destino_idx, pasos_lista)
        pasos_lista.append((origen_idx, destino_idx))
        self._generar_pasos_solucion(n_discos - 1, aux_idx, destino_idx, origen_idx, pasos_lista)
    
    def deshacer_ultimo_movimiento(self):
        if self.historial_movimientos_juego:
            origen_original, destino_original = self.historial_movimientos_juego.pop()
            if self.torres[destino_original]: 
                disco_a_devolver = self.torres[destino_original].pop()
                self.torres[origen_original].append(disco_a_devolver)
                self.movimientos -= 1 
                return True, "" 
            return False, "Error al deshacer."
        return False, "No hay movimientos para deshacer."

# ==============================================================================
# === IMPORTACIONES Y RUTAS (GUI) ===
# ==============================================================================
SCRIPT_DIR_HANOI = Path(__file__).resolve().parent
RUTA_FUENTE_HANOI_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_HANOI:
    RUTA_FUENTE_HANOI_COMPLETA = SCRIPT_DIR_HANOI / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_HANOI
    if not os.path.exists(RUTA_FUENTE_HANOI_COMPLETA) : print(f"[DEBUG Hanoi] Fuente NO ENCONTRADA: {RUTA_FUENTE_HANOI_COMPLETA}")

class MockNetworkClient: # (Mismo Mock que antes)
    def save_torres_hanoi_score(self, num_disks, moves_made, success, callback):
        print(f"[MockCliente Hanoi] Enviado: {{'disks': {num_disks}, 'moves': {moves_made}, 'success': {success}}}}}")
        response = {'status': 'ok', 'message': 'TorresHanoi score saved (mock)'}
        if callback: callback(response)

def get_network_client(): # (Mismo get_network_client que antes)
    try:
        from cliente.comunicacion.cliente_network import get_network_client as real_get_network_client
        return real_get_network_client()
    except ImportError:
        print("[TorresHanoiGUI] Usando MockNetworkClient.")
        return MockNetworkClient()

# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (TorresHanoiGUI) ===
# ==============================================================================
class TorresHanoiGUI:
    def __init__(self, discos=3, ancho=VENTANA_ANCHO_HANOI, alto=VENTANA_ALTO_HANOI):
        pygame.init()
        self.discos = discos
        self.juego = TorresHanoi(discos)
        self.network_client = get_network_client()
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Torres de Hanoi - {discos} Discos")

        self._asignar_colores()
        self._cargar_fuentes()

        self.espacio_torres_ancho = self.ancho - ESPACIO_LATERAL_BOTONES - 20 
        centro_total_torres = self.espacio_torres_ancho / 2 + 20 
        espacio_entre_torres = self.espacio_torres_ancho / 3.5 
        self.torre_pos_x_coords = [
            int(centro_total_torres - espacio_entre_torres),
            int(centro_total_torres),
            int(centro_total_torres + espacio_entre_torres)
        ]
        self.base_y_coord = self.alto - BASE_TORRE_Y_OFFSET

        self.disco_seleccionado_valor = None 
        self.torre_origen_seleccionada_idx = None
        self.resolviendo_automaticamente = False
        self.pasos_solucion_automatica = []
        self.paso_actual_solucion_automatica = 0
        self.ultimo_tiempo_mov_auto = 0
        self.hover_torre_idx = None 
        self.hover_boton_texto = None 
        self.mensaje_feedback_texto = ""
        self.mensaje_feedback_tiempo_fin = 0
        self.duracion_feedback_ms = 2000 
        self.resultado_hanoi_guardado_este_intento = False
        self.accion_al_salir = None # "VOLVER_MENU" o "CERRAR_JUEGO"

    def _asignar_colores(self):
        self.color_fondo = COLORES["fondo"]
        self.color_base_torre = COLORES["base_torre"]
        self.color_poste_torre = COLORES["poste_torre"]
        self.colores_discos_lista = COLORES["discos"]
        self.color_texto_info = COLORES["texto_info"]
        self.color_texto_botones = COLORES["texto_botones"]
        self.color_boton_normal = COLORES["boton_normal"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_boton_deshacer = COLORES.get("boton_deshacer_especial", self.color_boton_normal)
        self.color_boton_volver_menu = COLORES.get("boton_navegacion", self.color_boton_normal)
        self.color_texto_resuelto = COLORES["texto_resuelto"]
        self.color_feedback_fondo = COLORES["feedback_fondo"]
        self.color_texto_feedback = COLORES.get("texto_feedback", self.color_texto_info)

    def _cargar_fuentes(self):
        try:
            if RUTA_FUENTE_HANOI_COMPLETA and os.path.exists(RUTA_FUENTE_HANOI_COMPLETA):
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_TITULO_HANOI)
                self.fuente_feedback = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_FEEDBACK_HANOI)
            else:
                if NOMBRE_FUENTE_JUEGO_HANOI: print(f"Advertencia: Fuente {NOMBRE_FUENTE_JUEGO_HANOI} no encontrada. Usando SysFont.")
                self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.SysFont('Arial', TAMANO_FUENTE_TITULO_HANOI, bold=True)
                self.fuente_feedback = pygame.font.SysFont('Arial', TAMANO_FUENTE_FEEDBACK_HANOI)
        except Exception as e:
            print(f"Error cargando fuente para TorresHanoi ({e}). Usando SysFont.")
            self.fuente_info, self.fuente_botones, self.fuente_titulo_juego, self.fuente_feedback = [pygame.font.SysFont('Arial', s) for s in [TAMANO_FUENTE_INFO_HANOI, TAMANO_FUENTE_BOTONES_HANOI, TAMANO_FUENTE_TITULO_HANOI, TAMANO_FUENTE_FEEDBACK_HANOI]]

    def dibujar_gui_completa(self):
        self.ventana.fill(self.color_fondo)
        self._dibujar_torres_y_discos()
        self._dibujar_panel_info_y_botones()
        self._dibujar_feedback_mensaje()
        pygame.display.flip()

    def _dibujar_torres_y_discos(self): # (Misma función que antes)
        ancho_base_total = self.torre_pos_x_coords[-1] - self.torre_pos_x_coords[0] + DISCO_ANCHO_MAX * 1.2
        x_base_total = self.torre_pos_x_coords[0] - (DISCO_ANCHO_MAX * 1.2) / 2
        x_base_total = max(10, x_base_total) 
        ancho_base_total = min(ancho_base_total, self.ancho - 20 - ESPACIO_LATERAL_BOTONES)
        pygame.draw.rect(self.ventana, self.color_base_torre, (x_base_total, self.base_y_coord, ancho_base_total, BASE_TORRE_ALTURA), border_radius=3)

        for i, x_coord_poste in enumerate(self.torre_pos_x_coords):
            color_poste_actual = self.color_poste_torre
            if self.torre_origen_seleccionada_idx == i or \
               (self.hover_torre_idx == i and self.torre_origen_seleccionada_idx is None and self.juego.torres[i]) or \
               (self.hover_torre_idx == i and self.torre_origen_seleccionada_idx is not None and self.juego.es_movimiento_valido(self.torre_origen_seleccionada_idx, i)):
                color_poste_actual = tuple(max(0, min(255, c + 25)) for c in self.color_poste_torre)
            pygame.draw.rect(self.ventana, color_poste_actual, (x_coord_poste - POSTE_ANCHO // 2, self.base_y_coord - POSTE_ALTURA, POSTE_ANCHO, POSTE_ALTURA), border_top_left_radius=5, border_top_right_radius=5)

            for idx_disco_en_torre, valor_disco_actual in enumerate(self.juego.torres[i]):
                ancho_disco_actual = DISCO_ANCHO_MAX - (DISCO_REDUCCION_ANCHO * (self.discos - valor_disco_actual))
                x_disco_actual = x_coord_poste - ancho_disco_actual // 2
                y_disco_actual = self.base_y_coord - (idx_disco_en_torre + 1) * DISCO_ALTURA_UNIDAD
                color_idx_para_disco = (valor_disco_actual - 1) % len(self.colores_discos_lista)
                color_base_disco = self.colores_discos_lista[color_idx_para_disco]
                rect_disco_actual = pygame.Rect(x_disco_actual, y_disco_actual, ancho_disco_actual, DISCO_ALTURA_UNIDAD)

                if self.torre_origen_seleccionada_idx == i and idx_disco_en_torre == len(self.juego.torres[i]) - 1:
                    color_borde_seleccionado = tuple(max(0, min(255, c - 60)) for c in color_base_disco) 
                    pygame.draw.rect(self.ventana, color_borde_seleccionado, rect_disco_actual.inflate(DISCO_HOVER_INFLATE, DISCO_HOVER_INFLATE), border_radius=5)
                pygame.draw.rect(self.ventana, color_base_disco, rect_disco_actual, border_radius=3)
                color_borde_normal_disco = tuple(max(0, c - 50) for c in color_base_disco)
                pygame.draw.rect(self.ventana, color_borde_normal_disco, rect_disco_actual, DISCO_BORDE_GROSOR, border_radius=3)

    def _dibujar_panel_info_y_botones(self):
        panel_x = self.ancho - ESPACIO_LATERAL_BOTONES + 10
        mov_texto = f"Movimientos: {self.juego.movimientos}"
        min_mov_texto = f"(Mínimo: {self.juego.solucion_minima})"
        render_mov = self.fuente_info.render(mov_texto, True, self.color_texto_info)
        render_min_mov = self.fuente_info.render(min_mov_texto, True, self.color_texto_info)
        self.ventana.blit(render_mov, (panel_x, ESPACIO_SUPERIOR_INFO))
        self.ventana.blit(render_min_mov, (panel_x, ESPACIO_SUPERIOR_INFO + render_mov.get_height() + 5))

        y_offset_botones = ESPACIO_SUPERIOR_INFO + render_mov.get_height() + render_min_mov.get_height() + 30
        if self.juego.esta_resuelto():
            if not self.resultado_hanoi_guardado_este_intento: self._guardar_resultado_hanoi(exito=True)
            felicitacion_render = self.fuente_titulo_juego.render("¡Resuelto!", True, self.color_texto_resuelto)
            self.ventana.blit(felicitacion_render, felicitacion_render.get_rect(centerx=panel_x + (ESPACIO_LATERAL_BOTONES-20)//2, top=y_offset_botones))
            y_offset_botones += felicitacion_render.get_height() + 15

        ancho_boton_panel = ESPACIO_LATERAL_BOTONES - 40
        botones_definiciones = [
            {"texto": "Reiniciar", "accion_id": "reiniciar"},
            {"texto": "Resolver", "accion_id": "resolver_auto"},
            {"texto": "Deshacer", "accion_id": "deshacer"},
            {"texto": "Volver al Menú", "accion_id": "volver_menu"} # Botón añadido
        ]
        self.mapa_botones_rects = {} 
        self.hover_boton_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for i, boton_def in enumerate(botones_definiciones):
            y_boton_actual = y_offset_botones + i * (BOTON_ALTO_HANOI + 10) 
            rect_boton = pygame.Rect(panel_x + 10, y_boton_actual, ancho_boton_panel, BOTON_ALTO_HANOI)
            self.mapa_botones_rects[boton_def["accion_id"]] = rect_boton
            es_hover = rect_boton.collidepoint(mouse_pos)
            color_boton_actual = self.color_boton_normal
            if boton_def["accion_id"] == "deshacer": color_boton_actual = self.color_boton_deshacer
            elif boton_def["accion_id"] == "volver_menu": color_boton_actual = self.color_boton_volver_menu
            if es_hover:
                self.hover_boton_texto = boton_def["texto"]
                color_boton_actual = self.color_boton_hover
            pygame.draw.rect(self.ventana, color_boton_actual, rect_boton, border_radius=BOTON_BORDE_RADIO_HANOI)
            color_borde_boton = tuple(max(0, c - 30) for c in color_boton_actual)
            pygame.draw.rect(self.ventana, color_borde_boton, rect_boton, BOTON_BORDE_GROSOR_HANOI, border_radius=BOTON_BORDE_RADIO_HANOI)
            render_texto_boton = self.fuente_botones.render(boton_def["texto"], True, self.color_texto_botones)
            self.ventana.blit(render_texto_boton, render_texto_boton.get_rect(center=rect_boton.center))
    
    def _dibujar_feedback_mensaje(self): # (Misma función que antes)
        if self.mensaje_feedback_texto and pygame.time.get_ticks() < self.mensaje_feedback_tiempo_fin:
            texto_render = self.fuente_feedback.render(self.mensaje_feedback_texto, True, self.color_texto_feedback)
            rect_texto = texto_render.get_rect(centerx=(self.ancho - ESPACIO_LATERAL_BOTONES) / 2, top=ESPACIO_SUPERIOR_INFO + 10) 
            fondo_rect = rect_texto.inflate(20, 10) 
            s = pygame.Surface(fondo_rect.size, pygame.SRCALPHA)
            s.fill(self.color_feedback_fondo)
            self.ventana.blit(s, fondo_rect.topleft)
            self.ventana.blit(texto_render, rect_texto)
        elif pygame.time.get_ticks() >= self.mensaje_feedback_tiempo_fin:
            self.mensaje_feedback_texto = "" 

    def _mostrar_feedback(self, texto, duracion_ms=None): # (Misma función que antes)
        self.mensaje_feedback_texto = texto
        if duracion_ms is None: duracion_ms = self.duracion_feedback_ms
        self.mensaje_feedback_tiempo_fin = pygame.time.get_ticks() + duracion_ms
        print(f"[Feedback GUI Hanoi] {texto}") 

    def _guardar_resultado_hanoi(self, exito: bool): # (Misma función que antes)
        if self.resultado_hanoi_guardado_este_intento and exito: return
        self._mostrar_feedback(f"Guardando: Discos={self.discos}, Movs={self.juego.movimientos}, Éxito={exito}", 3000)
        print(f"SIMULANDO ENVÍO HANOI: Discos={self.discos}, Movs={self.juego.movimientos}, Éxito={exito}")
        self._callback_guardado_hanoi({'status': 'ok', 'message': 'TorresHanoi score saved (simulado)'}, exito)

    def _callback_guardado_hanoi(self, response, exito_original): # (Misma función que antes)
        status_msg = "Ok" if response and response.get("status") == "ok" else "Error"
        details = response.get('message') if response else "N/A"
        self._mostrar_feedback(f"Guardado: {status_msg} - {details}", 3000)
        if exito_original and status_msg == "Ok": self.resultado_hanoi_guardado_este_intento = True

    def _accion_reiniciar_juego(self): # (Misma función que antes)
        self.juego.reiniciar()
        self.resolviendo_automaticamente = False
        self.pasos_solucion_automatica = []
        self.paso_actual_solucion_automatica = 0
        self.torre_origen_seleccionada_idx = None
        self.disco_seleccionado_valor = None
        self.resultado_hanoi_guardado_este_intento = False
        self._mostrar_feedback("Juego Reiniciado.")

    def _accion_resolver_automaticamente(self): # (Misma función que antes)
        if not self.resolviendo_automaticamente:
            self._accion_reiniciar_juego() 
            self.resolviendo_automaticamente = True
            self.pasos_solucion_automatica = [] 
            self.juego._generar_pasos_solucion(self.discos, 0, 2, 1, self.pasos_solucion_automatica)
            self.paso_actual_solucion_automatica = 0
            self.ultimo_tiempo_mov_auto = pygame.time.get_ticks() 
            self._mostrar_feedback(f"Resolviendo para {self.discos} discos...", 2000 + len(self.pasos_solucion_automatica) * RESOLVER_AUTO_DELAY_MS)

    def _accion_deshacer_movimiento(self): # (Misma función que antes)
        if self.resolviendo_automaticamente:
            self._mostrar_feedback("No se puede deshacer durante la resolución automática.", 2000)
            return
        deshecho_ok, msg = self.juego.deshacer_ultimo_movimiento()
        if deshecho_ok:
            self.resultado_hanoi_guardado_este_intento = False 
            self.torre_origen_seleccionada_idx = None 
            self.disco_seleccionado_valor = None
            self._mostrar_feedback("Movimiento deshecho.")
        else:
            self._mostrar_feedback(msg if msg else "No se pudo deshacer.", 2000)

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hover_torre_idx = None
        if not self.resolviendo_automaticamente:
            for i, x_coord_poste in enumerate(self.torre_pos_x_coords):
                rect_torre_hover = pygame.Rect(x_coord_poste - DISCO_ANCHO_MAX // 2, self.base_y_coord - POSTE_ALTURA - (self.discos * DISCO_ALTURA_UNIDAD), DISCO_ANCHO_MAX, POSTE_ALTURA + (self.discos * DISCO_ALTURA_UNIDAD) + BASE_TORRE_ALTURA)
                if rect_torre_hover.collidepoint(mouse_pos):
                    self.hover_torre_idx = i
                    break 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.accion_al_salir = "CERRAR_JUEGO"
                return False 
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._manejar_clic_general(mouse_pos):
                    if self.accion_al_salir == "VOLVER_MENU": # Si el clic resultó en querer salir
                        return False 
                    return True 
            if evento.type == pygame.KEYDOWN: # No restringir por resolviendo_automaticamente para ESC
                if evento.key == pygame.K_ESCAPE:
                    self.accion_al_salir = "VOLVER_MENU"
                    return False 
                if not self.resolviendo_automaticamente: # Otros atajos solo si no está resolviendo
                    if evento.key == pygame.K_r: self._accion_reiniciar_juego(); return True
                    if evento.key == pygame.K_s: self._accion_resolver_automaticamente(); return True
                    if evento.key == pygame.K_u: self._accion_deshacer_movimiento(); return True
                    if pygame.K_1 <= evento.key <= pygame.K_3:
                        self._procesar_seleccion_torre(evento.key - pygame.K_1)
                        return True
        return True

    def _manejar_clic_general(self, pos_clic):
        for accion_id, rect_boton in self.mapa_botones_rects.items():
            if rect_boton.collidepoint(pos_clic):
                # Permitir Reiniciar y Volver al Menú incluso durante la resolución automática
                if self.resolviendo_automaticamente and accion_id not in ["reiniciar", "volver_menu"]:
                    self._mostrar_feedback("Resolviendo. Espere, reinicie o vuelva al menú.", 2500)
                    return True
                if   accion_id == "reiniciar": self._accion_reiniciar_juego()
                elif accion_id == "resolver_auto": self._accion_resolver_automaticamente()
                elif accion_id == "deshacer": self._accion_deshacer_movimiento()
                elif accion_id == "volver_menu": # Acción para el nuevo botón
                    self.accion_al_salir = "VOLVER_MENU"
                    # No retornamos False aquí, lo hará manejar_eventos al ver el flag.
                return True
        if not self.resolviendo_automaticamente and self.hover_torre_idx is not None:
            self._procesar_seleccion_torre(self.hover_torre_idx)
            return True
        if self.torre_origen_seleccionada_idx is not None: # Clic fuera para deseleccionar
            self.torre_origen_seleccionada_idx = None
            self.disco_seleccionado_valor = None
            return True 
        return False

    def _procesar_seleccion_torre(self, torre_idx_clicada): # (Misma función que antes)
        if self.torre_origen_seleccionada_idx is None: 
            if self.juego.torres[torre_idx_clicada]: 
                self.torre_origen_seleccionada_idx = torre_idx_clicada
                self.disco_seleccionado_valor = self.juego.torres[torre_idx_clicada][-1]
                self._mostrar_feedback(f"Disco {self.disco_seleccionado_valor} de torre {torre_idx_clicada + 1}. Elige destino.", 2500)
            else:
                self._mostrar_feedback(f"Torre {torre_idx_clicada + 1} vacía.", 1500)
        else: 
            if self.torre_origen_seleccionada_idx == torre_idx_clicada: 
                self.torre_origen_seleccionada_idx = None 
                self.disco_seleccionado_valor = None
                self._mostrar_feedback("Selección cancelada.", 1000)
            else:
                movido_ok, msg_error = self.juego.mover_disco(self.torre_origen_seleccionada_idx, torre_idx_clicada)
                if movido_ok:
                    self._mostrar_feedback(f"Movido disco de torre {self.torre_origen_seleccionada_idx + 1} a {torre_idx_clicada + 1}.")
                    self.resultado_hanoi_guardado_este_intento = False 
                    if self.juego.esta_resuelto(): self._mostrar_feedback("¡TORRES DE HANOI RESUELTAS!", 5000)
                else:
                    self._mostrar_feedback(f"Inválido: {msg_error}", 2000)
                self.torre_origen_seleccionada_idx = None
                self.disco_seleccionado_valor = None

    def _actualizar_resolucion_automatica(self): # (Misma función que antes)
        if not self.resolviendo_automaticamente: return
        tiempo_actual = pygame.time.get_ticks()
        if tiempo_actual - self.ultimo_tiempo_mov_auto >= RESOLVER_AUTO_DELAY_MS:
            if self.paso_actual_solucion_automatica < len(self.pasos_solucion_automatica):
                origen_idx, destino_idx = self.pasos_solucion_automatica[self.paso_actual_solucion_automatica]
                movido_ok, _ = self.juego.mover_disco(origen_idx, destino_idx) 
                if movido_ok:
                    self.paso_actual_solucion_automatica += 1
                    self.ultimo_tiempo_mov_auto = tiempo_actual
                    if self.juego.esta_resuelto():
                         self._mostrar_feedback("Solución automática completada.", 3000)
                         self.resolviendo_automaticamente = False 
                else:
                    self._mostrar_feedback("Error en paso automático. Deteniendo.", 3000)
                    self.resolviendo_automaticamente = False
            else: 
                self.resolviendo_automaticamente = False
                if not self.juego.esta_resuelto(): self._mostrar_feedback("Fin de pasos automáticos, pero no resuelto.", 3000)

    def ejecutar(self):
        self._mostrar_feedback(f"Torres de Hanoi - {self.discos} Discos. ¡Suerte!", 2500)
        reloj = pygame.time.Clock()
        corriendo = True
        self.accion_al_salir = None 
        while corriendo:
            corriendo = self.manejar_eventos() 
            if not corriendo: break 
            if self.resolviendo_automaticamente: self._actualizar_resolucion_automatica()
            self.dibujar_gui_completa()
            reloj.tick(FPS_HANOI)
        print(f"[TorresHanoiGUI] Saliendo. Acción: {self.accion_al_salir if self.accion_al_salir else 'CERRAR_JUEGO'}")
        return self.accion_al_salir if self.accion_al_salir else "CERRAR_JUEGO"


if __name__ == "__main__": # (Mismo bloque de prueba que antes)
    print("Ejecutando TorresHanoiGUI directamente para pruebas...")
    # ... (código de creación de directorios y sys.path si es necesario) ...
    juego_gui_hanoi = TorresHanoiGUI(discos=3) 
    resultado_salida = juego_gui_hanoi.ejecutar()
    print(f"El juego de Hanoi terminó con la acción: {resultado_salida}")
    pygame.quit()
    sys.exit()