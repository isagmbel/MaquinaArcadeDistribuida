import pygame
import sys
import math
import os
from pathlib import Path

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (NReinas) ===
# ==============================================================================

# --- Layout y Ventana ---
VENTANA_ANCHO_NREINAS = 600
VENTANA_ALTO_NREINAS = 650
FPS_NREINAS = 60
ESPACIO_BOTONES_Y = 50 # Espacio vertical desde abajo para la zona de botones

# --- Fuentes ---
NOMBRE_FUENTE_JUEGO_NREINAS = "nokiafc22.ttf" # O "04B_03_.TTF", etc.
TAMANO_FUENTE_BOTONES_NREINAS = 18
TAMANO_FUENTE_INFO_NREINAS = 16

# --- Colores ---
PALETAS_COLOR_NREINAS = {
    "pastel_juego": {
        "fondo": (250, 240, 245), "celda_clara": (255, 255, 255),
        "celda_oscura": (230, 230, 250), "borde_tablero": (200, 180, 200),
        "texto_general": (80, 60, 80), "boton_resolver": (180, 230, 180),
        "boton_reiniciar": (255, 180, 180), "boton_verificar": (180, 180, 230),
        "boton_navegacion": (190, 190, 220), "boton_hover": (220, 220, 220),
        "reina_cuerpo": (255, 120, 170), "reina_corona": (255, 180, 200)
    },
    "azul_tablero": { # Ejemplo de otra paleta
        "fondo": (30, 40, 50), "celda_clara": (180, 190, 200),
        "celda_oscura": (100, 110, 130), "borde_tablero": (220, 220, 220),
        "texto_general": (230, 230, 240), "boton_resolver": (80, 180, 80),
        "boton_reiniciar": (200, 80, 80), "boton_verificar": (80, 80, 200),
        "boton_navegacion": (100, 100, 150), "boton_hover": (130, 130, 130),
        "reina_cuerpo": (255, 215, 0), "reina_corona": (255, 255, 255) # Reina dorada/blanca
    }
}
PALETA_ACTUAL_NREINAS = "pastel_juego" # Cambia esto para probar
COLORES = PALETAS_COLOR_NREINAS[PALETA_ACTUAL_NREINAS]

# --- Elementos UI Juego ---
ANIMACION_CELDA_HOVER_FACTOR = 1.1
ANIMACION_CELDA_SUAVIDAD = 0.1
BORDE_GROSOR_CELDA = 2
BOTON_ANCHO_NORMAL = 120
BOTON_ANCHO_NAV = 150
BOTON_ALTO = 35
BOTON_BORDE_RADIO = 3
BOTON_BORDE_GROSOR = 2
BOTON_HOVER_INFLATE = 1 # Píxeles a inflar en hover

# ==============================================================================
# === IMPORTACIONES Y RUTAS ===
# ==============================================================================

SCRIPT_DIR_NREINAS = Path(__file__).resolve().parent
RUTA_FUENTE_NREINAS_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_NREINAS:
    # --- CORRECCIÓN AQUÍ: Quitar .parent ---
    RUTA_FUENTE_NREINAS_COMPLETA = SCRIPT_DIR_NREINAS / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_NREINAS
    # --- FIN CORRECCIÓN ---
    # --- DEBUG PRINT (Temporal) ---
    print(f"[DEBUG NReinas] SCRIPT_DIR: {SCRIPT_DIR_NREINAS}")
    print(f"[DEBUG NReinas] RUTA FUENTE CALCULADA: {RUTA_FUENTE_NREINAS_COMPLETA}")
    print(f"[DEBUG NReinas] EXISTE LA RUTA?: {os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA)}")
    # --- FIN DEBUG PRINT ---


from cliente.juegos.n_reinas import NReinas
from cliente.comunicacion.cliente_network import get_network_client

# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (NReinas) ===
# ==============================================================================

