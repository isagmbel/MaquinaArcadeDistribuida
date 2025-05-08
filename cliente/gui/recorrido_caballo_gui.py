import pygame
import sys
import os
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (RecorridoCaballo) ===
# ==============================================================================

# --- Layout y Ventana ---
VENTANA_ANCHO_CABALLO = 600
VENTANA_ALTO_CABALLO = 650
FPS_CABALLO = 60
ESPACIO_BOTONES_Y_CABALLO = 50

# --- Fuentes ---
NOMBRE_FUENTE_JUEGO_CABALLO = "nokiafc22.ttf"
TAMANO_FUENTE_NUMEROS_CABALLO = 22
TAMANO_FUENTE_BOTONES_CABALLO = 18
TAMANO_FUENTE_INFO_CABALLO = 16

# --- Colores ---
PALETAS_COLOR_CABALLO = {
    "pastel_juego": {
        "fondo": (245, 250, 240), "celda_clara": (255, 255, 255),
        "celda_oscura": (220, 240, 220), "borde_tablero": (180, 200, 180),
        "texto_numeros": (60, 80, 60), "texto_general": (70, 90, 70),
        "boton_resolver": (180, 230, 180), "boton_reiniciar": (255, 180, 180),
        "boton_verificar": (180, 180, 230), "boton_navegacion": (190, 190, 220),
        "boton_hover": (220, 220, 220),
    },
    "marron_clasico": { # Paleta alternativa
        "fondo": (245, 222, 179), # Wheat
        "celda_clara": (245, 245, 220), # Beige
        "celda_oscura": (210, 180, 140), # Tan
        "borde_tablero": (139, 69, 19),  # SaddleBrown
        "texto_numeros": (85, 50, 10),   # Dark Brown
        "texto_general": (100, 70, 20),  # Brownish
        "boton_resolver": (144, 238, 144), # LightGreen
        "boton_reiniciar": (240, 128, 128), # LightCoral
        "boton_verificar": (173, 216, 230), # LightBlue
        "boton_navegacion": (211, 211, 211), # LightGray
        "boton_hover": (230, 230, 230),
    }
}
PALETA_ACTUAL_CABALLO = "pastel_juego" # Cambia esto para probar
COLORES = PALETAS_COLOR_CABALLO[PALETA_ACTUAL_CABALLO]

# --- Elementos UI Juego ---
ANIMACION_CELDA_HOVER_INFLATE = 4 # Píxeles a inflar celda en hover
BORDE_GROSOR_CELDA_CABALLO = 1
BOTON_ANCHO_NORMAL_CABALLO = 120
BOTON_ANCHO_NAV_CABALLO = 150
BOTON_ALTO_CABALLO = 35
BOTON_BORDE_RADIO_CABALLO = 3
BOTON_BORDE_GROSOR_CABALLO = 2
BOTON_HOVER_INFLATE_CABALLO = 1

# ==============================================================================
# === IMPORTACIONES Y RUTAS ===
# ==============================================================================

SCRIPT_DIR_CABALLO = Path(__file__).resolve().parent
RUTA_FUENTE_CABALLO_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_CABALLO:
    # --- CORRECCIÓN AQUÍ: Quitar .parent ---
    RUTA_FUENTE_CABALLO_COMPLETA = SCRIPT_DIR_CABALLO / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_CABALLO
    # --- FIN CORRECCIÓN ---
    # --- DEBUG PRINT (Temporal) ---
    print(f"[DEBUG Caballo] SCRIPT_DIR: {SCRIPT_DIR_CABALLO}")
    print(f"[DEBUG Caballo] RUTA FUENTE CALCULADA: {RUTA_FUENTE_CABALLO_COMPLETA}")
    print(f"[DEBUG Caballo] EXISTE LA RUTA?: {os.path.exists(RUTA_FUENTE_CABALLO_COMPLETA)}")
    # --- FIN DEBUG PRINT ---


from cliente.juegos.recorrido_caballo import RecorridoCaballo
from cliente.comunicacion.cliente_network import get_network_client
# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (RecorridoCaballo) ===
# ==============================================================================

