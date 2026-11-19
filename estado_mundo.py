class EstadoMundo:
    """Gestiona el estado dinámico del mundo mediante un diccionario seguro."""
    def __init__(self):
        self.datos = {
            "sala_actual": "Umbral de Piedra",
            "recompensa_acumulada": 0,
            "llave_lunar": False,
            "camara_makhai_bloqueada": True,
            "salas_visitadas": {"Umbral de Piedra"},
            "enemigos_derrotados": 0
        }

    def consultar(self, clave, defecto=None):
        """Consulta segura con .get() para evitar KeyError."""
        return self.datos.get(clave, defecto)

    def actualizar(self, clave, valor):
        """Inserta o actualiza una clave en el diccionario."""
        self.datos[clave] = valor

    def eliminar(self, clave):
        """Elimina una clave temporal de forma segura sin lanzar error si no existe."""
        return self.datos.pop(clave, None)

    def resumen_progreso(self):
        """Función propia 1: Resume las métricas principales del jugador."""
        visitadas = len(self.datos.get("salas_visitadas", set()))
        oro = self.datos.get("recompensa_acumulada", 0)
        enemigos = self.datos.get("enemigos_derrotados", 0)
        return (
            f"Sala: {self.datos.get('sala_actual')} | "
            f"Salas exploradas: {visitadas} | "
            f"Enemigos derrotados: {enemigos} | "
            f"Recompensa total: {oro}"
        )

    def filtrar_estados_activos(self):
        """Función propia 2: Filtra y devuelve solo las banderas booleanas activas (True)."""
        return [
            clave for clave, valor in self.datos.items()
            if isinstance(valor, bool) and valor is True
        ]