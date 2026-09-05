class HistorialAcciones:
    def __init__(self):
        """  Usamos una lista de Python para simular el comportamiento de la pila """
        self.pila = [] 

    def guardar_accion(self, accion):
        """ LIFO: Agrega el elemento a la cima de la pila """
        self.pila.append(accion)
        print(f"[+] Acción guardada: {accion} | Total en pila: {len(self.pila)}")

    def deshacer_accion(self):
        """  LIFO: Saca y devuelve el último elemento que entró """
        if len(self.pila) > 0:
            accion_deshecha = self.pila.pop()
            print(f"[-] Deshaciendo: {accion_deshecha} | Quedan: {len(self.pila)}")
            return accion_deshecha
        else:
            print("[!] No hay acciones para deshacer en el historial.")
            return None
        
        
