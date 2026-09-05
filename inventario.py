class Inventario:
    def __init__(self, capacidad_maxima=10):
        """ La estructura principal es una lista """
        self.items = []
        self.capacidad_maxima = capacidad_maxima

    def agregar_item(self, nombre, categoria, cantidad=1):
        """Agrega un objeto nuevo o suma la cantidad si ya existe."""
        
        # 1. Buscar si el objeto ya está en el inventario
        for item in self.items:
            if item["nombre"] == nombre:
                item["cantidad"] += cantidad
                print(f"[+] Se sumaron {cantidad} de {nombre}. Total: {item['cantidad']}")
                return True # Terminamos la función con éxito
                
        # 2. Si no existe, verificamos si hay espacio en la mochila
        if len(self.items) < self.capacidad_maxima:
            nuevo_item = {
                "nombre": nombre,
                "categoria": categoria,
                "cantidad": cantidad
            }
            self.items.append(nuevo_item)
            print(f"[+] Nuevo objeto recogido: {nombre} ({categoria})")
            return True
        else:
            print("[!] Tu inventario está lleno. No puedes cargar más objetos.")
            return False

    def mostrar_inventario(self):
        """Imprime el estado actual del inventario en la consola."""
        print("\n--- MOCHILA DEL JUGADOR ---")
        if not self.items:
            print("El inventario está vacío.")
        else:
            for item in self.items:
                print(f"- {item['nombre']} x{item['cantidad']} [{item['categoria']}]")
        print("---------------------------\n")
        
    def soltar_item(self, nombre, cantidad=1):
        """Elimina una cantidad específica de un objeto, o el objeto completo si llega a 0."""
        for item in self.items:
            if item["nombre"] == nombre:
                if item["cantidad"] > cantidad:
                    item["cantidad"] -= cantidad
                    print(f"[-] Soltaste {cantidad} de {nombre}. Quedan: {item['cantidad']}")
                else:
                    self.items.remove(item)
                    print(f"[-] Soltaste todos los {nombre}. El objeto fue removido de la mochila.")
                return True
                
        print(f"[!] No tienes '{nombre}' en tu inventario para soltar.")
        return False

    def usar_item(self, nombre):
        """Usa un objeto. Si es un consumible, reduce su cantidad."""
        for item in self.items:
            if item["nombre"] == nombre:
                print(f"[*] Has usado: {nombre}")
                # Si es un consumible (como una poción), se gasta al usarlo
                if item["categoria"].lower() == "consumible":
                    self.soltar_item(nombre, 1)
                return True
                
        print(f"[!] No puedes usar '{nombre}' porque no está en tu inventario.")
        return False
        
        
""" # --- PRUEBA AISLADA DEL MÓDULO ---
if __name__ == "__main__":
    mi_mochila = Inventario(capacidad_maxima=3)
    
    # Simulamos recoger cosas en el mapa
    mi_mochila.agregar_item("Poción de Salud", "Consumible", 1)
    mi_mochila.agregar_item("Espada de Hierro", "Arma", 1)
    mi_mochila.agregar_item("Poción de Salud", "Consumible", 2) # Debería apilarse
    
    mi_mochila.mostrar_inventario()
    
    # Llenamos la mochila
    mi_mochila.agregar_item("Cristal Mágico", "Material", 5)
    
    # Intentamos recoger un cuarto objeto diferente (debería dar error de espacio)
    mi_mochila.agregar_item("Escudo de Madera", "Armadura", 1) """