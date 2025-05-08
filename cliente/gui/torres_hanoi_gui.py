import pygame
import sys
import time # Sigue siendo necesario para la pausa en resolución automática
import os # Para os.path.exists en la carga de fuentes
from pathlib import Path

# MODIFICACIONES: CONFIGURACIÓN DE APARIENCIA
# Fuentes
NOMBRE_FUENTE_JUEGO_HANOI = "nokiafc22.ttf" # O "04B_03_.TTF", o None
TAMANO_FUENTE_INFO_HANOI = 20
TAMANO_FUENTE_BOTONES_HANOI = 18
TAMANO_FUENTE_TITULO_HANOI = 30 # Para el "¡Resuelto!"

# Colores 
PALETAS_COLOR_HANOI = {
    "pastel_juego": {
        "fondo": (240, 245, 250), # Un azul muy pálido
        "base_torre": (200, 190, 170), # Beige
        "poste_torre": (180, 170, 150),
        "discos": [ # Mantener variedad de colores para discos
            (255, 182, 193), (173, 216, 230), (144, 238, 144),
            (255, 255, 153), (221, 160, 221), (175, 238, 238),
            (255, 218, 185), (211, 211, 211) 
        ],
        "texto_info": (70, 70, 90),    # Azul oscuro/gris
        "texto_botones": (60, 60, 80),
        "boton_normal": (200, 200, 220),
        "boton_hover": (220, 220, 240),
        "texto_resuelto": (80, 160, 80) # Verde para "¡Resuelto!"
    }
}
PALETA_ACTUAL_HANOI = "pastel_juego"
COLORES_HANOI = PALETAS_COLOR_HANOI[PALETA_ACTUAL_HANOI]
# CONFIGURACIÓN DE APARIENCIA

# RUTAS Y CLIENTE DE RED
SCRIPT_DIR_HANOI = Path(__file__).resolve().parent
RUTA_FUENTE_HANOI_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_HANOI:
    RUTA_FUENTE_HANOI_COMPLETA = SCRIPT_DIR_HANOI / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_HANOI

from cliente.juegos.torres_hanoi import TorresHanoi
from cliente.comunicacion.cliente_network import get_network_client
# 

