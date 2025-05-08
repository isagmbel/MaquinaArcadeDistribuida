class NReinas:
    def __init__(self, tamaño=8):
        self.tamaño = tamaño
        self.tablero = [[0] * tamaño for _ in range(tamaño)]
        self.soluciones = []
    
    def es_seguro(self, fila, col):
        # Verifica la fila hacia la izquierda
        for i in range(col):
            if self.tablero[fila][i] == 1:
                return False
        
        # Verifica la diagonal superior izquierda
        for i, j in zip(range(fila, -1, -1), range(col, -1, -1)):
            if self.tablero[i][j] == 1:
                return False
        
        # Verifica la diagonal inferior izquierda
        for i, j in zip(range(fila, self.tamaño, 1), range(col, -1, -1)):
            if self.tablero[i][j] == 1:
                return False
        
        return True
    
    def resolver(self, col=0):
        if col >= self.tamaño:
            # Guardamos una copia de la solución actual
            self.soluciones.append([fila[:] for fila in self.tablero])
            return True
        
        res = False
        for i in range(self.tamaño):
            if self.es_seguro(i, col):
                self.tablero[i][col] = 1
                res = self.resolver(col + 1) or res
                self.tablero[i][col] = 0  # Backtrack
        
        return res
    
    def obtener_soluciones(self):
        self.soluciones = []
        self.resolver()
        return self.soluciones
    
    def reiniciar(self):
        self.tablero = [[0] * self.tamaño for _ in range(self.tamaño)]
        self.soluciones = []
    
    def colocar_reina(self, fila, columna):
        if self.es_seguro(fila, columna):
            self.tablero[fila][columna] = 1
            return True
        return False
    
    def es_solucion(self):
        # Verifica que haya exactamente N reinas
        reinas = sum(sum(fila) for fila in self.tablero)
        if reinas != self.tamaño:
            return False
        
        # Verifica que no haya conflictos
        posiciones = [(fila, col) for fila in range(self.tamaño) 
                     for col in range(self.tamaño) if self.tablero[fila][col] == 1]
        
        for i in range(len(posiciones)):
            for j in range(i + 1, len(posiciones)):
                fila1, col1 = posiciones[i]
                fila2, col2 = posiciones[j]
                
                # Misma fila o misma columna
                if fila1 == fila2 or col1 == col2:
                    return False
                # Misma diagonal
                if abs(fila1 - fila2) == abs(col1 - col2):
                    return False
        
        return True