# MAQUINADEARCADE/servidor/main_servidor.py
import socket
import threading
import sys
from pathlib import Path 


SERVER_SCRIPT_FILE = Path(__file__).resolve() # Ruta completa a este archivo (main_servidor.py)
PROJECT_ROOT = SERVER_SCRIPT_FILE.parents[1]  # Sube un nivel: de servidor/main_servidor.py a MAQUINADEARCADE/

# Añadir el directorio raíz del proyecto a sys.path si no está ya
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT)) # Insertar al principio para prioridad

from servidor.servidor_config import SERVER_HOST, SERVER_PORT, MAX_CLIENTS # Asumo que DATABASE_URL también está aquí o no es necesario directamente para ArcadeServer
from servidor.database.db_manager import DatabaseManager
from servidor.database.models import create_tables
from servidor.network.client_handler import ClientHandlerThread

class ArcadeServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.db_manager = DatabaseManager() # Una instancia para todos los hilos
        self.client_threads = []
        self.running = True

        # Crear tablas si no existen
        print("Inicializando base de datos...")
        create_tables() # Esto usa DATABASE_URL desde servidor_config.py a través de models.py
        print("Base de datos lista.")

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Reutilizar dirección
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(MAX_CLIENTS)
            print(f"[SERVIDOR] Escuchando en {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    handler = ClientHandlerThread(client_socket, client_address, self.db_manager)
                    handler.start()
                    self.client_threads.append(handler)
                    # Limpiar hilos terminados
                    self.client_threads = [t for t in self.client_threads if t.is_alive()]
                except OSError as e: 
                    if self.running: 
                        print(f"[SERVIDOR] Error en accept(): {e}")
                    break 
                except Exception as e:
                    print(f"[SERVIDOR] Error inesperado al aceptar conexión: {e}")
                    
        except Exception as e:
            print(f"[SERVIDOR] Error al iniciar: {e}")
        finally:
            self.stop()

    def stop(self):
        print("[SERVIDOR] Deteniendo servidor...")
        self.running = False # Señal para que el bucle de accept termine
        
        if self.server_socket:
            try:
                self.server_socket.close() 
                print("[SERVIDOR] Socket de escucha cerrado.")
            except Exception as e:
                print(f"[SERVIDOR] Error al cerrar socket de escucha: {e}")

        # Esperar a que los hilos de cliente terminen
        print(f"[SERVIDOR] Esperando a que terminen {len(self.client_threads)} hilos de cliente...")
        for thread in self.client_threads:
            if thread.is_alive():
                print(f"[SERVIDOR] Deteniendo hilo {thread.name}...")
                thread.stop() # Llama al método stop del hilo ClientHandler
                thread.join(timeout=2) # Espera un máximo de 2 segundos
                if thread.is_alive():
                    print(f"[SERVIDOR] Hilo {thread.name} no se detuvo a tiempo.")
        
        if self.db_manager:
            try:
                self.db_manager.close()
                print("[SERVIDOR] Conexión a base de datos cerrada.")
            except Exception as e:
                print(f"[SERVIDOR] Error al cerrar conexión de base de datos: {e}")
        print("[SERVIDOR] Servidor completamente detenido.")


if __name__ == "__main__":
    # Debug: Imprimir sys.path después de la modificación para confirmar
    # print(f"DEBUG: sys.path en main_servidor.py: {sys.path}")
    
    server = ArcadeServer(SERVER_HOST, SERVER_PORT)
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Interrupción por teclado recibida. Iniciando apagado...")
    except Exception as e:
        print(f"[SERVIDOR] Excepción no controlada en el nivel principal: {e}")
    finally:
        # Asegurarse de que stop se llama incluso si start() falla o hay KeyboardInterrupt
        if server.running: # Si el servidor todavía cree que está corriendo (ej. si start falló pronto)
            server.stop() 
        elif not server.running and server.server_socket is not None : # Si ya se marcó como no running pero queremos asegurar limpieza
             # Esta condición es un poco redundante si stop() ya se llamó, pero por si acaso.
             if not server.server_socket._closed: # Evitar llamar close en socket ya cerrado
                 server.stop() # Llama a stop si no se ha completado el apagado
        print("[SERVIDOR] Script principal finalizado.")