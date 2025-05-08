import pygame
import sys
import time
import os
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (TorresHanoi) ===
# ==============================================================================

# --- Layout y Ventana ---
VENTANA_ANCHO_HANOI = 800
VENTANA_ALTO_HANOI = 600
FPS_HANOI = 30 # Más bajo puede ser mejor para ver animaciones o resolución automática

# --- Fuentes ---
NOMBRE_FUENTE_JUEGO_HANOI = "nokiafc22.ttf"
TAMANO_FUENTE_INFO_HANOI = 20
TAMANO_FUENTE_BOTONES_HANOI = 18
TAMANO_FUENTE_TITULO_HANOI = 30 # Para "¡Resuelto!"

# --- Colores ---
PALETAS_COLOR_HANOI = {
    "pastel_juego": {
        "fondo": (240, 245, 250), "base_torre": (200, 190, 170),
        "poste_torre": (180, 170, 150),
        "discos": [ (255, 182, 193), (173, 216, 230), (144, 238, 144), (255, 255, 153),
                   (221, 160, 221), (175, 238, 238), (255, 218, 185), (211, 211, 211) ],
        "texto_info": (70, 70, 90), "texto_botones": (60, 60, 80),
        "boton_normal": (200, 200, 220), "boton_hover": (220, 220, 240),
        "texto_resuelto": (80, 160, 80)
    },
    "madera_oscura": { # Paleta alternativa
        "fondo": (110, 80, 60), # Marrón oscuro
        "base_torre": (60, 40, 30), # Más oscuro
        "poste_torre": (80, 60, 50),
        "discos": [ (255, 99, 71), (255, 165, 0), (255, 215, 0), (154, 205, 50),
                   (32, 178, 170), (100, 149, 237), (186, 85, 211), (218, 112, 214) ], # Colores más saturados
        "texto_info": (240, 230, 220), # Texto claro
        "texto_botones": (220, 210, 200),
        "boton_normal": (100, 70, 50), # Botones oscuros
        "boton_hover": (120, 90, 70),
        "texto_resuelto": (144, 238, 144) # Verde claro
    }
}
PALETA_ACTUAL_HANOI = "pastel_juego" 
COLORES = PALETAS_COLOR_HANOI[PALETA_ACTUAL_HANOI]

# --- Elementos UI Juego ---
BASE_TORRE_Y_OFFSET = 60 # Distancia desde abajo
BASE_TORRE_ALTURA = 20
BASE_TORRE_MARGEN_X = 0.1 # Porcentaje del ancho para margen base
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
BOTON_POS_X_HANOI = VENTANA_ANCHO_HANOI - 170 # Posición X común para botones
BOTON_ESPACIO_Y_HANOI = 40
RESOLVER_AUTO_DELAY_MS = 400 # Pausa entre movimientos automáticos

# ==============================================================================
# === IMPORTACIONES Y RUTAS ===
# ==============================================================================

SCRIPT_DIR_HANOI = Path(__file__).resolve().parent
RUTA_FUENTE_HANOI_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_HANOI:
    # --- CORRECCIÓN AQUÍ: Quitar .parent ---
    RUTA_FUENTE_HANOI_COMPLETA = SCRIPT_DIR_HANOI / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_HANOI
    # --- FIN CORRECCIÓN ---
    # --- DEBUG PRINT (Temporal) ---
    print(f"[DEBUG Hanoi] SCRIPT_DIR: {SCRIPT_DIR_HANOI}")
    print(f"[DEBUG Hanoi] RUTA FUENTE CALCULADA: {RUTA_FUENTE_HANOI_COMPLETA}")
    print(f"[DEBUG Hanoi] EXISTE LA RUTA?: {os.path.exists(RUTA_FUENTE_HANOI_COMPLETA)}")
    # --- FIN DEBUG PRINT ---

from cliente.juegos.torres_hanoi import TorresHanoi
from cliente.comunicacion.cliente_network import get_network_client

# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (TorresHanoi) ===
# ==============================================================================

