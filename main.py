import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cliente.gui.menu_gui import MenuGUI

if __name__ == "__main__":

    print(f"Python sys.path incluye: {PROJECT_ROOT}") # Para depuración
    print("Lanzando el menú principal del cliente...")

    # Lanzar la interfaz gráfica principal
    menu = MenuGUI()
    menu.ejecutar()