class RecorridoCaballoGUI:
    # === Inicialización ===
    def __init__(self, tamaño=8, ancho=VENTANA_ANCHO_CABALLO, alto=VENTANA_ALTO_CABALLO):
        pygame.init()
        self.tamaño = tamaño
        self.juego = RecorridoCaballo(tamaño)
        self.network_client = get_network_client()
        self.posicion_inicial_caballo = None
        self.resultado_guardado_este_intento = False

        # --- Ventana ---
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Recorrido del Caballo")

        # --- Asignar Colores ---
        self._asignar_colores()

        # --- Cargar Fuentes ---
        self._cargar_fuentes()

        # --- Cálculo de Dimensiones UI ---
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y_CABALLO) // self.tamaño

        # --- Estado del Juego ---
        self.modo = "jugar"
        self.solucion_actual_idx = 0
        self.paso_actual_manual = 1
        self.celda_hover = None
        self.boton_hover_texto = None

    def _asignar_colores(self):
        """Asigna los colores de la paleta actual a los atributos de la instancia."""
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

    def _cargar_fuentes(self):
        """Carga las fuentes definidas en la configuración."""
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

    # === Lógica de Dibujado ===
    def dibujar_gui_completa(self):
        """Dibuja todos los elementos de la GUI."""
        self.ventana.fill(self.color_fondo)
        self._dibujar_tablero()
        self._dibujar_botones()
        pygame.display.flip()

    def _dibujar_tablero(self):
        """Dibuja el tablero y los números de los pasos."""
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
        """Dibuja los botones de acción/navegación."""
        y_botones = self.alto - 45
        botones_info_jugar = [
            {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_resolver, "texto": "Resolver"},
            {"rect": pygame.Rect(140, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_reiniciar, "texto": "Reiniciar"},
            {"rect": pygame.Rect(270, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_verificar, "texto": "Verificar"}
        ]
        botones_info_ver_sol = [
            {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NAV_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_navegacion, "texto": "Anterior"},
            {"rect": pygame.Rect(170, y_botones, BOTON_ANCHO_NAV_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_navegacion, "texto": "Siguiente"},
            {"rect": pygame.Rect(330, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "color": self.color_boton_reiniciar, "texto": "Volver"}
        ]

        botones_actuales_info = botones_info_jugar if self.modo == "jugar" else botones_info_ver_sol

        if self.modo == "jugar":
            texto_paso = self.fuente_info.render(f"Paso: {self.paso_actual_manual}", True, self.color_texto_general)
            self.ventana.blit(texto_paso, (400, y_botones + (BOTON_ALTO_CABALLO // 2 - texto_paso.get_height() // 2)))
        elif self.juego.soluciones:
            texto_sol = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.color_texto_general)
            self.ventana.blit(texto_sol, (460, y_botones + (BOTON_ALTO_CABALLO // 2 - texto_sol.get_height() // 2)))

        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for boton_data in botones_actuales_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw = boton_data["color"]
            rect_draw = boton_data["rect"]

            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.color_boton_hover
                rect_draw = rect_draw.inflate(BOTON_HOVER_INFLATE_CABALLO * 2, BOTON_HOVER_INFLATE_CABALLO * 2)

            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=BOTON_BORDE_RADIO_CABALLO)
            border_color_darker = tuple(max(0, c - 30) for c in color_draw)
            pygame.draw.rect(self.ventana, border_color_darker, rect_draw, BOTON_BORDE_GROSOR_CABALLO, border_radius=BOTON_BORDE_RADIO_CABALLO)

            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto_general)
            self.ventana.blit(texto_render, texto_render.get_rect(center=rect_draw.center))

    # === Lógica de Comunicación con Servidor ===
    def _guardar_resultado_caballo(self, completitud: bool):
        """Envía el resultado al servidor."""
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

    # === Manejo de Eventos ===
    def manejar_eventos(self):
        """Procesa eventos de Pygame. Retorna False para salir."""
        mouse_pos = pygame.mouse.get_pos()
        # --- Actualizar hover de celda ---
        self.celda_hover = None
        if mouse_pos[1] < self.alto - ESPACIO_BOTONES_Y_CABALLO:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                self.celda_hover = (fila, col)

        # --- Procesar cola de eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                 if self._manejar_clic(evento.pos):
                     return True # Indica que se manejó una acción

        return True # Continuar

    def _manejar_clic(self, pos_clic):
        """Maneja un clic del ratón en el tablero o los botones."""
        x_click, y_click = pos_clic

        # --- Clic en Tablero ---
        if self.modo == "jugar" and y_click < self.alto - ESPACIO_BOTONES_Y_CABALLO:
            col_click = x_click // self.celda_ancho
            fila_click = y_click // self.celda_alto
            if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                if self.juego.mover_caballo(fila_click, col_click, self.paso_actual_manual):
                    if self.paso_actual_manual == 1:
                        self.posicion_inicial_caballo = (fila_click, col_click)
                    self.paso_actual_manual += 1
                    self.resultado_guardado_este_intento = False
                    return True

        # --- Clic en Botones ---
        elif y_click >= self.alto - ESPACIO_BOTONES_Y_CABALLO:
            y_botones = self.alto - 45
            botones_jugar_defs = [
                {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "accion": "resolver"},
                {"rect": pygame.Rect(140, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "accion": "reiniciar"},
                {"rect": pygame.Rect(270, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "accion": "verificar"}
            ]
            botones_ver_sol_defs = [
                {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NAV_CABALLO, BOTON_ALTO_CABALLO), "accion": "anterior"},
                {"rect": pygame.Rect(170, y_botones, BOTON_ANCHO_NAV_CABALLO, BOTON_ALTO_CABALLO), "accion": "siguiente"},
                {"rect": pygame.Rect(330, y_botones, BOTON_ANCHO_NORMAL_CABALLO, BOTON_ALTO_CABALLO), "accion": "volver"}
            ]
            botones_actuales_defs = botones_jugar_defs if self.modo == "jugar" else botones_ver_sol_defs

            for boton_def in botones_actuales_defs:
                if boton_def["rect"].collidepoint(x_click, y_click):
                    self._ejecutar_accion_boton(boton_def["accion"])
                    return True
        return False # Clic no manejado

    def _ejecutar_accion_boton(self, accion):
        """Ejecuta la lógica correspondiente a la acción de un botón."""
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
            self.modo = "jugar"
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

    # === Bucle Principal ===
    def ejecutar(self):
        """Inicia y mantiene el bucle principal del juego Recorrido del Caballo."""
        print(f"[RecorridoCaballoGUI] Iniciando juego para tamaño {self.tamaño}x{self.tamaño}...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break

            self.dibujar_gui_completa()
            reloj.tick(FPS_CABALLO)
        print("[RecorridoCaballoGUI] Saliendo del juego Recorrido del Caballo.")

# ==============================================================================
# === Bloque de Ejecución Directa (para pruebas) ===
# ==============================================================================
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