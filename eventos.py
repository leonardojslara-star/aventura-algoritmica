class ColaEventos:
    def __init__(self):
        self.cola = []

    def agregar_evento(self, tipo_evento, datos):
        nuevo_evento = {"tipo": tipo_evento, "datos": datos}
        self.cola.append(nuevo_evento)
        
    def procesar_eventos(self):
        """Saca todos los eventos pendientes y los devuelve en orden (FIFO)."""
        eventos_a_resolver = []
        while len(self.cola) > 0:
            # pop(0) saca el evento más antiguo de la fila
            eventos_a_resolver.append(self.cola.pop(0))
            
        return eventos_a_resolver