class TorresHanoiGUI:
    # === Inicialización ===
    def __init__(self, discos=3, ancho=VENTANA_ANCHO_HANOI, alto=VENTANA_ALTO_HANOI):
        pygame.init()
        self.discos = discos
        self.juego = TorresHanoi(discos)
        self.network_client = get_network_client()
        self.resultado_hanoi_guardado = False

        # --- Ventana ---
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Torres de Hanoi")

        # --- Asignar Colores ---
        self._asignar_colores()

        # --- Cargar Fuentes ---
        self._cargar_fuentes()

        # --- Cálculo de Dimensiones UI ---
        self.torre_pos_x_coords = [ancho // 4, ancho // 2, 3 * ancho // 4]
        self.base_y_coord = alto - BASE_TORRE_Y_OFFSET

        # --- Estado del Juego ---
        self.disco_seleccionado_val = None
        self.torre_origen_idx = None
        self.resolviendo_auto = False
        self.pasos_solucion_auto = []
        self.paso_actual_auto = 0
        self.hover_torre_idx = None
        self.hover_boton_texto = None

    def _asignar_colores(self):
        """Asigna los colores de la paleta actual a los atributos de la instancia."""
        self.color_fondo = COLORES["fondo"]
        self.color_base_torre = COLORES["base_torre"]
        self.color_poste_torre = COLORES["poste_torre"]
        self.colores_discos = COLORES["discos"] # Lista de colores
        self.color_texto_info = COLORES["texto_info"]
        self.color_texto_botones = COLORES["texto_botones"]
        self.color_boton_normal = COLORES["boton_normal"]
        self.color_boton_hover = COLORES["boton_hover"]
        self.color_texto_resuelto = COLORES["texto_resuelto"]

    def _cargar_fuentes(self):
        """Carga las fuentes definidas en la configuración."""
        try:
            if RUTA_FUENTE_HANOI_COMPLETA and os.path.exists(RUTA_FUENTE_HANOI_COMPLETA):
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.Font(RUTA_FUENTE_HANOI_COMPLETA, TAMANO_FUENTE_TITULO_HANOI)
            elif NOMBRE_FUENTE_JUEGO_HANOI:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_HANOI} no encontrada.")
            else:
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_HANOI)
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_HANOI)
                self.fuente_titulo_juego = pygame.font.Font(None, TAMANO_FUENTE_TITULO_HANOI)
        except Exception as e:
            print(f"Error cargando fuente para TorresHanoi ({e}). Usando SysFont.")
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_HANOI)
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_HANOI)
            self.fuente_titulo_juego = pygame.font.SysFont('Arial', TAMANO_FUENTE_TITULO_HANOI, bold=True)

    # === Lógica de Dibujado ===
    def dibujar_gui_completa(self):
        """Dibuja todos los elementos de la GUI."""
        self.ventana.fill(self.color_fondo)
        self._dibujar_torres_y_discos()
        self._dibujar_ui_info()
        pygame.display.flip()

    def _dibujar_torres_y_discos(self):
        """Dibuja la base, los postes y los discos."""
        # Base
        base_ancho = self.ancho * (1 - 2 * BASE_TORRE_MARGEN_X)
        pygame.draw.rect(self.ventana, self.color_base_torre,
                         (self.ancho * BASE_TORRE_MARGEN_X, self.base_y_coord, base_ancho, BASE_TORRE_ALTURA),
                         border_radius=3)

        # Postes
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            color_poste = self.color_poste_torre
            if self.hover_torre_idx == i:
                color_poste = tuple(max(0, c + 15) for c in self.color_poste_torre)
            pygame.draw.rect(self.ventana, color_poste,
                            (x_coord - POSTE_ANCHO // 2, self.base_y_coord - POSTE_ALTURA,
                             POSTE_ANCHO, POSTE_ALTURA), border_top_left_radius=5, border_top_right_radius=5)

        # Discos
        for torre_idx, torre_discos in enumerate(self.juego.torres):
            for disco_idx_en_torre, valor_disco in enumerate(torre_discos):
                ancho_disco = DISCO_ANCHO_MAX - (DISCO_REDUCCION_ANCHO * (self.discos - valor_disco))
                x_disco = self.torre_pos_x_coords[torre_idx] - ancho_disco // 2
                y_disco = self.base_y_coord - BASE_TORRE_ALTURA - (disco_idx_en_torre + 1) * DISCO_ALTURA_UNIDAD

                color_idx_disco = (valor_disco - 1) % len(self.colores_discos)
                color_disco_base = self.colores_discos[color_idx_disco]
                rect_disco = pygame.Rect(x_disco, y_disco, ancho_disco, DISCO_ALTURA_UNIDAD)

                # Efecto hover/seleccionado
                if self.torre_origen_idx == torre_idx and disco_idx_en_torre == len(torre_discos) - 1:
                    hover_color = tuple(max(0, c - 30) for c in color_disco_base)
                    pygame.draw.rect(self.ventana, hover_color, rect_disco.inflate(DISCO_HOVER_INFLATE, DISCO_HOVER_INFLATE), border_radius=3)

                pygame.draw.rect(self.ventana, color_disco_base, rect_disco, border_radius=3)
                border_color_disco = tuple(max(0, c - 50) for c in color_disco_base)
                pygame.draw.rect(self.ventana, border_color_disco, rect_disco, DISCO_BORDE_GROSOR, border_radius=3)

    def _dibujar_ui_info(self):
        """Dibuja la información de movimientos, estado y botones."""
        # Texto de Movimientos
        movimientos_texto_render = self.fuente_info.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})",
            True, self.color_texto_info)
        self.ventana.blit(movimientos_texto_render, (20, 20))

        # Texto "Resuelto"
        if self.juego.esta_resuelto():
            if not self.resultado_hanoi_guardado:
                self._guardar_resultado_hanoi(exito=True) # Guardar al dibujar si no se ha guardado
            felicitacion_render = self.fuente_titulo_juego.render("¡Resuelto!", True, self.color_texto_resuelto)
            self.ventana.blit(felicitacion_render, felicitacion_render.get_rect(center=(self.ancho // 2, 80)))

        # Botones
        botones_info = [
            {"texto": "Reiniciar", "pos": (BOTON_POS_X_HANOI, 30), "ancho": BOTON_ANCHO_HANOI, "accion": self.accion_reiniciar},
            {"texto": "Resolver", "pos": (BOTON_POS_X_HANOI, 30 + BOTON_ESPACIO_Y_HANOI), "ancho": BOTON_ANCHO_HANOI, "accion": self.accion_resolver_auto},
            {"texto": "Deshacer", "pos": (BOTON_POS_X_HANOI, 30 + 2*BOTON_ESPACIO_Y_HANOI), "ancho": BOTON_ANCHO_HANOI, "accion": self.accion_deshacer_wrapper}
        ]

        self.hover_boton_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for boton_data in botones_info:
            x_b, y_b = boton_data["pos"]
            rect_b = pygame.Rect(x_b, y_b, boton_data["ancho"], BOTON_ALTO_HANOI)
            hover_b = rect_b.collidepoint(mouse_pos)

            color_b_draw = self.color_boton_normal
            if hover_b:
                self.hover_boton_texto = boton_data["texto"]
                color_b_draw = self.color_boton_hover

            pygame.draw.rect(self.ventana, color_b_draw, rect_b, border_radius=BOTON_BORDE_RADIO_HANOI)
            border_color_darker = tuple(max(0, c - 30) for c in color_b_draw)
            pygame.draw.rect(self.ventana, border_color_darker, rect_b, BOTON_BORDE_GROSOR_HANOI, border_radius=BOTON_BORDE_RADIO_HANOI)

            texto_b_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto_botones)
            self.ventana.blit(texto_b_render, texto_b_render.get_rect(center=rect_b.center))

    # === Lógica de Acciones y Comunicación ===
    def accion_deshacer_wrapper(self):
        """Wrapper para deshacer que resetea el flag de guardado."""
        self.juego.deshacer_ultimo_movimiento()
        self.resultado_hanoi_guardado = False

    def _guardar_resultado_hanoi(self, exito: bool):
        """Envía el resultado al servidor."""
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
        """Reinicia el estado del juego y la GUI."""
        self.juego.reiniciar()
        self.resolviendo_auto = False
        self.resultado_hanoi_guardado = False
        self.torre_origen_idx = None
        self.disco_seleccionado_val = None

    def accion_resolver_auto(self):
        """Inicia la resolución automática."""
        if not self.resolviendo_auto:
            self.accion_reiniciar()
            self.resolviendo_auto = True
            self.pasos_solucion_auto = []
            self._generar_solucion_hanoi(self.discos, 0, 2, 1) # Asumiendo 3 torres: 0=origen, 2=destino, 1=auxiliar
            self.paso_actual_auto = 0

    def _generar_solucion_hanoi(self, n_discos, origen_idx, destino_idx, aux_idx):
        """Genera recursivamente los pasos para la solución."""
        if n_discos == 0: return
        self._generar_solucion_hanoi(n_discos - 1, origen_idx, aux_idx, destino_idx)
        self.pasos_solucion_auto.append((origen_idx, destino_idx))
        self._generar_solucion_hanoi(n_discos - 1, aux_idx, destino_idx, origen_idx)

    # === Manejo de Eventos ===
    def manejar_eventos(self):
        """Procesa eventos de Pygame. Retorna False para salir."""
        mouse_pos = pygame.mouse.get_pos()
        # --- Actualizar hover de torre ---
        self.hover_torre_idx = None
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            # Área de detección un poco más generosa
            torre_rect_detect = pygame.Rect(x_coord - DISCO_ANCHO_MAX // 1.5,
                                            self.base_y_coord - POSTE_ALTURA - DISCO_ALTURA_UNIDAD * self.discos,
                                            DISCO_ANCHO_MAX * 1.33,
                                            POSTE_ALTURA + DISCO_ALTURA_UNIDAD * self.discos)
            if torre_rect_detect.collidepoint(mouse_pos):
                self.hover_torre_idx = i

        # --- Procesar cola de eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not self.resolviendo_auto:
                if self._manejar_clic(mouse_pos):
                    return True

            if evento.type == pygame.KEYDOWN:
                if self._manejar_teclado(evento.key):
                   return True
        return True

    def _manejar_clic(self, pos_clic):
        """Maneja un clic del ratón en los botones o torres."""
        # --- Clic en Botones ---
        botones_info = [
             {"rect": pygame.Rect(BOTON_POS_X_HANOI, 30, BOTON_ANCHO_HANOI, BOTON_ALTO_HANOI), "accion_obj": self.accion_reiniciar},
             {"rect": pygame.Rect(BOTON_POS_X_HANOI, 30 + BOTON_ESPACIO_Y_HANOI, BOTON_ANCHO_HANOI, BOTON_ALTO_HANOI), "accion_obj": self.accion_resolver_auto},
             {"rect": pygame.Rect(BOTON_POS_X_HANOI, 30 + 2*BOTON_ESPACIO_Y_HANOI, BOTON_ANCHO_HANOI, BOTON_ALTO_HANOI), "accion_obj": self.accion_deshacer_wrapper}
        ]
        for boton_data in botones_info:
            if boton_data["rect"].collidepoint(pos_clic):
                boton_data["accion_obj"]()
                return True # Clic manejado

        # --- Clic en Torres ---
        if self.hover_torre_idx is not None:
            if self.torre_origen_idx is None: # Seleccionar torre origen
                if self.juego.torres[self.hover_torre_idx]:
                    self.torre_origen_idx = self.hover_torre_idx
                    self.disco_seleccionado_val = self.juego.torres[self.hover_torre_idx][-1]
            else: # Seleccionar torre destino
                self.juego.mover_disco(self.torre_origen_idx, self.hover_torre_idx)
                self.resultado_hanoi_guardado = False # Resetear flag al mover manualmente
                self.torre_origen_idx = None # Deseleccionar siempre
                self.disco_seleccionado_val = None
            return True # Clic manejado (incluso si el movimiento fue inválido)

        # Si no se hizo clic en nada relevante, deseleccionar
        self.torre_origen_idx = None
        self.disco_seleccionado_val = None
        return False # Clic no manejado

    def _manejar_teclado(self, key):
        """Maneja eventos de teclado."""
        if key == pygame.K_r: self.accion_reiniciar(); return True
        elif key == pygame.K_s: self.accion_resolver_auto(); return True
        elif key == pygame.K_u: self.accion_deshacer_wrapper(); return True
        return False

    # === Lógica de Actualización (para resolución automática) ===
    def actualizar_resolucion_automatica(self):
        """Realiza un paso de la resolución automática si está activa."""
        if self.resolviendo_auto and self.paso_actual_auto < len(self.pasos_solucion_auto):
            origen_idx, destino_idx = self.pasos_solucion_auto[self.paso_actual_auto]
            movido = self.juego.mover_disco(origen_idx, destino_idx)
            if movido: # Solo incrementar paso si el movimiento fue válido (debería serlo siempre)
                self.paso_actual_auto += 1
            pygame.time.delay(RESOLVER_AUTO_DELAY_MS)
        elif self.resolviendo_auto and self.paso_actual_auto >= len(self.pasos_solucion_auto):
            self.resolviendo_auto = False # Terminó

    # === Bucle Principal ===
    def ejecutar(self):
        """Inicia y mantiene el bucle principal del juego Torres de Hanoi."""
        print(f"[TorresHanoiGUI] Iniciando juego para {self.discos} discos...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break

            if self.resolviendo_auto:
                self.actualizar_resolucion_automatica()

            self.dibujar_gui_completa()
            reloj.tick(FPS_HANOI)
        print("[TorresHanoiGUI] Saliendo del juego Torres de Hanoi.")

# ==============================================================================
# === Bloque de Ejecución Directa (para pruebas) ===
# ==============================================================================
if __name__ == "__main__":
    print("Ejecutando TorresHanoiGUI directamente para pruebas...")
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG: Project root {PROJECT_ROOT_TEST} in sys.path.")

    juego_gui_hanoi = TorresHanoiGUI(discos=3) # Probar con 3 discos
    juego_gui_hanoi.ejecutar()
    pygame.quit()
    sys.exit()