class TorresHanoiGUI:
    def __init__(self, discos=3, ancho=800, alto=600):
        pygame.init()
        self.discos = discos
        self.juego = TorresHanoi(discos)
        
        self.network_client = get_network_client()
        self.resultado_hanoi_guardado = False

        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Torres de Hanoi")
        
        # --- MODIFICACIONES: ASIGNAR COLORES Y FUENTES ---
        self.FONDO = COLORES_HANOI["fondo"]
        self.BASE_COLOR = COLORES_HANOI["base_torre"]
        self.POSTE_COLOR = COLORES_HANOI["poste_torre"]
        self.COLORES_DISCOS = COLORES_HANOI["discos"]
        self.TEXTO_INFO_COLOR = COLORES_HANOI["texto_info"]
        self.TEXTO_BOTONES_COLOR = COLORES_HANOI["texto_botones"]
        self.BOTON_NORMAL_COLOR = COLORES_HANOI["boton_normal"]
        self.BOTON_HOVER_COLOR = COLORES_HANOI["boton_hover"]
        self.TEXTO_RESUELTO_COLOR = COLORES_HANOI["texto_resuelto"]

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
        # --- FIN MODIFICACIONES ---
        
        self.base_altura = 20
        self.poste_ancho = 15 # Más delgado
        self.poste_altura = 250 # Un poco más bajo
        self.disco_altura_unidad = 25 # Más delgados
        self.disco_ancho_max = 140 
        self.disco_reduccion_ancho = 18
        
        self.torre_pos_x_coords = [ancho//4, ancho//2, 3*ancho//4]
        self.base_y_coord = alto - 60 # Más espacio abajo
        
        self.disco_seleccionado_val = None
        self.torre_origen_idx = None
        self.resolviendo_auto = False
        self.pasos_solucion_auto = []
        self.paso_actual_auto = 0
        self.hover_torre_idx = None
        self.hover_boton_texto = None
    
    def dibujar_torres(self):
        pygame.draw.rect(self.ventana, self.BASE_COLOR, 
                        (self.ancho*0.1, self.base_y_coord, self.ancho*0.8, self.base_altura), border_radius=3)
        
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            color_poste = self.POSTE_COLOR
            if self.hover_torre_idx == i:
                color_poste = tuple(max(0, c + 15) for c in self.POSTE_COLOR)
            pygame.draw.rect(self.ventana, color_poste, 
                            (x_coord - self.poste_ancho//2, self.base_y_coord - self.poste_altura, 
                             self.poste_ancho, self.poste_altura), border_top_left_radius=5, border_top_right_radius=5)
        
        for torre_idx, torre_discos in enumerate(self.juego.torres):
            for disco_idx_en_torre, valor_disco in enumerate(torre_discos):
                ancho_disco = self.disco_ancho_max - (self.disco_reduccion_ancho * (self.discos - valor_disco))
                x_disco = self.torre_pos_x_coords[torre_idx] - ancho_disco // 2
                y_disco = self.base_y_coord - self.base_altura - (disco_idx_en_torre + 1) * self.disco_altura_unidad
                
                color_idx_disco = (valor_disco - 1) % len(self.COLORES_DISCOS)
                color_disco_base = self.COLORES_DISCOS[color_idx_disco]
                
                rect_disco = pygame.Rect(x_disco, y_disco, ancho_disco, self.disco_altura_unidad)
                
                if self.torre_origen_idx == torre_idx and disco_idx_en_torre == len(torre_discos) - 1:
                    pygame.draw.rect(self.ventana, tuple(max(0,c-30) for c in color_disco_base), rect_disco.inflate(6,6), border_radius=3)

                pygame.draw.rect(self.ventana, color_disco_base, rect_disco, border_radius=3)
                pygame.draw.rect(self.ventana, tuple(max(0,c-50) for c in color_disco_base), rect_disco, 2, border_radius=3)
    
    def dibujar_ui(self):
        movimientos_texto = self.fuente_info.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})", 
            True, self.TEXTO_INFO_COLOR)
        self.ventana.blit(movimientos_texto, (20, 20))
        
        if self.juego.esta_resuelto():
            if not self.resultado_hanoi_guardado:
                self._guardar_resultado_hanoi(exito=True)
            felicitacion = self.fuente_titulo_juego.render("¡Resuelto!", True, self.TEXTO_RESUELTO_COLOR)
            self.ventana.blit(felicitacion, 
                            (self.ancho//2 - felicitacion.get_width()//2, self.alto // 2 - 150)) # Más centrado
        
        botones_info = [
            {"texto": "Reiniciar", "pos": (self.ancho - 170, 30), "ancho": 150, "accion": self.accion_reiniciar},
            {"texto": "Resolver", "pos": (self.ancho - 170, 70), "ancho": 150, "accion": self.accion_resolver_auto},
            {"texto": "Deshacer", "pos": (self.ancho - 170, 110), "ancho": 150, "accion": self.accion_deshacer_wrapper}
        ]
        
        self.hover_boton_texto = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_info:
            x_b, y_b = boton_data["pos"]
            rect_b = pygame.Rect(x_b, y_b, boton_data["ancho"], 35) # Botones un poco más altos
            hover_b = rect_b.collidepoint(mouse_pos)
            
            color_b_draw = self.BOTON_NORMAL_COLOR
            if hover_b:
                self.hover_boton_texto = boton_data["texto"]
                color_b_draw = self.BOTON_HOVER_COLOR
            
            pygame.draw.rect(self.ventana, color_b_draw, rect_b, border_radius=5)
            pygame.draw.rect(self.ventana, tuple(max(0,c-30) for c in color_b_draw), rect_b, 2, border_radius=5)
            
            texto_b = self.fuente_botones.render(boton_data["texto"], True, self.TEXTO_BOTONES_COLOR)
            self.ventana.blit(texto_b, (rect_b.centerx - texto_b.get_width()//2, 
                                      rect_b.centery - texto_b.get_height()//2))

    def accion_deshacer_wrapper(self): # Wrapper para resetear flag de guardado
        self.juego.deshacer_ultimo_movimiento()
        self.resultado_hanoi_guardado = False # Si deshace, ya no está resuelto para guardado

    def _guardar_resultado_hanoi(self, exito: bool):
        if self.resultado_hanoi_guardado and exito:
            return
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
        self.resolviendo_auto = False
        self.resultado_hanoi_guardado = False
        self.torre_origen_idx = None
        self.disco_seleccionado_val = None

    def accion_resolver_auto(self):
        if not self.resolviendo_auto:
            self.accion_reiniciar()
            self.resolviendo_auto = True
            self.pasos_solucion_auto = []
            self._generar_solucion_hanoi(self.discos, 0, 2, 1)
            self.paso_actual_auto = 0

    def _generar_solucion_hanoi(self, n_discos, origen, destino, aux):
        if n_discos == 0: return
        self._generar_solucion_hanoi(n_discos - 1, origen, aux, destino)
        self.pasos_solucion_auto.append((origen, destino))
        self._generar_solucion_hanoi(n_discos - 1, aux, destino, origen)
    
    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        
        self.hover_torre_idx = None
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            torre_rect_detect = pygame.Rect(x_coord - self.disco_ancho_max//1.5, # Área de detección más ancha
                                            self.base_y_coord - self.poste_altura - self.disco_altura_unidad * self.discos, # Desde arriba de la torre
                                            self.disco_ancho_max*1.33, self.poste_altura + self.disco_altura_unidad * self.discos)
            if torre_rect_detect.collidepoint(mouse_pos):
                self.hover_torre_idx = i
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: return False
            
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and not self.resolviendo_auto:
                botones_info = [
                    {"rect": pygame.Rect(self.ancho - 170, 30, 150, 35), "accion_obj": self.accion_reiniciar},
                    {"rect": pygame.Rect(self.ancho - 170, 70, 150, 35), "accion_obj": self.accion_resolver_auto},
                    {"rect": pygame.Rect(self.ancho - 170, 110, 150, 35), "accion_obj": self.accion_deshacer_wrapper}
                ]
                
                for boton_data in botones_info:
                    if boton_data["rect"].collidepoint(mouse_pos):
                        boton_data["accion_obj"]()
                        return True
                
                if self.hover_torre_idx is not None:
                    if self.torre_origen_idx is None:
                        if self.juego.torres[self.hover_torre_idx]:
                            self.torre_origen_idx = self.hover_torre_idx
                            self.disco_seleccionado_val = self.juego.torres[self.hover_torre_idx][-1]
                    else:
                        self.juego.mover_disco(self.torre_origen_idx, self.hover_torre_idx)
                        self.resultado_hanoi_guardado = False # Movimiento manual, resetear flag
                        self.torre_origen_idx = None
                        self.disco_seleccionado_val = None
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r: self.accion_reiniciar()
                elif evento.key == pygame.K_s: self.accion_resolver_auto()
                elif evento.key == pygame.K_u: self.accion_deshacer_wrapper()
        return True
    
    def actualizar_resolucion_automatica(self):
        if self.resolviendo_auto and self.paso_actual_auto < len(self.pasos_solucion_auto):
            origen_idx, destino_idx = self.pasos_solucion_auto[self.paso_actual_auto]
            self.juego.mover_disco(origen_idx, destino_idx)
            self.paso_actual_auto += 1
            pygame.time.delay(400) # Pausa para ver
        elif self.resolviendo_auto and self.paso_actual_auto >= len(self.pasos_solucion_auto):
            self.resolviendo_auto = False
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break
            
            if self.resolviendo_auto:
                self.actualizar_resolucion_automatica()
            
            self.ventana.fill(self.FONDO)
            self.dibujar_torres()
            self.dibujar_ui()
            pygame.display.flip()
            reloj.tick(30)
        print("[TorresHanoiGUI] Saliendo del juego Torres de Hanoi.")

if __name__ == "__main__":
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT_TEST) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT_TEST))

    juego_gui_hanoi = TorresHanoiGUI(discos=3)
    juego_gui_hanoi.ejecutar()
    pygame.quit()
    sys.exit()