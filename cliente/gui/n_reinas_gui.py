import pygame
import sys
import math
import os
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (NReinas) ===
# ==============================================================================
VENTANA_ANCHO_NREINAS = 600
VENTANA_ALTO_NREINAS = 700 
FPS_NREINAS = 60
ESPACIO_BOTONES_Y = 50
ESPACIO_FEEDBACK_Y = 30 
NOMBRE_FUENTE_JUEGO_NREINAS = "nokiafc22.ttf"
TAMANO_FUENTE_BOTONES_NREINAS = 15 # Aún más pequeño para 6 botones
TAMANO_FUENTE_INFO_NREINAS = 16
TAMANO_FUENTE_FEEDBACK_NREINAS = 18

PALETAS_COLOR_NREINAS = { # (Misma paleta que antes, asegúrate de tener "boton_navegacion")
    "pastel_juego": {
        "fondo": (250, 240, 245), "celda_clara": (255, 255, 255),
        "celda_oscura": (230, 230, 250), "borde_tablero": (200, 180, 200),
        "texto_general": (80, 60, 80), "boton_resolver": (180, 230, 180),
        "boton_reiniciar": (255, 180, 180), "boton_verificar": (180, 180, 230),
        "boton_navegacion": (190, 190, 220), "boton_hover": (220, 220, 220), # Usado para "Ayuda", "Deshacer", "Volver Menú"
        "reina_cuerpo": (255, 120, 170), "reina_corona": (255, 180, 200),
        "sugerencia_ayuda": (0, 200, 0, 100), 
        "feedback_fondo": (220, 220, 220, 200) 
    },
    # ... (tu otra paleta) ...
}
PALETA_ACTUAL_NREINAS = "pastel_juego"
COLORES = PALETAS_COLOR_NREINAS[PALETA_ACTUAL_NREINAS]

ANIMACION_CELDA_HOVER_FACTOR = 1.1
ANIMACION_CELDA_SUAVIDAD = 0.1
BORDE_GROSOR_CELDA = 2
BOTON_ALTO = 35
BOTON_BORDE_RADIO = 3
BOTON_BORDE_GROSOR = 2
BOTON_HOVER_INFLATE = 1

# ==============================================================================
# === CLASE NReinas (Lógica del Juego) ===
# ==============================================================================
class NReinas: # (Misma clase que antes)
    def __init__(self, tamaño=8):
        self.tamaño = tamaño
        self.tablero = [[0] * tamaño for _ in range(tamaño)]
        self.soluciones = []
    def es_seguro(self, fila, col): # Original es_seguro para el resolver
        for i in range(col): # Fila a la izquierda
            if self.tablero[fila][i] == 1: return False
        for i, j in zip(range(fila, -1, -1), range(col, -1, -1)): # Diagonal sup izq
            if self.tablero[i][j] == 1: return False
        for i, j in zip(range(fila, self.tamaño, 1), range(col, -1, -1)): # Diagonal inf izq
            if self.tablero[i][j] == 1: return False
        return True
    def resolver(self, col=0):
        if col >= self.tamaño:
            self.soluciones.append([fila[:] for fila in self.tablero])
            return True
        res = False
        for i in range(self.tamaño):
            if self.es_seguro(i, col):
                self.tablero[i][col] = 1
                res = self.resolver(col + 1) or res
                self.tablero[i][col] = 0 
        return res
    def obtener_soluciones(self):
        self.soluciones = []
        self.tablero = [[0] * self.tamaño for _ in range(self.tamaño)]
        self.resolver()
        return self.soluciones
    def reiniciar(self):
        self.tablero = [[0] * self.tamaño for _ in range(self.tamaño)]
        self.soluciones = []
    def es_solucion(self): # Para verificar solución del jugador
        reinas = sum(sum(fila) for fila in self.tablero)
        if reinas != self.tamaño: return False
        posiciones = [(r, c) for r in range(self.tamaño) for c in range(self.tamaño) if self.tablero[r][c] == 1]
        for i in range(len(posiciones)):
            for j in range(i + 1, len(posiciones)):
                r1, c1 = posiciones[i]; r2, c2 = posiciones[j]
                if r1 == r2 or c1 == c2 or abs(r1 - r2) == abs(c1 - c2): return False
        return True

