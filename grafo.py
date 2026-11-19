from collections import deque

class Grafo:
    """Implementación genérica de un grafo mediante lista de adyacencia."""
    def __init__(self, dirigido=False):
        self.adyacencia = {}
        self.dirigido = dirigido

    def agregar_vertice(self, vertice):
        if vertice not in self.adyacencia:
            self.adyacencia[vertice] = []

    def agregar_arista(self, origen, destino):
        self.agregar_vertice(origen)
        self.agregar_vertice(destino)
        if destino not in self.adyacencia[origen]:
            self.adyacencia[origen].append(destino)
        if not self.dirigido and origen not in self.adyacencia[destino]:
            self.adyacencia[destino].append(origen)

    def bfs_ruta_corta(self, inicio, destino, bloqueados=None):
        """
        Encuentra la ruta con menos saltos (BFS) entre dos salas,
        evitando salas bloqueadas según el estado del mundo.
        """
        if bloqueados is None:
            bloqueados = set()
        if inicio not in self.adyacencia or destino not in self.adyacencia:
            return []
        if inicio in bloqueados or destino in bloqueados:
            return []

        visitados = {inicio}
        cola = deque([(inicio, [inicio])])

        while cola:
            actual, camino = cola.popleft()
            if actual == destino:
                return camino
            for vecino in self.adyacencia.get(actual, []):
                if vecino not in visitados and vecino not in bloqueados:
                    visitados.add(vecino)
                    cola.append((vecino, camino + [vecino]))
        return []

    def dfs_zonas_alcanzables(self, inicio, bloqueados=None, visitados=None):
        """
        Explora en profundidad (DFS) todas las zonas a las que Makhai
        puede llegar actualmente sin atravesar puertas cerradas.
        """
        if bloqueados is None:
            bloqueados = set()
        if visitados is None:
            visitados = set()

        if inicio not in self.adyacencia or inicio in bloqueados:
            return visitados

        visitados.add(inicio)
        for vecino in self.adyacencia.get(inicio, []):
            if vecino not in visitados and vecino not in bloqueados:
                self.dfs_zonas_alcanzables(vecino, bloqueados, visitados)
        return visitados


def construir_mapa_makhai():
    """Construye la red de salas de Awakening of Makhai."""
    mapa = Grafo(dirigido=False)
    mapa.agregar_arista("Umbral de Piedra", "Forja de Obsidiana")
    mapa.agregar_arista("Umbral de Piedra", "Puente Antiguo")
    mapa.agregar_arista("Forja de Obsidiana", "Santuario Lunar")
    mapa.agregar_arista("Puente Antiguo", "Santuario Lunar")
    mapa.agregar_arista("Santuario Lunar", "Cámara de Makhai")
    return mapa