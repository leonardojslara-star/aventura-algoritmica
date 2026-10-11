"""Módulo de historial de acciones utilizando una Pila (LIFO) - Semana 5 / Guía 5."""

class HistorialAcciones:
    def __init__(self):
        """Inicializa la pila del historial como una lista vacía."""
        self.pila = []

    def guardar_accion(self, tipo, descripcion, sala_origen, pos_origen=(400, 300)):
        """LIFO: Registra una acción importante en el tope de la pila con append()."""
        accion = {
            "tipo": tipo,
            "descripcion": descripcion,
            "sala_origen": sala_origen,
            "pos_origen": pos_origen
        }
        self.pila.append(accion)
        print(f"[+] Historial (append): [{tipo.upper()}] {descripcion} (Desde: {sala_origen}) | Total en pila: {len(self.pila)}")

    def deshacer_accion(self):
        """LIFO: Extrae y devuelve la última acción con pop(). Maneja el caso límite de pila vacía."""
        if len(self.pila) > 0:
            accion_deshecha = self.pila.pop()
            print(f"[-] Deshaciendo (pop): {accion_deshecha['descripcion']} -> Volviendo a '{accion_deshecha['sala_origen']}'")
            return accion_deshecha
        else:
            print("[!] Caso límite: No hay movimientos que deshacer, el historial está vacío.")
            return None

    def consultar_ultima(self):
        """Consulta la última acción registrada sin sacarla de la pila (peek)."""
        if len(self.pila) > 0:
            ultima = self.pila[-1]
            print(f"[?] Última acción en cima: [{ultima['tipo'].upper()}] {ultima['descripcion']}")
            return ultima
        else:
            print("[!] Caso límite: El historial está vacío, no hay última acción para consultar.")
            return None

    def mostrar_historial(self):
        """Muestra el historial completo desde la acción más reciente hasta la más antigua."""
        print("\n--- 📜 HISTORIAL DE ACCIONES (Más reciente -> Más antigua) ---")
        if not self.pila:
            print("El historial está vacío.")
        else:
            for i in range(len(self.pila) - 1, -1, -1):
                acc = self.pila[i]
                print(f"  {len(self.pila) - i}. [{acc['tipo'].upper()}] {acc['descripcion']} (Origen: {acc['sala_origen']})")
        print("--------------------------------------------------------------\n")

    # --- 2 FUNCIONES ADAPTADAS DE LA GUÍA 5 ---
    def contar_acciones_de_tipo(self, tipo_buscado):
        """Cuenta cuántas acciones de un tipo específico ('movimiento', 'recoger', 'usar', 'soltar') hay en la pila."""
        total = sum(1 for acc in self.pila if acc["tipo"].lower() == tipo_buscado.lower())
        print(f"[#] Total de acciones de tipo '{tipo_buscado}': {total}")
        return total

    def deshacer_multiples(self, cantidad):
        """Deshace N acciones seguidas de forma segura validando casos límite."""
        if cantidad <= 0:
            print("[!] Caso límite: La cantidad a deshacer debe ser un número positivo mayor a 0.")
            return []
        
        acciones_deshechas = []
        print(f"[*] Intentando deshacer {cantidad} acción(es)...")
        for _ in range(cantidad):
            if not self.pila:
                print("[!] El historial quedó vacío antes de completar todas las deshechas.")
                break
            acciones_deshechas.append(self.deshacer_accion())
        return acciones_deshechas