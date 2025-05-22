import pygame
import sys
import os
from pathlib import Path
import time 

# ==============================================================================
# === CONFIGURACIÓN DE APARIENCIA Y JUEGO (RecorridoCaballo) ===
# ==============================================================================
VENTANA_ANCHO_CABALLO = 600
VENTANA_ALTO_CABALLO = 700 
FPS_CABALLO = 60
ESPACIO_BOTONES_Y_CABALLO = 50
ESPACIO_FEEDBACK_Y_CABALLO = 30 
NOMBRE_FUENTE_JUEGO_CABALLO = "nokiafc22.ttf"
TAMANO_FUENTE_NUMEROS_CABALLO = 20 
TAMANO_FUENTE_BOTONES_CABALLO = 15 # Reducido para 6 botones
TAMANO_FUENTE_INFO_CABALLO = 16
TAMANO_FUENTE_FEEDBACK_CABALLO = 18

PALETAS_COLOR_CABALLO = { # (Misma paleta que antes, asegúrate de tener "boton_navegacion")
    "pastel_juego": {
        "fondo": (245, 250, 240), "celda_clara": (255, 255, 255),
        "celda_oscura": (220, 240, 220), "borde_tablero": (180, 200, 180),
        "texto_numeros": (60, 80, 60), "texto_general": (70, 90, 70),
        "boton_resolver": (180, 230, 180), "boton_reiniciar": (255, 180, 180),
        "boton_verificar": (180, 180, 230), "boton_navegacion": (190, 190, 220), # Usado para Ayuda, Deshacer, Menú
        "boton_hover": (220, 220, 220),
        "sugerencia_ayuda": (0, 200, 0, 100), 
        "feedback_fondo": (220, 220, 220, 200) 
    },
    # ... (tu otra paleta) ...
}
PALETA_ACTUAL_CABALLO = "pastel_juego"
COLORES = PALETAS_COLOR_CABALLO[PALETA_ACTUAL_CABALLO]

ANIMACION_CELDA_HOVER_INFLATE = 4
BORDE_GROSOR_CELDA_CABALLO = 1
BOTON_ALTO_CABALLO = 35
BOTON_BORDE_RADIO_CABALLO = 3
BOTON_BORDE_GROSOR_CABALLO = 2
BOTON_HOVER_INFLATE_CABALLO = 1

