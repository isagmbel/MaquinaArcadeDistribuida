import time

class RecorridoCaballo:
    def __init__(self, tamaño=8):
        self.tamaño = tamaño
        self.tablero = [[-1 for _ in range(tamaño)] for _ in range(tamaño)]
        self.movimientos = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        self.soluciones = []
        self.tiempo_limite = 2.0  # Segundos máximos para buscar soluciones
        self.max_soluciones = 10  # Número máximo de soluciones a encontrar
    
    def es_valido(self, x, y):
        return 0 <= x < self.tamaño and 0 <= y < self.tamaño and self.tablero[x][y] == -1
    
    def contar_salidas(self, x, y):
        """Cuenta el número de movimientos posibles desde una posición."""
        count = 0
        for dx, dy in self.movimientos:
            nx, ny = x + dx, y + dy
            if self.es_valido(nx, ny):
                count += 1
        return count
    
    def resolver(self, x=0, y=0, movimiento=1, tiempo_inicio=None):
        if tiempo_inicio is None:
            tiempo_inicio = time.time()
        
        # Verificar límite de tiempo
        if time.time() - tiempo_inicio > self.tiempo_limite:
            return True
            
        # Verificar límite de soluciones
        if len(self.soluciones) >= self.max_soluciones:
            return True
            
        self.tablero[x][y] = movimiento
        
        if movimiento == self.tamaño * self.tamaño:
            # Encontramos una solución
            self.soluciones.append([fila[:] for fila in self.tablero])
            self.tablero[x][y] = -1
            return len(self.soluciones) >= self.max_soluciones
        
        # Aplicar heurística de Warnsdorff
        # Ordenar los movimientos por el número de salidas (menos salidas primero)
        movimientos_ordenados = []
        for dx, dy in self.movimientos:
            nx, ny = x + dx, y + dy
            if self.es_valido(nx, ny):
                salidas = self.contar_salidas(nx, ny)
                movimientos_ordenados.append((salidas, nx, ny))
        
        # Ordenar por número de salidas (menor primero)
        movimientos_ordenados.sort()
        
        for _, nx, ny in movimientos_ordenados:
            if self.resolver(nx, ny, movimiento + 1, tiempo_inicio):
                # Para acelerar: retornamos True si ya tenemos suficientes soluciones
                if len(self.soluciones) >= self.max_soluciones:
                    self.tablero[x][y] = -1
                    return True
        
        self.tablero[x][y] = -1
        return False
    
    def encontrar_soluciones(self):
        self.soluciones = []
        tiempo_inicio = time.time()
        
        # Si el tamaño es mayor a 5x5, limitemos a una sola solución para ser más eficiente
        if self.tamaño > 5:
            self.max_soluciones = 1
        
        # Probar desde diferentes posiciones iniciales
        if not self.soluciones:
            for i in range(min(4, self.tamaño)):
                for j in range(min(4, self.tamaño)):
                    self.reiniciar()
                    self.resolver(i, j, 1, tiempo_inicio)
                    if self.soluciones:
                        break
                if self.soluciones:
                    break
        
        return self.soluciones
    
    def reiniciar(self):
        self.tablero = [[-1 for _ in range(self.tamaño)] for _ in range(self.tamaño)]
    
    def mover_caballo(self, x, y, paso):
        if self.es_valido(x, y):
            self.tablero[x][y] = paso
            return True
        return False
    
    def es_solucion_valida(self):
        # Verificar que todos los pasos del 1 al tamaño² estén presentes
        pasos = set()
        for fila in self.tablero:
            for valor in fila:
                if valor != -1:
                    pasos.add(valor)
        
        if len(pasos) != self.tamaño * self.tamaño:
            return False
        
        # Verificar que los movimientos sean válidos
        posiciones = {}
        for i in range(self.tamaño):
            for j in range(self.tamaño):
                if self.tablero[i][j] != -1:
                    posiciones[self.tablero[i][j]] = (i, j)
        
        for paso in range(1, self.tamaño * self.tamaño):
            x1, y1 = posiciones[paso]
            x2, y2 = posiciones[paso + 1]
            dx, dy = abs(x1 - x2), abs(y1 - y2)
            if (dx, dy) not in [(1, 2), (2, 1)]:
                return False
        
        return True