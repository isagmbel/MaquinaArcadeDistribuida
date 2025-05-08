# cliente/comunicacion/cliente_network.py
import socket
import json
import threading # Para enviar en segundo plano

# Puedes obtener HOST y PORT de un archivo de config_cliente.py si quieres
SERVER_HOST = 'localhost' # Debe coincidir con servidor_config.py
SERVER_PORT = 12345     # Debe coincidir con servidor_config.py

class ClientNetwork:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # Singleton para la conexión de red
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.client_socket = None
        self._connect_lock = threading.Lock() # Para evitar múltiples intentos de conexión simultáneos
        self._initialized = True
        # No conectamos aquí, sino bajo demanda o explícitamente

    def _connect(self):
        # Intenta conectar solo si no está ya conectado
        with self._connect_lock:
            if self.client_socket is None or not self._is_socket_connected():
                try:
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.settimeout(5) # Timeout para conexión y operaciones
                    self.client_socket.connect((self.host, self.port))
                    print(f"[CLIENTE] Conectado a {self.host}:{self.port}")
                    return True
                except (socket.error, ConnectionRefusedError, socket.timeout) as e:
                    print(f"[CLIENTE] Error al conectar con el servidor: {e}")
                    self.client_socket = None # Asegurar que está None si falla
                    return False
            return True # Ya estaba conectado

    def _is_socket_connected(self):
        if not self.client_socket:
            return False
        try:
            # SO_ERROR devuelve 0 si no hay error pendiente (conectado)
            error_code = self.client_socket.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            return error_code == 0
        except socket.error:
            return False # Socket no válido o cerrado

    def send_data(self, data: dict, callback=None):
        """Envía datos al servidor en un hilo separado."""
        def _send_task():
            if not self._connect(): # Intenta conectar/reconectar
                print("[CLIENTE] No se pudo conectar para enviar datos.")
                if callback:
                    callback({"status": "error", "message": "Connection failed"})
                return

            try:
                message = json.dumps(data) + '\n' # Asegurar delimitador
                self.client_socket.sendall(message.encode('utf-8'))
                print(f"[CLIENTE] Enviado: {data}")

                # Esperar respuesta (opcional, pero bueno para confirmación)
                response_chunks = []
                while True:
                    chunk = self.client_socket.recv(1024)
                    if not chunk: # El servidor cerró la conexión
                        print("[CLIENTE] El servidor cerró la conexión inesperadamente.")
                        self.close() # Marcar socket como cerrado
                        if callback:
                            callback({"status": "error", "message": "Server closed connection"})
                        return
                    response_chunks.append(chunk.decode('utf-8'))
                    if chunk.decode('utf-8').endswith('\n'):
                        break
                
                full_response = "".join(response_chunks).strip()
                response_json = json.loads(full_response)
                print(f"[CLIENTE] Recibida respuesta: {response_json}")
                if callback:
                    callback(response_json)

            except (socket.error, socket.timeout, json.JSONDecodeError) as e:
                print(f"[CLIENTE] Error durante la comunicación: {e}")
                self.close() # Asumir que la conexión está mal
                if callback:
                    callback({"status": "error", "message": f"Communication error: {e}"})
            # No cerramos la conexión aquí para reutilizarla
        
        # Ejecutar la tarea de envío en un nuevo hilo
        thread = threading.Thread(target=_send_task, daemon=True)
        thread.start()

    def save_n_reinas_score(self, n_value: int, success: bool, attempts: int, callback=None):
        payload = {
            "action": "save_score",
            "game_type": "n_reinas",
            "data": {
                "n_value": n_value,
                "success": success,
                "attempts": attempts
            }
        }
        self.send_data(payload, callback)

    def save_knights_tour_score(self, start_position: str, moves_made: int, completed: bool, callback=None):
        payload = {
            "action": "save_score",
            "game_type": "knights_tour",
            "data": {
                "start_position": start_position,
                "moves_made": moves_made,
                "completed": completed
            }
        }
        self.send_data(payload, callback)

    def save_torres_hanoi_score(self, num_disks: int, moves_made: int, success: bool, callback=None):
        payload = {
            "action": "save_score",
            "game_type": "torres_hanoi",
            "data": {
                "num_disks": num_disks,
                "moves_made": moves_made,
                "success": success
            }
        }
        self.send_data(payload, callback)

    def close(self):
        if self.client_socket:
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass # Socket ya podría estar cerrado
            self.client_socket.close()
            self.client_socket = None
            print("[CLIENTE] Conexión cerrada.")

# Para obtener la instancia única fácilmente
def get_network_client():
    return ClientNetwork()