# ==============================================================================
# === CLASE RecorridoCaballo (Lógica del Juego) ===
# ==============================================================================
class RecorridoCaballo: # (Misma clase que antes)
    def __init__(self, tamaño=8):
        self.tamaño = tamaño
        self.tablero = [[-1 for _ in range(tamaño)] for _ in range(tamaño)]
        self.movimientos_posibles_caballo = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
        self.soluciones = []
        self.tiempo_limite = 2.0
        self.max_soluciones_autoresolver = 10
    def es_valido(self, x, y): # Para el solver y ayuda
        return 0 <= x < self.tamaño and 0 <= y < self.tamaño and self.tablero[x][y] == -1
    def contar_salidas(self, x, y):
        c=0;_=[(c:=c+1) for dx,dy in self.movimientos_posibles_caballo if self.es_valido(x+dx,y+dy)];return c
    def resolver_recursivo(self, x,y,m,t_i):
        if time.time()-t_i > self.tiempo_limite or len(self.soluciones)>=self.max_soluciones_autoresolver: return True
        self.tablero[x][y]=m
        if m==self.tamaño*self.tamaño:
            self.soluciones.append([r[:] for r in self.tablero]);self.tablero[x][y]=-1
            return len(self.soluciones)>=self.max_soluciones_autoresolver
        movs=[(self.contar_salidas(x+dx,y+dy),x+dx,y+dy) for dx,dy in self.movimientos_posibles_caballo if self.es_valido(x+dx,y+dy)]
        movs.sort()
        for _,nx,ny in movs:
            if self.resolver_recursivo(nx,ny,m+1,t_i):
                if len(self.soluciones)>=self.max_soluciones_autoresolver: self.tablero[x][y]=-1; return True
        self.tablero[x][y]=-1; return False
    def encontrar_soluciones_autoresolver(self):
        self.soluciones = []; self.reiniciar_tablero(); t_i=time.time()
        orig_max=self.max_soluciones_autoresolver
        if self.tamaño>5: self.max_soluciones_autoresolver=1
        self.resolver_recursivo(0,0,1,t_i)
        if not self.soluciones and self.tamaño<=5:
            for r_s in range(min(self.tamaño//2+1,self.tamaño)):
                for c_s in range(min(self.tamaño//2+1,self.tamaño)):
                    if (r_s,c_s)==(0,0) or time.time()-t_i > self.tiempo_limite: continue
                    self.reiniciar_tablero(); self.resolver_recursivo(r_s,c_s,1,t_i)
                    if len(self.soluciones)>=self.max_soluciones_autoresolver: break
                if len(self.soluciones)>=self.max_soluciones_autoresolver or time.time()-t_i > self.tiempo_limite: break
        if self.tamaño>5: self.max_soluciones_autoresolver=orig_max
        return self.soluciones
    def reiniciar_tablero(self): self.tablero=[[-1 for _ in range(self.tamaño)] for _ in range(self.tamaño)]
    def mover_caballo_jugador(self,f,c,p,u_pos):
        if self.tablero[f][c]!=-1: return False,"Casilla ocupada."
        if p==1: self.tablero[f][c]=p; return True,""
        if u_pos is None: return False,"Error interno."
        ux,uy=u_pos; dx,dy=abs(f-ux),abs(c-uy)
        if(dx,dy)in[(1,2),(2,1)]: self.tablero[f][c]=p; return True,""
        return False,"Movimiento de caballo inválido."
    def es_solucion_valida_jugador(self):
        pasos,max_p,pos_p={},0,{}
        for r in range(self.tamaño):
            for c in range(self.tamaño):
                v=self.tablero[r][c]
                if v!=-1:
                    if v in pasos:return False
                    pasos.add(v);pos_p[v]=(r,c)
                    if v>max_p:max_p=v
        if any(i not in pasos for i in range(1,max_p+1)) or max_p!=self.tamaño*self.tamaño: return False
        for i in range(1,max_p):
            x1,y1=pos_p[i];x2,y2=pos_p[i+1];dx,dy=abs(x1-x2),abs(y1-y2)
            if(dx,dy)not in[(1,2),(2,1)]:return False
        return True

# ==============================================================================
# === IMPORTACIONES Y RUTAS (GUI) ===
# ==============================================================================
SCRIPT_DIR_CABALLO = Path(__file__).resolve().parent
RUTA_FUENTE_CABALLO_COMPLETA = None
if NOMBRE_FUENTE_JUEGO_CABALLO:
    RUTA_FUENTE_CABALLO_COMPLETA = SCRIPT_DIR_CABALLO / "assets" / "fonts" / NOMBRE_FUENTE_JUEGO_CABALLO
    if not os.path.exists(RUTA_FUENTE_CABALLO_COMPLETA) : print(f"[DEBUG Caballo] Fuente NO ENCONTRADA: {RUTA_FUENTE_CABALLO_COMPLETA}")

class MockNetworkClient: # (Misma clase que antes)
    def save_knights_tour_score(self, start_position, moves_made, completed, callback):
        print(f"[MockCliente Caballo] Enviado: {{'start_pos': {start_position}, 'moves': {moves_made}, 'completed': {completed}}}}}")
        response = {'status': 'ok', 'message': 'KnightsTour score saved (mock)'}
        if callback: callback(response)

def get_network_client(): # (Misma clase que antes)
    try:
        from cliente.comunicacion.cliente_network import get_network_client as real_get_network_client
        return real_get_network_client()
    except ImportError:
        print("[RecorridoCaballoGUI] Usando MockNetworkClient.")
        return MockNetworkClient()

# ==============================================================================
# === CLASE PRINCIPAL DE LA GUI (RecorridoCaballoGUI) ===
# ==============================================================================
class RecorridoCaballoGUI:
    def __init__(self, tamaño=8, ancho=VENTANA_ANCHO_CABALLO, alto=VENTANA_ALTO_CABALLO):
        pygame.init()
        self.tamaño = tamaño; self.juego = RecorridoCaballo(tamaño)
        self.network_client = get_network_client()
        self.ancho, self.alto = ancho, alto
        self.ventana = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption(f"Recorrido del Caballo {tamaño}x{tamaño}")
        self._asignar_colores(); self._cargar_fuentes()
        self.celda_ancho = self.ancho // self.tamaño
        self.celda_alto = (self.alto - ESPACIO_BOTONES_Y_CABALLO - ESPACIO_FEEDBACK_Y_CABALLO) // self.tamaño
        self.modo = "jugar"; self.solucion_actual_idx = 0
        self.paso_actual_manual = 1; self.ultima_pos_caballo_manual = None
        self.historial_movimientos = [] # (tablero_anterior, paso_anterior, ultima_pos_anterior, pos_inicial_anterior)
        self.posicion_inicial_registrada = None # (fila, col) del primer movimiento
        self.celda_hover, self.boton_hover_texto, self.celda_sugerida = None, None, None
        self.mensaje_feedback_texto, self.mensaje_feedback_tiempo_fin = "", 0
        self.duracion_feedback_ms = 3000
        self.resultado_guardado_este_intento = False
        self.accion_al_salir = None

    def _asignar_colores(self): # (Misma función que antes)
        self.color_fondo=COLORES["fondo"];self.color_celda_clara=COLORES["celda_clara"];self.color_celda_oscura=COLORES["celda_oscura"]
        self.color_borde_tablero=COLORES["borde_tablero"];self.color_texto_numeros=COLORES["texto_numeros"];self.color_texto_general=COLORES["texto_general"]
        self.color_boton_resolver=COLORES["boton_resolver"];self.color_boton_reiniciar=COLORES["boton_reiniciar"];self.color_boton_verificar=COLORES["boton_verificar"]
        self.color_boton_navegacion=COLORES["boton_navegacion"];self.color_boton_hover=COLORES["boton_hover"]
        self.color_sugerencia_ayuda=COLORES["sugerencia_ayuda"];self.color_feedback_fondo=COLORES["feedback_fondo"]

    def _cargar_fuentes(self): # (Misma función que antes)
        try:
            if RUTA_FUENTE_CABALLO_COMPLETA and os.path.exists(RUTA_FUENTE_CABALLO_COMPLETA):
                self.fuente_numeros=pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA,TAMANO_FUENTE_NUMEROS_CABALLO);self.fuente_botones=pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA,TAMANO_FUENTE_BOTONES_CABALLO)
                self.fuente_info=pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA,TAMANO_FUENTE_INFO_CABALLO);self.fuente_feedback=pygame.font.Font(RUTA_FUENTE_CABALLO_COMPLETA,TAMANO_FUENTE_FEEDBACK_CABALLO)
            else:
                if NOMBRE_FUENTE_JUEGO_CABALLO: print(f"Advertencia: Fuente {NOMBRE_FUENTE_JUEGO_CABALLO} no encontrada. Usando SysFont.")
                self.fuente_numeros,self.fuente_botones,self.fuente_info,self.fuente_feedback = [pygame.font.SysFont('Arial',s) for s in [TAMANO_FUENTE_NUMEROS_CABALLO,TAMANO_FUENTE_BOTONES_CABALLO,TAMANO_FUENTE_INFO_CABALLO,TAMANO_FUENTE_FEEDBACK_CABALLO]]
        except Exception as e:
            print(f"Error cargando fuente para RecorridoCaballo ({e}). Usando SysFont.")
            self.fuente_numeros,self.fuente_botones,self.fuente_info,self.fuente_feedback = [pygame.font.SysFont('Arial',s) for s in [TAMANO_FUENTE_NUMEROS_CABALLO,TAMANO_FUENTE_BOTONES_CABALLO,TAMANO_FUENTE_INFO_CABALLO,TAMANO_FUENTE_FEEDBACK_CABALLO]]
    
    def dibujar_gui_completa(self): # (Misma función que antes)
        self.ventana.fill(self.color_fondo); self._dibujar_tablero(); self._dibujar_botones(); self._dibujar_feedback_mensaje(); pygame.display.flip()

    def _dibujar_tablero(self): # (Misma función que antes)
        for r in range(self.tamaño):
            for c in range(self.tamaño):
                cb=self.color_celda_clara if(r+c)%2==0 else self.color_celda_oscura; rb=pygame.Rect(c*self.celda_ancho,r*self.celda_alto,self.celda_ancho,self.celda_alto)
                cd,rd=cb,rb
                if self.celda_hover==(r,c): cd=tuple(max(0,min(255,cv+15 if sum(cb)<382 else cv-15))for cv in cb);rd=rb.inflate(ANIMACION_CELDA_HOVER_INFLATE,ANIMACION_CELDA_HOVER_INFLATE)
                pygame.draw.rect(self.ventana,cd,rd)
                if self.celda_sugerida==(r,c): s=pygame.Surface((rd.width,rd.height),pygame.SRCALPHA);pygame.draw.rect(s,self.color_sugerencia_ayuda,(0,0,rd.width,rd.height),border_radius=3);self.ventana.blit(s,rd.topleft)
                v=self.juego.tablero[r][c];_=[self.ventana.blit(tr:=self.fuente_numeros.render(str(v),1,self.color_texto_numeros),tr.get_rect(center=rb.center))] if v!=-1 else 0
                pygame.draw.rect(self.ventana,self.color_borde_tablero,rd,BORDE_GROSOR_CELDA_CABALLO)

    def _dibujar_botones(self):
        y_botones = self.alto - ESPACIO_BOTONES_Y_CABALLO + (ESPACIO_BOTONES_Y_CABALLO - BOTON_ALTO_CABALLO) / 2
        
        num_botones_jugar, num_botones_ver_sol = 6, 3 # 6 botones para jugar (incluye Menú)
        margen_total, espacio_entre = 20, 5
        
        ancho_boton_jugar = (self.ancho - margen_total - (num_botones_jugar -1) * espacio_entre) // num_botones_jugar
        ancho_boton_ver_sol = (self.ancho - margen_total - (num_botones_ver_sol -1) * espacio_entre) // num_botones_ver_sol
        offset_x = 10
        
        self.mapa_botones_rects = {} 
        botones_actuales_info = []

        if self.modo == "jugar":
            defs_jugar = [
                {"texto": "Resolver", "accion_id": "resolver", "color": self.color_boton_resolver},
                {"texto": "Reiniciar", "accion_id": "reiniciar", "color": self.color_boton_reiniciar},
                {"texto": "Verificar", "accion_id": "verificar", "color": self.color_boton_verificar},
                {"texto": "Ayuda", "accion_id": "ayuda", "color": self.color_boton_navegacion},
                {"texto": "Deshacer", "accion_id": "deshacer", "color": self.color_boton_navegacion},
                {"texto": "Menú", "accion_id": "volver_menu", "color": self.color_boton_navegacion}
            ]
            for i, d in enumerate(defs_jugar):
                rect = pygame.Rect(offset_x + i*(ancho_boton_jugar+espacio_entre), y_botones, ancho_boton_jugar, BOTON_ALTO_CABALLO)
                botones_actuales_info.append({"rect": rect, "color": d["color"], "texto": d["texto"]})
                self.mapa_botones_rects[d["accion_id"]] = rect
        else: # modo "ver_soluciones"
            defs_ver_sol = [
                {"texto": "Anterior", "accion_id": "anterior", "color": self.color_boton_navegacion},
                {"texto": "Siguiente", "accion_id": "siguiente", "color": self.color_boton_navegacion},
                {"texto": "Volver", "accion_id": "volver", "color": self.color_boton_reiniciar}
            ]
            for i, d in enumerate(defs_ver_sol):
                rect = pygame.Rect(offset_x + i*(ancho_boton_ver_sol+espacio_entre), y_botones, ancho_boton_ver_sol, BOTON_ALTO_CABALLO)
                botones_actuales_info.append({"rect": rect, "color": d["color"], "texto": d["texto"]})
                self.mapa_botones_rects[d["accion_id"]] = rect
            if self.juego.soluciones:
                texto_sol = self.fuente_info.render(f"Sol: {self.solucion_actual_idx + 1}/{len(self.juego.soluciones)}", 1, self.color_texto_general)
                self.ventana.blit(texto_sol, (self.mapa_botones_rects["volver"].right + 10, y_botones + (BOTON_ALTO_CABALLO - texto_sol.get_height()) // 2))

        self.boton_hover_texto = None; mouse_pos = pygame.mouse.get_pos()
        for bd in botones_actuales_info:
            hover = bd["rect"].collidepoint(mouse_pos)
            cd,rd=bd["color"],bd["rect"]
            if hover: self.boton_hover_texto=bd["texto"];cd=self.color_boton_hover;rd=rd.inflate(BOTON_HOVER_INFLATE_CABALLO*2,BOTON_HOVER_INFLATE_CABALLO*2)
            pygame.draw.rect(self.ventana,cd,rd,border_radius=BOTON_BORDE_RADIO_CABALLO)
            bcd=tuple(max(0,c-30)for c in cd);pygame.draw.rect(self.ventana,bcd,rd,BOTON_BORDE_GROSOR_CABALLO,border_radius=BOTON_BORDE_RADIO_CABALLO)
            tr=self.fuente_botones.render(bd["texto"],1,self.color_texto_general);self.ventana.blit(tr,tr.get_rect(center=rd.center))

    def _dibujar_feedback_mensaje(self): # (Misma función que antes)
        if self.mensaje_feedback_texto and pygame.time.get_ticks()<self.mensaje_feedback_tiempo_fin:
            tr=self.fuente_feedback.render(self.mensaje_feedback_texto,1,self.color_texto_general);rt=tr.get_rect(centerx=self.ancho/2,bottom=self.alto-ESPACIO_BOTONES_Y_CABALLO-(ESPACIO_FEEDBACK_Y_CABALLO-tr.get_height())/2-5)
            fr=rt.inflate(20,10);s=pygame.Surface(fr.size,pygame.SRCALPHA);s.fill(self.color_feedback_fondo);self.ventana.blit(s,fr.topleft);self.ventana.blit(tr,rt)
        elif pygame.time.get_ticks()>=self.mensaje_feedback_tiempo_fin:self.mensaje_feedback_texto=""

    def _mostrar_feedback(self, texto, duracion_ms=None): # (Misma función que antes)
        self.mensaje_feedback_texto=texto;self.mensaje_feedback_tiempo_fin=pygame.time.get_ticks()+(duracion_ms or self.duracion_feedback_ms);print(f"[Feedback GUI Caballo] {texto}")

    def _guardar_resultado_caballo(self, completitud: bool): # (Misma función que antes)
        if self.resultado_guardado_este_intento: return
        pos_i_str = str(self.posicion_inicial_registrada) if self.posicion_inicial_registrada else "No registrada"
        movs = self.paso_actual_manual -1 if self.paso_actual_manual > 0 else 0
        self._mostrar_feedback(f"Guardando: Pos Ini={pos_i_str}, Movs={movs}, Completado={completitud}",3000)
        print(f"SIMULANDO ENVÍO CABALLO: Pos Ini={pos_i_str}, Movs={movs}, Completado={completitud}")
        self._callback_guardado_caballo({'status':'ok','message':'KnightsTour score saved (simulado)'},completitud)

    def _callback_guardado_caballo(self, response, completitud_original): # (Misma función que antes)
        sm="Ok" if response and response.get("status")=="ok" else "Error";dt=response.get('message') if response else "N/A"
        self._mostrar_feedback(f"Guardado Servidor: {sm} - {dt}",3000)
        if completitud_original and sm=="Ok": self.resultado_guardado_este_intento=True

    def manejar_eventos(self):
        mouse_pos=pygame.mouse.get_pos();self.celda_hover=None
        if mouse_pos[1]<(self.alto-ESPACIO_BOTONES_Y_CABALLO-ESPACIO_FEEDBACK_Y_CABALLO):
            c,f=mouse_pos[0]//self.celda_ancho,mouse_pos[1]//self.celda_alto
            if 0<=f<self.tamaño and 0<=c<self.tamaño:self.celda_hover=(f,c)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: self.accion_al_salir="CERRAR_JUEGO"; return False
            if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                if self._manejar_clic(ev.pos):
                    if self.accion_al_salir=="VOLVER_MENU": return False
                    return True
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE: self.accion_al_salir="VOLVER_MENU"; return False
                # Aquí otros atajos si los tienes
        return True

    def _manejar_clic(self, pos_clic):
        x,y=pos_clic; self.celda_sugerida=None
        zona_tablero_alto=self.alto-ESPACIO_BOTONES_Y_CABALLO-ESPACIO_FEEDBACK_Y_CABALLO
        if self.modo=="jugar" and y<zona_tablero_alto:
            col,fila=x//self.celda_ancho,y//self.celda_alto
            if 0<=fila<self.tamaño and 0<=col<self.tamaño:
                ta=[r[:] for r in self.juego.tablero]; pa=self.paso_actual_manual; upa=self.ultima_pos_caballo_manual; pira = self.posicion_inicial_registrada
                mov_ok, msg = self.juego.mover_caballo_jugador(fila,col,self.paso_actual_manual,self.ultima_pos_caballo_manual)
                if mov_ok:
                    self.historial_movimientos.append((ta,pa,upa,pira))
                    if len(self.historial_movimientos)>(self.tamaño*self.tamaño)+5: self.historial_movimientos.pop(0)
                    if self.paso_actual_manual==1: self.posicion_inicial_registrada=(fila,col)
                    self.ultima_pos_caballo_manual=(fila,col);self.paso_actual_manual+=1;self.resultado_guardado_este_intento=False
                    if self.paso_actual_manual > self.tamaño*self.tamaño: self._mostrar_feedback("¡Tablero completo! Verifica.")
                    return True
                else: self._mostrar_feedback(msg,1500); return False
        # Clic en botones
        for accion_id, rect_boton in self.mapa_botones_rects.items():
            if rect_boton.collidepoint(x,y):
                self._ejecutar_accion_boton(accion_id)
                return True
        return False

    def _reset_estado_juego_manual(self): # (Misma función que antes)
        self.juego.reiniciar_tablero();self.paso_actual_manual=1;self.ultima_pos_caballo_manual=None
        self.historial_movimientos=[];self.celda_sugerida=None;self.resultado_guardado_este_intento=False
        self.posicion_inicial_registrada=None 

    def _ejecutar_accion_boton(self, accion_id): # Modificado para incluir volver_menu
        self.celda_sugerida = None
        if   accion_id == "resolver":
            self._mostrar_feedback("Buscando soluciones...",10000);pygame.display.flip()
            sols=self.juego.encontrar_soluciones_autoresolver()
            if sols:self.modo="ver_soluciones";self.solucion_actual_idx=0;self.juego.tablero=[r[:]for r in sols[0]];self._mostrar_feedback(f"{len(sols)} soluciones.")
            else: self._mostrar_feedback("No se encontraron soluciones.")
            self._reset_estado_juego_manual()
        elif accion_id == "reiniciar": self._reset_estado_juego_manual();self.modo="jugar";self._mostrar_feedback("Tablero reiniciado.")
        elif accion_id == "verificar":
            if self.paso_actual_manual==1 and not any(any(c!=-1 for c in r)for r in self.juego.tablero):self._mostrar_feedback("Tablero vacío.",2000);return
            es_v=self.juego.es_solucion_valida_jugador()
            if es_v:self._mostrar_feedback("¡Recorrido Completo y Válido!")
            else:self._mostrar_feedback("Recorrido Incorrecto." if self.paso_actual_manual-1==self.tamaño*self.tamaño else f"Recorrido Incompleto. Faltan {self.tamaño*self.tamaño-(self.paso_actual_manual-1)}.")
            if self.paso_actual_manual-1==self.tamaño*self.tamaño: self._guardar_resultado_caballo(completitud=es_v)
        elif accion_id == "anterior" and self.juego.soluciones:self.solucion_actual_idx=(self.solucion_actual_idx-1+len(self.juego.soluciones))%len(self.juego.soluciones);self.juego.tablero=[r[:]for r in self.juego.soluciones[self.solucion_actual_idx]]
        elif accion_id == "siguiente" and self.juego.soluciones:self.solucion_actual_idx=(self.solucion_actual_idx+1)%len(self.juego.soluciones);self.juego.tablero=[r[:]for r in self.juego.soluciones[self.solucion_actual_idx]]
        elif accion_id == "volver": self.modo="jugar";self._reset_estado_juego_manual();self._mostrar_feedback("Modo de juego.")
        elif accion_id == "deshacer":
            if self.modo=="jugar" and self.historial_movimientos:
                ta,pa,upa,pira=self.historial_movimientos.pop()
                self.juego.tablero=[r[:]for r in ta];self.paso_actual_manual=pa;self.ultima_pos_caballo_manual=upa;self.posicion_inicial_registrada=pira
                self._mostrar_feedback("Movimiento deshecho.");self.resultado_guardado_este_intento=False
            elif self.modo!="jugar":self._mostrar_feedback("Deshacer no disponible.")
            else:self._mostrar_feedback("No hay movimientos para deshacer.")
        elif accion_id == "ayuda":
            if self.modo=="jugar":self._dar_ayuda_caballo()
            else:self._mostrar_feedback("Ayuda no disponible.")
        elif accion_id == "volver_menu": # Nueva acción
            self.accion_al_salir = "VOLVER_MENU"


    def _dar_ayuda_caballo(self): # (Misma función que antes)
        if self.paso_actual_manual>self.tamaño*self.tamaño:self._mostrar_feedback("Tablero completo.",2000);return
        if self.ultima_pos_caballo_manual is None and self.paso_actual_manual>1:self._mostrar_feedback("Error: No hay última pos.",2000);return
        if self.paso_actual_manual==1:
            for r in range(self.tamaño):
                for c in range(self.tamaño):
                    if self.juego.tablero[r][c]==-1:self.celda_sugerida=(r,c);self._mostrar_feedback(f"Sugerencia: Empieza en ({r+1},{chr(ord('A')+c)}).");return
            self._mostrar_feedback("Tablero lleno.",2000);return
        else:sx,sy=self.ultima_pos_caballo_manual
        # Heurística de Warnsdorff para la ayuda (simple)
        movs_validos_con_salidas = []
        for dx,dy in self.juego.movimientos_posibles_caballo:
            nx,ny=sx+dx,sy+dy
            if self.juego.es_valido(nx,ny): # es_valido verifica si la celda está DENTRO y VACÍA
                # Contar salidas desde (nx,ny) sin modificar el tablero
                num_salidas_desde_nx_ny = 0
                # Temporalmente simular que (nx,ny) está ocupada para contar salidas desde allí
                original_val_nx_ny = self.juego.tablero[nx][ny] # Debería ser -1
                self.juego.tablero[nx][ny] = self.paso_actual_manual # Simular ocupación
                
                for ddx,ddy in self.juego.movimientos_posibles_caballo:
                    nnx,nny=nx+ddx,ny+ddy
                    # es_valido ahora ve (nx,ny) como ocupada, así que no la contará como salida de sí misma.
                    # Pero para Warnsdorff, necesitamos que (nx,ny) esté vacía al contar sus salidas.
                    # Por lo tanto, es_valido debe ser usado con el tablero *antes* de colocar el caballo en (nx,ny)
                # Corrección para Warnsdorff: contar salidas desde (nx,ny) asumiendo que está vacía
                # pero las otras casillas están como están.
                self.juego.tablero[nx][ny] = -1 # Restaurar a vacía para contar bien las salidas
                num_salidas_desde_nx_ny = self.juego.contar_salidas(nx, ny)
                self.juego.tablero[nx][ny] = original_val_nx_ny # Dejar como estaba (vacía)

                movs_validos_con_salidas.append((num_salidas_desde_nx_ny, nx, ny))

        if movs_validos_con_salidas:
            movs_validos_con_salidas.sort() # Menor número de salidas primero
            _, mejor_x, mejor_y = movs_validos_con_salidas[0]
            self.celda_sugerida = (mejor_x, mejor_y)
            self._mostrar_feedback(f"Sugerencia (Warnsdorff): Mueve a ({mejor_x+1}, {chr(ord('A')+mejor_y)}).")
            return
        self._mostrar_feedback("No se encontraron movimientos válidos.",2000)

    def ejecutar(self):
        self._mostrar_feedback(f"Recorrido del Caballo {self.tamaño}x{self.tamaño}. ¡Suerte!", 2500)
        reloj = pygame.time.Clock(); corriendo = True; self.accion_al_salir = None
        while corriendo:
            corriendo = self.manejar_eventos()
            if not corriendo: break 
            self.dibujar_gui_completa(); reloj.tick(FPS_CABALLO)
        print(f"[RecorridoCaballoGUI] Saliendo. Acción: {self.accion_al_salir if self.accion_al_salir else 'CERRAR_JUEGO'}")
        return self.accion_al_salir if self.accion_al_salir else "CERRAR_JUEGO"

if __name__ == "__main__": # (Mismo bloque de prueba que antes)
    print("Ejecutando RecorridoCaballoGUI directamente para pruebas...")
    # ... (código de creación de directorios y sys.path si es necesario) ...
    juego_gui_caballo = RecorridoCaballoGUI(tamaño=6) 
    resultado_salida = juego_gui_caballo.ejecutar()
    print(f"El juego RecorridoCaballo terminó con la acción: {resultado_salida}")
    pygame.quit()
    sys.exit()