# ==============================================================================
# === IMPORTACIONES Y RUTAS (GUI) ===
# ==============================================================================
SCRIPT_DIR_NREINAS = Path(__file__).resolve().parent
RUTA_FUENTE_NREINAS_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_NREINAS:
    RUTA_FUENTE_NREINAS_COMPLETA = SCRIPT_DIR_NREINAS / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_NREINAS
    if not os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA) : print(f"[DEBUG NReinas] Fuente NO ENCONTRADA: {RUTA_FUENTE_NREINAS_COMPLETA}")

class MockNetworkClient: # (Misma clase que antes)
    def save_n_reinas_score(self, n_value, success, attempts, callback):
        print(f"[MockCliente NReinas] Enviado: {{'n_value': {n_value}, 'success': {success}, 'attempts': {attempts}}}}}")
        response = {'status': 'ok', 'message': 'NReinas score saved (mock)'}
        if callback: callback(response)

def get_network_client(): # (Misma clase que antes)
    try:
        from cliente.comunicacion.cliente_network import get_network_client as real_get_network_client
        return real_get_network_client()
    except ImportError:
        print("[NReinasGUI] Usando MockNetworkClient.")
        return MockNetworkClient()

# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (NReinasGUI) ===
# ==============================================================================
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
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y - ESPACIO_FEEDBACK_Y) // self.tamaño
        self.modo = "jugar"
        self.solucion_actual_idx = 0
        self.celda_hover = None
        self.boton_hover_texto = None
        self.hover_scale_anim = 1.0
        self.target_scale_anim = 1.0
        self.historial_tableros = []
        self.celda_sugerida = None
        self.mensaje_feedback_texto = ""
        self.mensaje_feedback_tiempo_fin = 0
        self.duracion_feedback_ms = 3000
        self.accion_al_salir = None # "VOLVER_MENU" o "CERRAR_JUEGO"

    def _asignar_colores(self): # (Misma función que antes)
        self.color_fondo = COLORES["fondo"]; self.color_celda_clara = COLORES["celda_clara"]
        self.color_celda_oscura = COLORES["celda_oscura"]; self.color_borde_tablero = COLORES["borde_tablero"]
        self.color_texto = COLORES["texto_general"]; self.color_boton_resolver = COLORES["boton_resolver"]
        self.color_boton_reiniciar = COLORES["boton_reiniciar"]; self.color_boton_verificar = COLORES["boton_verificar"]
        self.color_boton_navegacion = COLORES["boton_navegacion"]; self.color_boton_hover = COLORES["boton_hover"]
        self.color_reina_cuerpo = COLORES["reina_cuerpo"]; self.color_reina_corona = COLORES["reina_corona"]
        self.color_sugerencia_ayuda = COLORES["sugerencia_ayuda"]; self.color_feedback_fondo = COLORES["feedback_fondo"]

    def _cargar_fuentes(self): # (Misma función que antes)
        try:
            if RUTA_FUENTE_NREINAS_COMPLETA and os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA):
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_INFO_NREINAS)
                self.fuente_feedback = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_FEEDBACK_NREINAS)
            else:
                if NOMBRE_FUENTE_JUEGO_NREINAS: print(f"Advertencia: Fuente {NOMBRE_FUENTE_JUEGO_NREINAS} no encontrada. Usando SysFont.")
                self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_NREINAS)
                self.fuente_feedback = pygame.font.SysFont('Arial', TAMANO_FUENTE_FEEDBACK_NREINAS)
        except Exception as e:
            print(f"Error cargando fuente para NReinas ({e}). Usando SysFont.")
            self.fuente_botones, self.fuente_info, self.fuente_feedback = [pygame.font.SysFont('Arial', s) for s in [TAMANO_FUENTE_BOTONES_NREINAS, TAMANO_FUENTE_INFO_NREINAS, TAMANO_FUENTE_FEEDBACK_NREINAS]]

    def dibujar_gui_completa(self): # (Misma función que antes)
        self.ventana.fill(self.color_fondo)
        self._dibujar_tablero()
        self._dibujar_botones()
        self._dibujar_feedback_mensaje()
        pygame.display.flip()

    def _dibujar_tablero(self): # (Misma función que antes)
        self.hover_scale_anim += (self.target_scale_anim - self.hover_scale_anim) * ANIMACION_CELDA_SUAVIDAD
        for fila in range(self.tamaño):
            for col in range(self.tamaño):
                color_base = self.color_celda_clara if (fila + col) % 2 == 0 else self.color_celda_oscura
                rect_base = pygame.Rect(col * self.celda_ancho, fila * self.celda_alto, self.celda_ancho, self.celda_alto)
                current_scale, color_draw, rect_draw = 1.0, color_base, rect_base
                if self.celda_hover == (fila, col):
                    current_scale = self.hover_scale_anim
                    rect_draw = rect_base.inflate(int(self.celda_ancho * (current_scale - 1)), int(self.celda_alto * (current_scale - 1))); rect_draw.center = rect_base.center
                    color_draw = tuple(max(0, min(255, c + 20)) for c in color_base)
                pygame.draw.rect(self.ventana, color_draw, rect_draw)
                if self.celda_sugerida == (fila, col):
                    s = pygame.Surface((rect_draw.width, rect_draw.height), pygame.SRCALPHA)
                    pygame.draw.circle(s, self.color_sugerencia_ayuda, (rect_draw.width//2, rect_draw.height//2), min(rect_draw.width, rect_draw.height)//3)
                    self.ventana.blit(s, rect_draw.topleft)
                if self.juego.tablero[fila][col] == 1: self._dibujar_reina(rect_base.centerx, rect_base.centery, current_scale)
                pygame.draw.rect(self.ventana, self.color_borde_tablero, rect_draw, BORDE_GROSOR_CELDA)

    def _dibujar_reina(self, centro_x, centro_y, scale=1.0): # (Misma función que antes)
        radio_base = min(self.celda_ancho, self.celda_alto) // 3.5 
        radio_scaled = max(1, int(radio_base * scale))
        pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (centro_x, centro_y), radio_scaled)
        corona_radius = max(1, int(radio_scaled * 0.6))
        pygame.draw.circle(self.ventana, self.color_reina_corona, (centro_x, centro_y), corona_radius)
        pico_radius = max(1, int(radio_scaled * 0.15))
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            self.ventana.blit(pygame.Surface((pico_radius*2, pico_radius*2), pygame.SRCALPHA), (centro_x + int(radio_scaled*0.8*math.cos(angle)) - pico_radius, centro_y + int(radio_scaled*0.8*math.sin(angle)) - pico_radius), special_flags=pygame.BLEND_RGBA_ADD) # Fake draw
            pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (int(centro_x + radio_scaled * 0.8 * math.cos(angle)), int(centro_y + radio_scaled * 0.8 * math.sin(angle))), pico_radius)


    def _dibujar_botones(self):
        y_botones = self.alto - ESPACIO_BOTONES_Y + (ESPACIO_BOTONES_Y - BOTON_ALTO) / 2
        
        # Botones para modo "jugar" - Ahora son 6
        num_botones_jugar = 6
        margen_total_botones, espacio_entre_botones = 20, 5
        ancho_total_disp_jugar = self.ancho - margen_total_botones - (num_botones_jugar -1) * espacio_entre_botones
        ancho_boton_jugar = ancho_total_disp_jugar // num_botones_jugar
        
        # Botones para modo "ver_soluciones" - Se mantienen 3
        num_botones_ver_sol = 3
        ancho_total_disp_ver_sol = self.ancho - margen_total_botones - (num_botones_ver_sol -1) * espacio_entre_botones
        ancho_boton_ver_sol = ancho_total_disp_ver_sol // num_botones_ver_sol

        offset_x = 10
        
        self.mapa_botones_rects = {} # {accion_id: rect}
        botones_actuales_info = []

        if self.modo == "jugar":
            defs_jugar = [
                {"texto": "Resolver", "accion_id": "resolver", "color": self.color_boton_resolver},
                {"texto": "Reiniciar", "accion_id": "reiniciar", "color": self.color_boton_reiniciar},
                {"texto": "Verificar", "accion_id": "verificar", "color": self.color_boton_verificar},
                {"texto": "Ayuda", "accion_id": "ayuda", "color": self.color_boton_navegacion},
                {"texto": "Deshacer", "accion_id": "deshacer", "color": self.color_boton_navegacion},
                {"texto": "Menú", "accion_id": "volver_menu", "color": self.color_boton_navegacion} # Nuevo
            ]
            for i, d in enumerate(defs_jugar):
                rect = pygame.Rect(offset_x + i * (ancho_boton_jugar + espacio_entre_botones), y_botones, ancho_boton_jugar, BOTON_ALTO)
                botones_actuales_info.append({"rect": rect, "color": d["color"], "texto": d["texto"]})
                self.mapa_botones_rects[d["accion_id"]] = rect
        else: # modo "ver_soluciones"
            defs_ver_sol = [
                {"texto": "Anterior", "accion_id": "anterior", "color": self.color_boton_navegacion},
                {"texto": "Siguiente", "accion_id": "siguiente", "color": self.color_boton_navegacion},
                {"texto": "Volver", "accion_id": "volver", "color": self.color_boton_reiniciar} # "Volver" te lleva a modo jugar y reinicia
            ]
            for i, d in enumerate(defs_ver_sol):
                rect = pygame.Rect(offset_x + i * (ancho_boton_ver_sol + espacio_entre_botones), y_botones, ancho_boton_ver_sol, BOTON_ALTO)
                botones_actuales_info.append({"rect": rect, "color": d["color"], "texto": d["texto"]})
                self.mapa_botones_rects[d["accion_id"]] = rect

            if hasattr(self.juego, 'soluciones') and self.juego.soluciones:
                texto_sol_render = self.fuente_info.render(f"Sol: {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.color_texto)
                pos_x_texto_sol = self.mapa_botones_rects["volver"].right + 15 # A la derecha del botón "Volver"
                if pos_x_texto_sol + texto_sol_render.get_width() < self.ancho -10:
                     self.ventana.blit(texto_sol_render, (pos_x_texto_sol, y_botones + (BOTON_ALTO // 2 - texto_sol_render.get_height() // 2)))

        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()
        for boton_data in botones_actuales_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw, rect_draw = boton_data["color"], boton_data["rect"]
            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.color_boton_hover
                rect_draw = rect_draw.inflate(BOTON_HOVER_INFLATE * 2, BOTON_HOVER_INFLATE * 2)
            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=BOTON_BORDE_RADIO)
            border_color_darker = tuple(max(0, c - 30) for c in color_draw)
            pygame.draw.rect(self.ventana, border_color_darker, rect_draw, BOTON_BORDE_GROSOR, border_radius=BOTON_BORDE_RADIO)
            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto)
            self.ventana.blit(texto_render, texto_render.get_rect(center=rect_draw.center))

    def _dibujar_feedback_mensaje(self): # (Misma función que antes)
        if self.mensaje_feedback_texto and pygame.time.get_ticks() < self.mensaje_feedback_tiempo_fin:
            texto_render = self.fuente_feedback.render(self.mensaje_feedback_texto, True, self.color_texto)
            rect_texto = texto_render.get_rect(centerx=self.ancho / 2, bottom=self.alto - ESPACIO_BOTONES_Y - (ESPACIO_FEEDBACK_Y - texto_render.get_height())/2 - 5) 
            fondo_rect = rect_texto.inflate(20, 10)
            s = pygame.Surface(fondo_rect.size, pygame.SRCALPHA); s.fill(self.color_feedback_fondo)
            self.ventana.blit(s, fondo_rect.topleft)
            self.ventana.blit(texto_render, rect_texto)
        elif pygame.time.get_ticks() >= self.mensaje_feedback_tiempo_fin: self.mensaje_feedback_texto = ""

    def _mostrar_feedback(self, texto, duracion_ms=None): # (Misma función que antes)
        self.mensaje_feedback_texto = texto
        if duracion_ms is None: duracion_ms = self.duracion_feedback_ms
        self.mensaje_feedback_tiempo_fin = pygame.time.get_ticks() + duracion_ms
        print(f"[Feedback GUI NReinas] {texto}")

    def _guardar_resultado_nreinas(self, exito: bool): # (Misma función que antes)
        print(f"[NReinasGUI] Guardando: N={self.tamaño}, Éxito={exito}, Intentos={self.intentos_nreinas}")
        def callback_guardado(response):
            status = "Ok" if response and response.get("status") == "ok" else "Error"
            msg = response.get('message', 'N/A') if response else "Sin respuesta"
            self._mostrar_feedback(f"Guardado Servidor: {status} - {msg}", 2500)
        self.network_client.save_n_reinas_score(n_value=self.tamaño, success=exito, attempts=self.intentos_nreinas, callback=callback_guardado)

    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        nuevo_hover_celda = None
        zona_tablero_alto = self.alto - ESPACIO_BOTONES_Y - ESPACIO_FEEDBACK_Y
        if mouse_pos[1] < zona_tablero_alto:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño: nuevo_hover_celda = (fila, col)
        if nuevo_hover_celda != self.celda_hover:
            self.celda_hover = nuevo_hover_celda
            self.target_scale_anim = ANIMACION_CELDA_HOVER_FACTOR if nuevo_hover_celda else 1.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.accion_al_salir = "CERRAR_JUEGO"
                return False
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if self._manejar_clic(evento.pos):
                    if self.accion_al_salir == "VOLVER_MENU": return False
                    return True # Clic manejado, continuar
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.accion_al_salir = "VOLVER_MENU"
                    return False
                # Aquí podrías añadir otros atajos de teclado si quieres
        return True

    def _manejar_clic(self, pos_clic):
        x_click, y_click = pos_clic
        self.celda_sugerida = None 
        zona_tablero_alto = self.alto - ESPACIO_BOTONES_Y - ESPACIO_FEEDBACK_Y

        if self.modo == "jugar" and y_click < zona_tablero_alto: # Clic en tablero
            col_click = x_click // self.celda_ancho
            fila_click = y_click // self.celda_alto
            if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                copia_tablero_anterior = [fila[:] for fila in self.juego.tablero]
                self.historial_tableros.append(copia_tablero_anterior)
                if len(self.historial_tableros) > 20: self.historial_tableros.pop(0)
                self.juego.tablero[fila_click][col_click] = 1 - self.juego.tablero[fila_click][col_click]
                return True
        
        # Clic en zona de botones
        # Reconstruir self.mapa_botones_rects si no se hizo en dibujar_botones (se hace allí ahora)
        for accion_id, rect_boton in self.mapa_botones_rects.items():
            if rect_boton.collidepoint(x_click, y_click):
                self._ejecutar_accion_boton(accion_id)
                return True # Clic en botón manejado
        return False

    def _ejecutar_accion_boton(self, accion_id):
        self.celda_sugerida = None
        if accion_id == "resolver":
            soluciones = self.juego.obtener_soluciones()
            if soluciones:
                self.modo = "ver_soluciones"; self.solucion_actual_idx = 0
                self.juego.tablero = [f[:] for f in soluciones[self.solucion_actual_idx]]
                self._mostrar_feedback(f"Mostrando {len(soluciones)} soluciones."); self.historial_tableros = []
            else: self._mostrar_feedback("No se encontraron soluciones.")
        elif accion_id == "reiniciar":
            self.juego.reiniciar(); self.intentos_nreinas = 0; self.modo = "jugar"
            self.historial_tableros = []; self._mostrar_feedback("Tablero reiniciado.")
        elif accion_id == "verificar":
            self.intentos_nreinas += 1
            es_valida = self.juego.es_solucion()
            self._mostrar_feedback("¡Solución Correcta!" if es_valida else "Solución Incorrecta.")
            self._guardar_resultado_nreinas(exito=es_valida)
        elif accion_id == "anterior" and self.juego.soluciones:
            self.solucion_actual_idx = (self.solucion_actual_idx - 1 + len(self.juego.soluciones)) % len(self.juego.soluciones)
            self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
        elif accion_id == "siguiente" and self.juego.soluciones:
            self.solucion_actual_idx = (self.solucion_actual_idx + 1) % len(self.juego.soluciones)
            self.juego.tablero = [f[:] for f in self.juego.soluciones[self.solucion_actual_idx]]
        elif accion_id == "volver": # Volver de ver soluciones a jugar
            self.modo = "jugar"; self.juego.reiniciar(); self.historial_tableros = []
            self._mostrar_feedback("Modo de juego. Tablero reiniciado.")
        elif accion_id == "deshacer":
            if self.modo == "jugar" and self.historial_tableros:
                self.juego.tablero = self.historial_tableros.pop()
                self._mostrar_feedback("Movimiento deshecho.")
            elif self.modo != "jugar": self._mostrar_feedback("Deshacer no disponible.")
            else: self._mostrar_feedback("No hay movimientos para deshacer.")
        elif accion_id == "ayuda":
            if self.modo == "jugar": self._dar_ayuda()
            else: self._mostrar_feedback("Ayuda no disponible.")
        elif accion_id == "volver_menu":
            self.accion_al_salir = "VOLVER_MENU"
            # No hace falta hacer más, el bucle principal lo gestionará

    def _dar_ayuda(self): # (Misma función que antes)
        self.celda_sugerida = None
        # Usar una copia del tablero para probar es_seguro_general
        tablero_copia = [fila[:] for fila in self.juego.tablero]
        def es_seguro_general_para_ayuda(r_test, c_test, tablero_actual):
            # Verificar fila y columna
            for i in range(self.tamaño):
                if tablero_actual[r_test][i] == 1 and i != c_test: return False
                if tablero_actual[i][c_test] == 1 and i != r_test: return False
            # Verificar diagonales
            for i in range(self.tamaño):
                for j in range(self.tamaño):
                    if (i != r_test or j != c_test) and tablero_actual[i][j] == 1:
                        if abs(r_test - i) == abs(c_test - j): return False
            return True

        for col in range(self.tamaño): # Priorizar columnas de izq a der
            col_tiene_reina = any(self.juego.tablero[r][col] == 1 for r in range(self.tamaño))
            if not col_tiene_reina: # Si la columna no tiene reina
                for fila in range(self.tamaño):
                    if self.juego.tablero[fila][col] == 0 and es_seguro_general_para_ayuda(fila, col, self.juego.tablero):
                        self.celda_sugerida = (fila, col)
                        self._mostrar_feedback(f"Sugerencia: ({fila+1}, {chr(ord('A')+col)}).")
                        return
        # Si no se encontró en columnas vacías, buscar cualquier celda segura
        for r in range(self.tamaño):
            for c in range(self.tamaño):
                if self.juego.tablero[r][c] == 0 and es_seguro_general_para_ayuda(r, c, self.juego.tablero):
                    self.celda_sugerida = (r, c)
                    self._mostrar_feedback(f"Sugerencia alternativa: ({r+1}, {chr(ord('A')+c)}).")
                    return
        self._mostrar_feedback("No se encontró ayuda clara.")

    def ejecutar(self):
        self._mostrar_feedback(f"N-Reinas: Coloca {self.tamaño} reinas sin que se amenacen.", 3000)
        reloj = pygame.time.Clock()
        corriendo = True
        self.accion_al_salir = None 
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break 
            self.dibujar_gui_completa()
            reloj.tick(FPS_NREINAS)
        print(f"[NReinasGUI] Saliendo. Acción: {self.accion_al_salir if self.accion_al_salir else 'CERRAR_JUEGO'}")
        return self.accion_al_salir if self.accion_al_salir else "CERRAR_JUEGO"


if __name__ == "__main__": # (Mismo bloque de prueba que antes)
    print("Ejecutando NReinasGUI directamente para pruebas...")
    # ... (código de creación de directorios y sys.path si es necesario) ...
    juego_gui_nreinas = NReinasGUI(tamaño=8)
    resultado_salida = juego_gui_nreinas.ejecutar()
    print(f"El juego NReinas terminó con la acción: {resultado_salida}")
    pygame.quit()
    sys.exit()