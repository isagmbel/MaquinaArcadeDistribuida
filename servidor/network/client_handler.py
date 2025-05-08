# servidor/network/client_handler.py
import threading
import socket
import json
from servidor.database.db_manager import DatabaseManager

class ClientHandlerThread(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address, db_manager: DatabaseManager):
        super().__init__()
        self.client_socket = client_socket
        self.client_address = client_address
        self.db_manager = db_manager
        self.running = True
        print(f"[NUEVA CONEXION] {self.client_address} conectado.")

    def run(self):
        try:
            while self.running:
                # Esperar a recibir datos del cliente
                # Asumimos que los mensajes son JSON y terminan con \n
                message_chunks = []
                while True:
                    chunk = self.client_socket.recv(1024)
                    if not chunk: # Conexión cerrada por el cliente
                        self.running = False
                        break
                    message_chunks.append(chunk.decode('utf-8'))
                    if chunk.decode('utf-8').endswith('\n'): # Fin del mensaje JSON
                        break
                
                if not self.running or not message_chunks : # Si se cerró o no hay mensaje
                    break

                full_message = "".join(message_chunks).strip()
                if not full_message: # Mensaje vacío después de strip
                    continue

                print(f"[{self.client_address}] Recibido: {full_message}")
                
                try:
                    data = json.loads(full_message)
                    self.handle_client_request(data)
                except json.JSONDecodeError:
                    print(f"[{self.client_address}] Error: Mensaje JSON inválido.")
                    self.send_response({"status": "error", "message": "Invalid JSON"})
                except Exception as e:
                    print(f"[{self.client_address}] Error procesando petición: {e}")
                    self.send_response({"status": "error", "message": f"Server error: {e}"})

        except ConnectionResetError:
            print(f"[{self.client_address}] Conexión reiniciada por el cliente.")
        except Exception as e:
            print(f"[{self.client_address}] Error en el hilo del cliente: {e}")
        finally:
            print(f"[{self.client_address}] Desconectado.")
            self.client_socket.close()
            # self.db_manager.close() # No cerrar aquí, db_manager es compartido

    def handle_client_request(self, data: dict):
        action = data.get("action")
        game_type = data.get("game_type")
        payload = data.get("data")

        if action == "save_score" and payload:
            if game_type == "n_reinas":
                self.db_manager.add_n_reinas_score(
                    n_value=payload.get("n_value"),
                    success=payload.get("success"),
                    attempts=payload.get("attempts")
                )
                self.send_response({"status": "ok", "message": "NReinas score saved"})
            elif game_type == "knights_tour":
                self.db_manager.add_knights_tour_score(
                    start_position=payload.get("start_position"),
                    moves_made=payload.get("moves_made"),
                    completed=payload.get("completed")
                )
                self.send_response({"status": "ok", "message": "KnightsTour score saved"})
            elif game_type == "torres_hanoi":
                self.db_manager.add_torres_hanoi_score(
                    num_disks=payload.get("num_disks"),
                    moves_made=payload.get("moves_made"),
                    success=payload.get("success")
                )
                self.send_response({"status": "ok", "message": "TorresHanoi score saved"})
            else:
                self.send_response({"status": "error", "message": "Unknown game type"})
        else:
            self.send_response({"status": "error", "message": "Unknown action or missing data"})

    def send_response(self, response_data: dict):
        try:
            message = json.dumps(response_data) + '\n' # Añadir delimitador
            self.client_socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f"[{self.client_address}] Error enviando respuesta: {e}")

    def stop(self):
        self.running = False
        # Podrías necesitar un self.client_socket.shutdown(socket.SHUT_RDWR) si el recv es bloqueante
        # y el hilo no se detiene. O un timeout en el socket.
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR) # Para desbloquear recv
            except OSError:
                pass # Socket ya podría estar cerrado
            self.client_socket.close()