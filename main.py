from gui.menu_gui import MenuGUI
import threading
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))


if __name__ == "__main__":

    
    # Lanzar la interfaz gráfica principal
    menu = MenuGUI()
    menu.ejecutar()