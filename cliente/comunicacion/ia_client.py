# MAQUINADEARCADE/cliente/comunicacion/ia_client.py
import requests
import json
import threading
import time

API_URL = "https://api-inference.huggingface.co/models/distilgpt2"

API_KEY = "" 
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json" 
}

def solicitar_sugerencia(juego_nombre, estado_json_str):
   
    prompt_texto_simple = f"Hola, estoy jugando {juego_nombre}. ¿Alguna idea?"

    payload_simple = {
        "inputs": prompt_texto_simple,
        "options": { # Mantenemos options por si ayuda con la carga del modelo
            "wait_for_model": True,
            "use_cache": False
        }
    }
   

    print(f"--- [IA_CLIENT DEBUG] ---")
    print(f"API URL: {API_URL}")
    print(f"Headers Enviados: {HEADERS}")
    print(f"Payload Enviado: {json.dumps(payload_simple, indent=2)}")
    print(f"-------------------------")

    try:
        # Usaremos una sesión para que `prepared_request` funcione bien
        session = requests.Session()
        request = requests.Request('POST', API_URL, headers=HEADERS, json=payload_simple)
        prepared_request = session.prepare_request(request)

        print(f"--- [IA_CLIENT PREPARED REQUEST DEBUG] ---")
        print(f"Method: {prepared_request.method}")
        print(f"URL: {prepared_request.url}")
        print(f"Headers: {prepared_request.headers}")
        print(f"Body (Payload): {prepared_request.body.decode() if prepared_request.body else 'No Body'}")
        print(f"------------------------------------")

        response = session.send(prepared_request, timeout=45) # Aumentamos un poco el timeout

        print(f"--- [IA_CLIENT RESPONSE DEBUG] ---")
        print(f"Código de estado: {response.status_code}")
        print(f"Headers de Respuesta: {response.headers}")
        print(f"Contenido de Respuesta (texto):")
        try:
   
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print(response.text) # Imprimir como texto plano si no es JSON
        print(f"--------------------------------")


        if response.status_code == 401:
            return "Error de la IA: API Key inválida o sin permisos (401)."
       
        
        response.raise_for_status()
        
        response_data = response.json() 

        if isinstance(response_data, list) and response_data:
            generated_text = response_data[0].get("generated_text")
            if generated_text: return generated_text
            return "La IA respondió pero no generó texto."
        elif isinstance(response_data, dict) and "error" in response_data: # Error del modelo
            error_msg = response_data["error"]
            if "estimated_time" in response_data:
                error_msg += f" El modelo puede estar cargando, tiempo estimado: {response_data['estimated_time']:.0f}s."
            return f"Error de la IA: {error_msg}"
        else:
            return f"Respuesta inesperada de la IA (JSON no reconocido): {str(response_data)[:300]}"

    except requests.exceptions.HTTPError as http_err:
      
        return f"Error HTTP ({http_err.response.status_code}) al contactar la IA. Ver consola para detalles."
    except requests.exceptions.RequestException as req_err:
        return f"Error de red al contactar la IA: {req_err}. Ver consola para detalles."
    except json.JSONDecodeError:
     
        return f"Error de formato en respuesta de la IA (JSON inválido tras éxito HTTP). Ver consola."
    except Exception as e:
        return f"Error inesperado solicitando sugerencia: {e}. Ver consola para detalles."

class IAHelperThread(threading.Thread):
    def __init__(self, juego, estado_json_str, callback):
        super().__init__()
        self.juego_nombre = juego
        self.estado_json_str = estado_json_str
        self.callback = callback
    def run(self):
        resultado = solicitar_sugerencia(self.juego_nombre, self.estado_json_str)
        self.callback(resultado)