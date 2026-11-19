"""
Módulo: arboles.py
Proyecto: Awakening of Makhai - Checkpoint 3 / Base para Exposición
Descripción: Implementación de Árboles de Misiones (con dependencias y recursividad) 
y Árboles de Decisión para la inteligencia de los enemigos.
"""

class NodoMision:
    """Clase que representa un nodo en el Árbol de Misiones de Makhai."""
    def __init__(self, nombre, recompensa=50):
        self.nombre = nombre
        self.recompensa = recompensa
        self.hijos = []
        self.completada = False

    def agregar_hijo(self, hijo):
        """Agrega una misión dependiente (hijo) a esta misión."""
        self.hijos.append(hijo)

    def preorden(self, nivel=0):
        """Imprime el árbol en preorden con sangría visual según el nivel."""
        estado = "[X]" if self.completada else "[ ]"
        print("  " * nivel + f"- {estado} {self.nombre}")
        for hijo in self.hijos:
            hijo.preorden(nivel + 1)

    def altura(self):
        """Calcula la altura máxima del subárbol de misiones recursivamente."""
        if not self.hijos:
            return 0
        return 1 + max(hijo.altura() for hijo in self.hijos)

    def contar_hojas(self):
        """Cuenta el total de misiones finales (hojas) en el árbol."""
        if not self.hijos:
            return 1
        return sum(hijo.contar_hojas() for hijo in self.hijos)

    def misiones_disponibles(self, padre_completado=True, lista=None):
        """
        Retorna una lista con los nombres de las misiones que están disponibles 
        (no completadas y cuyo padre directo ya fue completado).
        """
        if lista is None:
            lista = []
        
        if padre_completado and not self.completada:
            lista.append(self.nombre)
        
        # Las misiones hijas solo se evalúan si este padre ya está completado
        siguiente_padre_completado = self.completada
        for hijo in self.hijos:
            hijo.misiones_disponibles(siguiente_padre_completado, lista)
            
        return lista

    def completar_mision(self, nombre_mision, padre_completado=True):
        """
        Busca y completa una misión de forma recursiva. 
        Rechaza la acción si la misión está bloqueada (su padre no está completado).
        """
        if self.nombre == nombre_mision:
            if not padre_completado:
                print(f"[!] ERROR: La misión '{self.nombre}' está BLOQUEADA. Debes completar su misión predecesora primero.")
                return False
            if self.completada:
                print(f"[i] Aviso: La misión '{self.nombre}' ya había sido completada anteriormente.")
                return True
            self.completada = True
            print(f"[+] ¡ÉXITO! Misión completada: '{self.nombre}'")
            return True
        
        for hijo in self.hijos:
            if hijo.completar_mision(nombre_mision, self.completada):
                return True
        return False
    
    def postorden_recompensas(self):
        """
        Recorrido en POSTORDEN: suma primero las recompensas de todas las misiones hijas
        y al final suma la recompensa del nodo actual.
        """
        total = 0
        for hijo in self.hijos:
            total += hijo.postorden_recompensas()
        return total + self.recompensa

    def recorrido_por_niveles(self):
        """
        Recorrido POR NIVELES (BFS): agrupa y muestra las misiones según su etapa/nivel.
        """
        cola = [(self, 0)]
        etapas = {}
        while cola:
            actual, nivel = cola.pop(0)
            etapas.setdefault(nivel, []).append(actual.nombre)
            for hijo in actual.hijos:
                cola.append((hijo, nivel + 1))
        return etapas


class NodoDecision:
    """Clase que representa un nodo en el Árbol de Decisión de un enemigo/IA."""
    def __init__(self, pregunta=None, decision=None):
        self.pregunta = pregunta    # Si es nodo interno (pregunta de sí/no)
        self.decision = decision    # Si es nodo hoja (acción final)
        self.izq = None             # Rama para respuesta Sí (True)
        self.der = None             # Rama para respuesta No (False)


def decidir(nodo, situacion):
    """
    Recorre el árbol de decisión de forma recursiva evaluando un diccionario de situación
    hasta llegar a una hoja de acción.
    """
    if nodo.decision is not None:
        return nodo.decision
    
    # Evalúa la condición actual en el diccionario de estado del juego
    condicion = situacion.get(nodo.pregunta, False)
    if condicion:
        return decidir(nodo.izq, situacion)
    else:
        return decidir(nodo.der, situacion)


