# Máquina Arcade Distribuida en Python

Este proyecto implementa una Máquina Arcade distribuida con tres juegos clásicos basados en problemas de álgebra y lógica: el Problema de las N Reinas, el Recorrido del Caballo (Knight's Tour) y las Torres de Hanói. La aplicación sigue una arquitectura cliente-servidor, donde cada juego actúa como un cliente independiente que se comunica con un servidor central para el almacenamiento de los resultados de las partidas.

## Características Principales

*   **Tres Juegos Clásicos:**
    *   N Reinas
    *   Recorrido del Caballo
    *   Torres de Hanói
*   **Arquitectura Cliente-Servidor:**
    *   Servidor central para persistencia de datos de partidas.
    *   Clientes (juegos) se comunican con el servidor vía sockets TCP/IP.
*   **Programación Orientada a Objetos (POO):** Toda la lógica implementada siguiendo principios de POO.
*   **Paralelismo e Hilos (Threads):**
    *   El servidor es multihilo para manejar múltiples clientes simultáneamente.
    *   Los clientes utilizan hilos para la comunicación de red, evitando congelar la GUI.
*   **Interfaz Gráfica de Usuario (GUI):** Cada juego cuenta con una GUI interactiva desarrollada con Pygame.
*   **Base de Datos y ORM:**
    *   El servidor utiliza SQLite para almacenar los resultados.
    *   SQLAlchemy se emplea como ORM para la gestión de la base de datos.
*   **Separación de Lógica:** Clara separación entre la lógica de los juegos, la interfaz gráfica y la comunicación de red.

## Estructura del Proyecto
```
MAQUINADEARCADE/
├── cliente/
│ ├── init.py
│ ├── comunicacion/ # Lógica de red del cliente
│ │ ├── init.py
│ │ └── cliente_network.py
│ ├── gui/ # Módulos de la Interfaz Gráfica de Usuario
│ │ ├── init.py
│ │ ├── assets/ # Recursos gráficos y fuentes
│ │ ├── menu_gui.py # Menú principal para seleccionar juegos
│ │ ├── n_reinas_gui.py
│ │ ├── recorrido_caballo_gui.py
│ │ └── torres_hanoi_gui.py
│ └── juegos/ # Lógica interna de cada juego
│ ├── init.py
│ ├── n_reinas.py
│ ├── recorrido_caballo.py
│ └── torres_hanoi.py
├── servidor/
│ ├── init.py
│ ├── database/ # Gestión de la base de datos
│ │ ├── init.py
│ │ ├── db_manager.py
│ │ └── models.py # Modelos SQLAlchemy
│ ├── network/ # Lógica de red del servidor
│ │ ├── init.py
│ │ └── client_handler.py # Hilo para manejar cada cliente
│ ├── main_servidor.py # Script principal para iniciar el servidor
│ └── servidor_config.py # Configuraciones del servidor
│
├── main.py # Script principal para iniciar el cliente (menú)
├── README.md # Este archivo
└── requirements.txt # Dependencias del proyecto
```

## Requisitos Previos

*   Python 3.8 o superior.
*   `pip` (manejador de paquetes de Python).

## Instalación de Dependencias

1.  Clona este repositorio o descarga los archivos del proyecto.
2.  Navega hasta el directorio raíz del proyecto (`MAQUINADEARCADE/`) en tu terminal.
3.  Crea un entorno virtual (recomendado):
    ```bash
    python -m venv venv
    ```
    Activa el entorno virtual:
    *   En Windows: `venv\Scripts\activate`
    *   En macOS/Linux: `source venv/bin/activate`
4.  Instala las dependencias listadas en `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
    El archivo `requirements.txt` debería contener al menos:
    ```
    pygame
    SQLAlchemy
    ```

## Cómo Ejecutar la Aplicación

Para ejecutar la máquina arcade, necesitas iniciar el servidor primero y luego el cliente. Ambos deben ejecutarse desde el directorio raíz del proyecto (`MAQUINADEARCADE/`).

### 1. Iniciar el Servidor

*   Abre una terminal.
*   Navega al directorio `MAQUINADEARCADE/`.
*   Ejecuta el siguiente comando:
    ```bash
    python servidor/main_servidor.py
    ```
*   El servidor comenzará a escuchar conexiones. Deberías ver un mensaje como:
    `[SERVIDOR] Escuchando en localhost:12345`
*   **Deja esta terminal abierta mientras el servidor esté en uso.**

### 2. Iniciar el Cliente (Máquina Arcade)

*   Abre **otra** terminal (no cierres la del servidor).
*   Navega al directorio `MAQUINADEARCADE/`.
*   Ejecuta el siguiente comando:
    ```bash
    python main.py
    ```
*   Aparecerá la ventana del menú principal de la máquina arcade. Desde aquí podrás seleccionar y jugar a los diferentes juegos.
*   Los resultados de las partidas se enviarán al servidor y se almacenarán en la base de datos `arcade_scores.db` (ubicada en `MAQUINADEARCADE/` o donde lo especifique la configuración del servidor si se ejecuta desde ahí).

## Cómo Detener la Aplicación

*   **Para detener el Cliente:** Cierra la ventana de Pygame del menú o del juego. Si esto no cierra el proceso en la terminal, ve a la terminal donde ejecutaste `python main.py` y presiona `Ctrl+C`.
*   **Para detener el Servidor:** Ve a la terminal donde ejecutaste `python servidor/main_servidor.py` y presiona `Ctrl+C`. El servidor intentará un apagado ordenado.

## Posibles Mejoras Futuras

*   Implementar un sistema de autenticación de usuarios.
*   Mostrar tablas de puntuaciones en la GUI del cliente.
*   Añadir más juegos.
*   Mejorar la robustez de la comunicación de red (reintentos, manejo avanzado de errores).
*   Utilizar `asyncio` para la concurrencia en el servidor en lugar de hilos tradicionales.
*   Empaquetar la aplicación para una distribución más sencilla.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir cambios importantes o envía un *pull request*.