class NReinasGUI:
    # === Inicialización ===
    def __init__(self, tamaño=8, ancho=VENTANA_ANCHO_NREINAS, alto=VENTANA_ALTO_NREINAS):
        pygame.init() # Re-inicializar Pygame
        self.tamaño = tamaño
        self.juego = NReinas(tamaño)
        self.network_client = get_network_client()
        self.intentos_nreinas = 0

        # --- Ventana ---
        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Problema de las {tamaño} Reinas")

        # --- Asignar Colores ---
        self._asignar_colores()

        # --- Cargar Fuentes ---
        self._cargar_fuentes()

        # --- Cálculo de Dimensiones UI ---
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y) // self.tamaño

        # --- Estado del Juego ---
        self.modo = "jugar"
        self.solucion_actual_idx = 0
        self.celda_hover = None
        self.boton_hover_texto = None
        self.hover_scale_anim = 1.0
        self.target_scale_anim = 1.0

    def _asignar_colores(self):
        """Asigna los colores de la paleta actual a los atributos de la instancia."""
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

    def _cargar_fuentes(self):
        """Carga las fuentes definidas en la configuración."""
        try:
            if RUTA_FUENTE_NREINAS_COMPLETA and os.path.exists(RUTA_FUENTE_NREINAS_COMPLETA):
                self.fuente_botones = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(RUTA_FUENTE_NREINAS_COMPLETA, TAMANO_FUENTE_INFO_NREINAS)
            elif NOMBRE_FUENTE_JUEGO_NREINAS:
                raise pygame.error(f"Fuente {NOMBRE_FUENTE_JUEGO_NREINAS} no encontrada.")
            else:
                self.fuente_botones = pygame.font.Font(None, TAMANO_FUENTE_BOTONES_NREINAS)
                self.fuente_info = pygame.font.Font(None, TAMANO_FUENTE_INFO_NREINAS)
        except Exception as e:
            print(f"Error cargando fuente para NReinas ({e}). Usando SysFont.")
            self.fuente_botones = pygame.font.SysFont('Arial', TAMANO_FUENTE_BOTONES_NREINAS)
            self.fuente_info = pygame.font.SysFont('Arial', TAMANO_FUENTE_INFO_NREINAS)

    # === Lógica de Dibujado ===
    def dibujar_gui_completa(self):
        """Dibuja todos los elementos de la GUI."""
        self.ventana.fill(self.color_fondo)
        self._dibujar_tablero()
        self._dibujar_botones()
        pygame.display.flip()

    def _dibujar_tablero(self):
        """Dibuja el tablero de ajedrez y las reinas."""
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
                    # Centrar el rect inflado sobre el original
                    rect_draw.center = rect_base.center
                    # Aclarar/oscurecer color en hover
                    color_draw = tuple(max(0, min(255, c + 20)) for c in color_base)

                pygame.draw.rect(self.ventana, color_draw, rect_draw)

                if self.juego.tablero[fila][col] == 1:
                    self._dibujar_reina(rect_base.centerx, rect_base.centery, current_scale)

                pygame.draw.rect(self.ventana, self.color_borde_tablero, rect_draw, BORDE_GROSOR_CELDA)

    def _dibujar_reina(self, centro_x, centro_y, scale=1.0):
        """Dibuja una reina en las coordenadas dadas con la escala aplicada."""
        radio_base = min(self.celda_ancho, self.celda_alto) // 3
        radio_scaled = int(radio_base * scale)
        if radio_scaled < 1: radio_scaled = 1 # Evitar radio 0

        # Cuerpo
        pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (centro_x, centro_y), radio_scaled)
        # Corona
        corona_radius = int(radio_scaled * 0.6)
        if corona_radius < 1: corona_radius = 1
        pygame.draw.circle(self.ventana, self.color_reina_corona, (centro_x, centro_y), corona_radius)
        # Picos de la corona
        pico_radius = int(radio_scaled * 0.15)
        if pico_radius < 1: pico_radius = 1
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            crown_x = centro_x + int(radio_scaled * 0.8 * math.cos(angle))
            crown_y = centro_y + int(radio_scaled * 0.8 * math.sin(angle))
            pygame.draw.circle(self.ventana, self.color_reina_cuerpo, (crown_x, crown_y), pico_radius)

    def _dibujar_botones(self):
        """Dibuja los botones de acción/navegación."""
        y_botones = self.alto - 45 # Posición Y de la fila de botones
        botones_info_jugar = [
            {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "color": self.color_boton_resolver, "texto": "Resolver"},
            {"rect": pygame.Rect(140, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "color": self.color_boton_reiniciar, "texto": "Reiniciar"},
            {"rect": pygame.Rect(270, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "color": self.color_boton_verificar, "texto": "Verificar"}
        ]
        botones_info_ver_sol = [
            {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NAV, BOTON_ALTO), "color": self.color_boton_navegacion, "texto": "Anterior"},
            {"rect": pygame.Rect(170, y_botones, BOTON_ANCHO_NAV, BOTON_ALTO), "color": self.color_boton_navegacion, "texto": "Siguiente"},
            {"rect": pygame.Rect(330, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "color": self.color_boton_reiniciar, "texto": "Volver"}
        ]
        
        botones_actuales_info = botones_info_jugar if self.modo == "jugar" else botones_info_ver_sol

        if self.modo == "ver_soluciones" and hasattr(self.juego, 'soluciones') and self.juego.soluciones:
            texto_sol_render = self.fuente_info.render(f"Solución {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", True, self.color_texto)
            self.ventana.blit(texto_sol_render, (460, y_botones + (BOTON_ALTO // 2 - texto_sol_render.get_height() // 2)))

        self.boton_hover_texto = None
        mouse_pos = pygame.mouse.get_pos()

        for boton_data in botones_actuales_info:
            hover = boton_data["rect"].collidepoint(mouse_pos)
            color_draw = boton_data["color"]
            rect_draw = boton_data["rect"]

            if hover:
                self.boton_hover_texto = boton_data["texto"]
                color_draw = self.color_boton_hover
                rect_draw = rect_draw.inflate(BOTON_HOVER_INFLATE * 2, BOTON_HOVER_INFLATE * 2)

            pygame.draw.rect(self.ventana, color_draw, rect_draw, border_radius=BOTON_BORDE_RADIO)
            # Borde más oscuro
            border_color_darker = tuple(max(0, c - 30) for c in color_draw)
            pygame.draw.rect(self.ventana, border_color_darker, rect_draw, BOTON_BORDE_GROSOR, border_radius=BOTON_BORDE_RADIO)

            texto_render = self.fuente_botones.render(boton_data["texto"], True, self.color_texto)
            self.ventana.blit(texto_render, texto_render.get_rect(center=rect_draw.center))


    # === Lógica de Comunicación con Servidor ===
    def _guardar_resultado_nreinas(self, exito: bool):
        """Envía el resultado al servidor."""
        print(f"[NReinasGUI] Guardando: N={self.tamaño}, Éxito={exito}, Intentos={self.intentos_nreinas}")
        def callback_guardado(response):
            status = "Ok" if response and response.get("status") == "ok" else "Error"
            msg = response.get('message', 'N/A') if response else "Sin respuesta"
            print(f"[NReinasGUI] Guardado: {status} - {msg}")

        self.network_client.save_n_reinas_score(
            n_value=self.tamaño, success=exito, attempts=self.intentos_nreinas, callback=callback_guardado
        )

    # === Manejo de Eventos ===
    def manejar_eventos(self):
        """Procesa eventos de Pygame. Retorna False para salir."""
        mouse_pos = pygame.mouse.get_pos()
        # --- Actualizar hover de celda ---
        nuevo_hover_celda = None
        if mouse_pos[1] < self.alto - ESPACIO_BOTONES_Y:
            col = mouse_pos[0] // self.celda_ancho
            fila = mouse_pos[1] // self.celda_alto
            if 0 <= fila < self.tamaño and 0 <= col < self.tamaño:
                nuevo_hover_celda = (fila, col)
        if nuevo_hover_celda != self.celda_hover:
            self.celda_hover = nuevo_hover_celda
            self.target_scale_anim = ANIMACION_CELDA_HOVER_FACTOR if nuevo_hover_celda else 1.0

        # --- Procesar cola de eventos ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1: # Clic izquierdo
                if self._manejar_clic(evento.pos):
                    return True # Indica que se manejó una acción

        return True

    def _manejar_clic(self, pos_clic):
        """Maneja un clic del ratón en el tablero o los botones."""
        x_click, y_click = pos_clic

        # --- Clic en Tablero ---
        if self.modo == "jugar" and y_click < self.alto - ESPACIO_BOTONES_Y:
            col_click = x_click // self.celda_ancho
            fila_click = y_click // self.celda_alto
            if 0 <= fila_click < self.tamaño and 0 <= col_click < self.tamaño:
                self.juego.tablero[fila_click][col_click] = 1 - self.juego.tablero[fila_click][col_click] # Toggle
                return True

        # --- Clic en Botones ---
        elif y_click >= self.alto - ESPACIO_BOTONES_Y:
            y_botones = self.alto - 45 # Recalcular Y base de botones
            botones_jugar_defs = [
                {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "accion": "resolver"},
                {"rect": pygame.Rect(140, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "accion": "reiniciar"},
                {"rect": pygame.Rect(270, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "accion": "verificar"}
            ]
            botones_ver_sol_defs = [
                {"rect": pygame.Rect(10, y_botones, BOTON_ANCHO_NAV, BOTON_ALTO), "accion": "anterior"},
                {"rect": pygame.Rect(170, y_botones, BOTON_ANCHO_NAV, BOTON_ALTO), "accion": "siguiente"},
                {"rect": pygame.Rect(330, y_botones, BOTON_ANCHO_NORMAL, BOTON_ALTO), "accion": "volver"}
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
                self.modo = "jugar" # Asegurar modo jugar al reiniciar
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


    # === Bucle Principal ===
    def ejecutar(self):
        """Inicia y mantiene el bucle principal del juego NReinas."""
        print(f"[NReinasGUI] Iniciando juego para N={self.tamaño}...")
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break

            self.dibujar_gui_completa()
            reloj.tick(FPS_NREINAS)

        print("[NReinasGUI] Saliendo del juego N Reinas.")
        # No hacemos pygame.quit() aquí, se maneja al volver al menú o al cerrar la app.

# ==============================================================================
# === Bloque de Ejecución Directa (para pruebas) ===
# ==============================================================================
if __name__ == "__main__":
    print("Ejecutando NReinasGUI directamente para pruebas...")
    # Asegurar que el directorio raíz está en sys.path
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))
    print(f"DEBUG: Project root {PROJECT_ROOT_TEST} in sys.path.")

    # Para probar la comunicación, el servidor debe estar corriendo
    juego_gui_nreinas = NReinasGUI(tamaño=8)
    juego_gui_nreinas.ejecutar()

    pygame.quit() # Limpiar Pygame al salir de la prueba directa
    sys.exit()