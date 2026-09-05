class BuscadorInventario:
    
    @staticmethod
    def buscar_por_nombre(lista_items, nombre_objetivo):
        """
        Búsqueda Lineal: Recorre la lista elemento por elemento 
        hasta encontrar el objeto exacto.
        """
        print(f"\n[?] Buscando el objeto: '{nombre_objetivo}'...")
        for item in lista_items:
            # Usamos .lower() para que no importe si se escribe con mayúsculas o minúsculas
            if item["nombre"].lower() == nombre_objetivo.lower():
                print(f"[+] ¡Objeto encontrado!: {item['nombre']} x{item['cantidad']}")
                return item
                
        print("[-] El objeto no está en el inventario.")
        return None

    @staticmethod
    def filtrar_por_categoria(lista_items, categoria_objetivo):
        """
        Filtro: Recorre la lista y extrae todos los elementos que 
        pertenezcan a una categoría específica.
        """
        print(f"\n[?] Filtrando por categoría: '{categoria_objetivo}'...")
        resultados = []
        for item in lista_items:
            if item["categoria"].lower() == categoria_objetivo.lower():
                resultados.append(item)
                
        if resultados:
            print(f"[+] Se encontraron {len(resultados)} objetos en esta categoría.")
        else:
            print("[-] No hay objetos de esta categoría.")
            
        return resultados