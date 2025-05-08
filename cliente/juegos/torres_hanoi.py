class TorresHanoi:
    def __init__(self, discos=3):
        self.discos = discos
        self.torres = [[i for i in range(discos, 0, -1)], [], []]
        self.movimientos = 0
        self.solucion_minima = (2 ** discos) - 1
        self.historial = []
    
    def mover_disco(self, origen, destino):
        if self.es_movimiento_valido(origen, destino):
            disco = self.torres[origen].pop()
            self.torres[destino].append(disco)
            self.movimientos += 1
            self.historial.append((origen, destino))
            return True
        return False
    
    def es_movimiento_valido(self, origen, destino):
        if origen < 0 or origen > 2 or destino < 0 or destino > 2:
            return False
        if not self.torres[origen]:
            return False
        if not self.torres[destino]:
            return True
        return self.torres[origen][-1] < self.torres[destino][-1]
    
    def esta_resuelto(self):
        return len(self.torres[2]) == self.discos
    
    def reiniciar(self):
        self.torres = [[i for i in range(self.discos, 0, -1)], [], []]
        self.movimientos = 0
        self.historial = []
    
    def resolver_automatico(self):
        self.reiniciar()
        self._resolver_recursivo(self.discos, 0, 2, 1)
    
    def _resolver_recursivo(self, n, origen, destino, auxiliar):
        if n == 0:
            return
        self._resolver_recursivo(n-1, origen, auxiliar, destino)
        self.mover_disco(origen, destino)
        self._resolver_recursivo(n-1, auxiliar, destino, origen)
    
    def deshacer_ultimo_movimiento(self):
        if self.historial:
            origen, destino = self.historial.pop()
            disco = self.torres[destino].pop()
            self.torres[origen].append(disco)
            self.movimientos -= 1
            return True
        return False