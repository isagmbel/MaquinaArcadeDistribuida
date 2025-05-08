import pygame
import sys
import time
from pathlib import Path # Para pruebas directas en __main__

# --- MODIFICACIONES ---
from cliente.juegos.torres_hanoi import TorresHanoi
from cliente.comunicacion.cliente_network import get_network_client
# --- FIN MODIFICACIONES ---

class TorresHanoiGUI:
    def __init__(self, discos=3, ancho=800, alto=600):
        pygame.init() # Necesario
        self.discos = discos
        self.juego = TorresHanoi(discos)
        
        # --- MODIFICACIONES ---
        self.network_client = get_network_client()
        self.resultado_hanoi_guardado = False # Flag para evitar guardados múltiples
        # --- FIN MODIFICACIONES ---

        self.ancho = ancho
        self.alto = alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Torres de Hanoi")
        
        self.FONDO = (250, 240, 245)
        self.BASE_COLOR = (210, 180, 140) # Renombrado para claridad
        self.POSTE_COLOR = (200, 170, 130) # Renombrado
        self.COLORES_DISCOS = [ # Renombrado
            (255, 182, 193), (180, 230, 180), (180, 180, 230),
            (255, 255, 180), (230, 180, 230), (180, 230, 230),
            (255, 200, 180), (220, 200, 220)
        ]
        self.TEXTO_COLOR = (100, 80, 100) # Renombrado
        self.BOTON_COLOR = (200, 200, 220) # Renombrado
        self.BOTON_HOVER_COLOR = (220, 220, 240) # Renombrado
        
        self.base_altura = 20
        self.poste_ancho = 20
        self.poste_altura = 300
        self.disco_altura_unidad = 30 # Renombrado
        self.disco_ancho_max = 150 # Renombrado
        self.disco_reduccion_ancho = 20 # Renombrado
        
        self.torre_pos_x_coords = [ancho//4, ancho//2, 3*ancho//4] # Renombrado
        self.base_y_coord = alto - 50 # Renombrado
        
        self.fuente_normal = pygame.font.SysFont('Arial', 24) # Renombrado
        self.fuente_grande = pygame.font.SysFont('Arial', 36, bold=True) # Renombrado
        
        self.disco_seleccionado_val = None # Renombrado para claridad (valor del disco)
        self.torre_origen_idx = None # Renombrado
        self.resolviendo_auto = False # Renombrado
        self.pasos_solucion_auto = [] # Renombrado
        self.paso_actual_auto = 0 # Renombrado
        self.hover_torre_idx = None # Renombrado
        self.hover_boton_texto = None # Renombrado
    
    def dibujar_torres(self):
        pygame.draw.rect(self.ventana, self.BASE_COLOR, 
                        (50, self.base_y_coord, self.ancho-100, self.base_altura))
        
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            color_poste = self.POSTE_COLOR
            if self.hover_torre_idx == i:
                color_poste = (min(self.POSTE_COLOR[0] + 20, 255), 
                               min(self.POSTE_COLOR[1] + 20, 255), 
                               min(self.POSTE_COLOR[2] + 20, 255))
            pygame.draw.rect(self.ventana, color_poste, 
                            (x_coord - self.poste_ancho//2, self.base_y_coord - self.poste_altura, 
                             self.poste_ancho, self.poste_altura))
        
        for torre_idx, torre_discos in enumerate(self.juego.torres):
            for disco_idx_en_torre, valor_disco in enumerate(torre_discos):
                ancho_disco = self.disco_ancho_max - (self.disco_reduccion_ancho * (self.discos - valor_disco))
                x_disco = self.torre_pos_x_coords[torre_idx] - ancho_disco // 2
                y_disco = self.base_y_coord - self.base_altura - (disco_idx_en_torre + 1) * self.disco_altura_unidad
                
                color_idx_disco = (valor_disco - 1) % len(self.COLORES_DISCOS)
                color_disco_base = self.COLORES_DISCOS[color_idx_disco]
                
                rect_disco = pygame.Rect(x_disco, y_disco, ancho_disco, self.disco_altura_unidad)
                color_disco_draw = color_disco_base

                if self.torre_origen_idx == torre_idx and disco_idx_en_torre == len(torre_discos) - 1: # Disco superior de torre origen
                    color_disco_draw = (min(color_disco_base[0] + 30, 255),
                                        min(color_disco_base[1] + 30, 255),
                                        min(color_disco_base[2] + 30, 255))
                    # Dibujar un "aura" o borde más grueso para el disco seleccionado
                    pygame.draw.rect(self.ventana, color_disco_draw, rect_disco.inflate(6,6), border_radius=3)

                pygame.draw.rect(self.ventana, color_disco_base, rect_disco, border_radius=3) # Disco principal
                pygame.draw.rect(self.ventana, self.TEXTO_COLOR, rect_disco, 2, border_radius=3) # Borde del disco
    
    def dibujar_ui(self):
        movimientos_texto = self.fuente_normal.render(
            f"Movimientos: {self.juego.movimientos} (Mínimo: {self.juego.solucion_minima})", 
            True, self.TEXTO_COLOR)
        self.ventana.blit(movimientos_texto, (20, 20))
        
        if self.juego.esta_resuelto() and not self.resultado_hanoi_guardado: # --- MODIFICADO ---
            self._guardar_resultado_hanoi(exito=True) # --- MODIFICADO ---
        
        if self.juego.esta_resuelto():
            felicitacion = self.fuente_grande.render("¡Resuelto!", True, (100, 180, 100))
            self.ventana.blit(felicitacion, 
                            (self.ancho//2 - felicitacion.get_width()//2, 50))
        
        botones_info = [
            {"texto": "Reiniciar", "pos": (self.ancho - 220, 20), "accion": self.accion_reiniciar},
            {"texto": "Resolver", "pos": (self.ancho - 220, 60), "accion": self.accion_resolver_auto},
            {"texto": "Deshacer", "pos": (self.ancho - 220, 100), "accion": self.juego.deshacer_ultimo_movimiento}
        ]
        
        self.hover_boton_texto = None
        mouse_pos = pygame.mouse.get_pos()
        
        for boton_data in botones_info:
            x_b, y_b = boton_data["pos"]
            rect_b = pygame.Rect(x_b, y_b, 150, 30)
            hover_b = rect_b.collidepoint(mouse_pos)
            
            color_b_draw = self.BOTON_COLOR
            if hover_b:
                self.hover_boton_texto = boton_data["texto"]
                color_b_draw = self.BOTON_HOVER_COLOR
            
            pygame.draw.rect(self.ventana, color_b_draw, rect_b, border_radius=5)
            pygame.draw.rect(self.ventana, self.TEXTO_COLOR, rect_b, 2, border_radius=5)
            
            texto_b = self.fuente_normal.render(boton_data["texto"], True, self.TEXTO_COLOR)
            self.ventana.blit(texto_b, (rect_b.centerx - texto_b.get_width()//2, 
                                      rect_b.centery - texto_b.get_height()//2))

    # --- MODIFICACIONES ---
    def _guardar_resultado_hanoi(self, exito: bool):
        if self.resultado_hanoi_guardado and exito: # Solo guardar una vez por resolución exitosa
            print("[TorresHanoiGUI] Resultado exitoso ya guardado.")
            return
        
        # Si se llama con exito=False, podría ser un guardado por abandono, pero el requisito
        # parece implicar guardado al final de una partida (exitosa o no).
        # Por ahora, solo guardaremos explícitamente las partidas resueltas.

        print(f"[TorresHanoiGUI] Guardando: Discos={self.discos}, Movimientos={self.juego.movimientos}, Éxito={exito}")

        def callback_guardado(response):
            if response and response.get("status") == "ok":
                print(f"[TorresHanoiGUI] Puntuación guardada: {response.get('message')}")
            else:
                msg = response.get('message') if response else "Error desconocido"
                print(f"[TorresHanoiGUI] Error al guardar puntuación: {msg}")
        
        self.network_client.save_torres_hanoi_score(
            num_disks=self.discos,
            moves_made=self.juego.movimientos,
            success=exito,
            callback=callback_guardado
        )
        if exito:
            self.resultado_hanoi_guardado = True
    
    def accion_reiniciar(self):
        self.juego.reiniciar()
        self.resolviendo_auto = False
        self.resultado_hanoi_guardado = False # Permitir nuevo guardado si se resuelve
        self.torre_origen_idx = None
        self.disco_seleccionado_val = None

    def accion_resolver_auto(self):
        if not self.resolviendo_auto:
            self.accion_reiniciar() # Reinicia el estado y el flag de guardado
            self.resolviendo_auto = True
            self.pasos_solucion_auto = []
            self._generar_solucion_hanoi(self.discos, 0, 2, 1) # Origen 0, Destino 2, Auxiliar 1
            self.paso_actual_auto = 0
    # --- FIN MODIFICACIONES ---

    def _generar_solucion_hanoi(self, n_discos_mover, origen_idx, destino_idx, aux_idx):
        if n_discos_mover == 0:
            return
        self._generar_solucion_hanoi(n_discos_mover - 1, origen_idx, aux_idx, destino_idx)
        self.pasos_solucion_auto.append((origen_idx, destino_idx))
        self._generar_solucion_hanoi(n_discos_mover - 1, aux_idx, destino_idx, origen_idx)
    
    def manejar_eventos(self):
        mouse_pos = pygame.mouse.get_pos()
        
        self.hover_torre_idx = None
        for i, x_coord in enumerate(self.torre_pos_x_coords):
            # Ampliar área de detección para torres
            torre_rect_detect = pygame.Rect(x_coord - self.disco_ancho_max//2, 
                                            self.base_y_coord - self.poste_altura,
                                            self.disco_ancho_max, self.poste_altura)
            if torre_rect_detect.collidepoint(mouse_pos):
                self.hover_torre_idx = i
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False # Para salir del bucle ejecutar
            
            if evento.type == pygame.MOUSEBUTTONDOWN and not self.resolviendo_auto:
                botones_info = [
                    {"rect": pygame.Rect(self.ancho - 220, 20, 150, 30), "accion_obj": self.accion_reiniciar},
                    {"rect": pygame.Rect(self.ancho - 220, 60, 150, 30), "accion_obj": self.accion_resolver_auto},
                    {"rect": pygame.Rect(self.ancho - 220, 100, 150, 30), "accion_obj": self.juego.deshacer_ultimo_movimiento}
                ]
                
                for boton_data in botones_info:
                    if boton_data["rect"].collidepoint(mouse_pos):
                        boton_data["accion_obj"]()
                        return True # Evento manejado
                
                if self.hover_torre_idx is not None:
                    if self.torre_origen_idx is None: # Intentando tomar un disco
                        if self.juego.torres[self.hover_torre_idx]: # Si la torre no está vacía
                            self.torre_origen_idx = self.hover_torre_idx
                            self.disco_seleccionado_val = self.juego.torres[self.hover_torre_idx][-1]
                    else: # Intentando colocar un disco
                        if self.juego.mover_disco(self.torre_origen_idx, self.hover_torre_idx):
                            # El chequeo de si está resuelto y el guardado se hace en dibujar_ui
                            pass
                        # Siempre deseleccionar después de intentar colocar
                        self.torre_origen_idx = None
                        self.disco_seleccionado_val = None
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r: self.accion_reiniciar()
                elif evento.key == pygame.K_s: self.accion_resolver_auto()
                elif evento.key == pygame.K_u: self.juego.deshacer_ultimo_movimiento()
        return True # Seguir ejecutando
    
    def actualizar_resolucion_automatica(self):
        if self.resolviendo_auto and self.paso_actual_auto < len(self.pasos_solucion_auto):
            origen_idx, destino_idx = self.pasos_solucion_auto[self.paso_actual_auto]
            self.juego.mover_disco(origen_idx, destino_idx) # Mover_disco actualiza self.juego.movimientos
            self.paso_actual_auto += 1
            # El chequeo de si está resuelto y guardado se hace en dibujar_ui
            # Forzar un pequeño delay para la visualización
            pygame.time.delay(300) # 300 ms de pausa
        elif self.resolviendo_auto and self.paso_actual_auto >= len(self.pasos_solucion_auto):
            self.resolviendo_auto = False # Terminó la resolución automática
            # El estado resuelto se detectará y guardará en el próximo frame de dibujar_ui
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            
            if self.resolviendo_auto:
                self.actualizar_resolucion_automatica()
            
            self.ventana.fill(self.FONDO)
            self.dibujar_torres()
            self.dibujar_ui()
            pygame.display.flip()
            reloj.tick(30) # FPS más bajo puede ser mejor para este juego
        print("[TorresHanoiGUI] Saliendo del juego.")

if __name__ == "__main__":
    PROJECT_ROOT_TEST = Path(__file__).resolve().parents[2] 
    sys.path.append(str(PROJECT_ROOT_TEST))

    juego_gui = TorresHanoiGUI(discos=4) # Probar con 4 discos
    juego_gui.ejecutar()
    pygame.quit()
    sys.exit()