def construir_arbol_misiones():
    """Construye el árbol de misiones de Awakening of Makhai (8 misiones, 3 niveles)."""
    # Nivel 0 (Raíz)
    raiz = NodoMision("1. Despertar en el Umbral de Piedra")
    
    # Nivel 1 (Hijos de la raíz)
    mision_forja = NodoMision("2. Forjar la Hoja de Obsidiana")
    mision_amuleto = NodoMision("3. Recuperar el Amuleto de Jarek")
    raiz.agregar_hijo(mision_forja)
    raiz.agregar_hijo(mision_amuleto)
    
    # Nivel 2 (Hijos de Forja y Amuleto)
    mision_runas = NodoMision("4. Inscribir Runas de Poder")
    mision_acero = NodoMision("5. Templar el Acero Lunar")
    mision_puente = NodoMision("6. Derrotar al Guardián del Puente")
    mision_pergamino = NodoMision("7. Descifrar el Pergamino Ancestral")
    
    mision_forja.agregar_hijo(mision_runas)
    mision_forja.agregar_hijo(mision_acero)
    mision_amuleto.agregar_hijo(mision_puente)
    mision_amuleto.agregar_hijo(mision_pergamino)
    
    # Nivel 3 (Hijo final para completar los 3 niveles y 8 misiones)
    mision_jefe = NodoMision("8. Confrontar al Señor de Makhai")
    mision_acero.agregar_hijo(mision_jefe)
    
    return raiz


def construir_arbol_decision():
    """Construye el árbol de decisión de un enemigo con 3 preguntas y 4 hojas."""
    # Pregunta 1 (Raíz)
    raiz = NodoDecision(pregunta="jugador_cerca")
    
    # Pregunta 2 (Rama Sí de Jugador Cerca)
    nodo_vida = NodoDecision(pregunta="vida_baja")
    raiz.izq = nodo_vida  # Si jugador_cerca == True
    
    # Hojas de Pregunta 2
    nodo_vida.izq = NodoDecision(decision="Huir y buscar cobertura")      # Si vida_baja == True
    nodo_vida.der = NodoDecision(decision="Ejecutar Ataque Especial")     # Si vida_baja == False
    
    # Pregunta 3 (Rama No de Jugador Cerca)
    nodo_alerta = NodoDecision(pregunta="jefe_alerta")
    raiz.der = nodo_alerta # Si jugador_cerca == False
    
    # Hojas de Pregunta 3
    nodo_alerta.izq = NodoDecision(decision="Lanzar proyectil mágico a distancia") # Si jefe_alerta == True
    nodo_alerta.der = NodoDecision(decision="Patrullar zona y mantener guardia")    # Si jefe_alerta == False
    
    return raiz


def main():
    print("==================================================")
    print("   DEMO EN VIVO: AWAKENING OF MAKHAI - ÁRBOLES    ")
    print("==================================================\n")
    
    # 1. PRUEBA DEL ÁRBOL DE MISIONES
    print("--- [1] ÁRBOL DE MISIONES (Estructura Inicial) ---")
    arbol_misiones = construir_arbol_misiones()
    arbol_misiones.preorden()
    print(f"\nAltura del árbol: {arbol_misiones.altura()}")
    print(f"Total de misiones finales (hojas): {arbol_misiones.contar_hojas()}")
    print(f"Misiones disponibles inicialmente: {arbol_misiones.misiones_disponibles()}\n")
    
    print("--- [2] PROBANDO BLOQUEO DE MISIONES ---")
    # Intentar completar una misión hija avanzada sin haber completado su padre
    arbol_misiones.completar_mision("4. Inscribir Runas de Poder")
    
    print("\n--- [3] COMPLETANDO MISIONES EN VIVO ---")
    arbol_misiones.completar_mision("1. Despertar en el Umbral de Piedra")
    arbol_misiones.completar_mision("2. Forjar la Hoja de Obsidiana")
    
    print(f"\nMisiones disponibles ahora: {arbol_misiones.misiones_disponibles()}")
    
    print("\nÁrbol actualizado tras completar misiones:")
    arbol_misiones.preorden()
    
    print("\n==================================================")
    
    # 2. PRUEBA DEL ÁRBOL DE DECISIÓN DEL ENEMIGO
    print("--- [4] ÁRBOL DE DECISIÓN DEL ENEMIGO ---")
    ia_enemiga = construir_arbol_decision()
    
    # Situación 1: El jugador está cerca y el enemigo tiene vida baja
    sit_1 = {"jugador_cerca": True, "vida_baja": True}
    res_1 = decidir(ia_enemiga, sit_1)
    print(f"Situación 1 {sit_1} -> Decisión IA: '{res_1}'")
    
    # Situación 2: El jugador está cerca pero el enemigo tiene buena salud
    sit_2 = {"jugador_cerca": True, "vida_baja": False}
    res_2 = decidir(ia_enemiga, sit_2)
    print(f"Situación 2 {sit_2} -> Decisión IA: '{res_2}'")
    
    # Situación 3: El jugador está lejos pero el enemigo está en alerta
    sit_3 = {"jugador_cerca": False, "jefe_alerta": True}
    res_3 = decidir(ia_enemiga, sit_3)
    print(f"Situación 3 {sit_3} -> Decisión IA: '{res_3}'")

    # Situación 4: El jugador está lejos y el enemigo está tranquilo
    sit_4 = {"jugador_cerca": False, "jefe_alerta": False}
    res_4 = decidir(ia_enemiga, sit_4)
    print(f"Situación 4 {sit_4} -> Decisión IA: '{res_4}'")
    print("==================================================")


if __name__ == "__main__":
    main()