"""Módulo de generación recursiva de la mazmorra - Semana 7 / Guía 7."""

# Nombres propios basados en el lore de Awakening of Makhai (7 salas para profundidad 2)
NOMBRES_SALAS_MAKHAI = [
    "Sala de Inicio: Umbral de Piedra",     # Nivel 0 (Raíz)
    "Pasillo de los Faroles Caídos",        # Nivel 1 - Rama Izquierda
    "Galería de las Estatuas Antiguas",     # Nivel 1 - Rama Derecha
    "Cámara del Eco de Jarek",              # Nivel 2 - Hoja 1
    "Santuario del Cuarzo Roto",            # Nivel 2 - Hoja 2
    "Forja de las Sombras",                 # Nivel 2 - Hoja 3
    "Altar del Despertar de Makhai"         # Nivel 2 - Hoja 4
]

OBJETOS_SALAS_PROFUNDAS = [
    ("Corazón de Cuarzo Roto", "Objeto Clave"),
    ("Poción de Salud Ancestral", "Consumible"),
    ("Espada de Cuarzo", "Arma"),
    ("Llave de las Sombras", "Objeto Clave")
]

def generar_mazmorra_recursiva(nivel_actual, profundidad_maxima, iter_nombres):
    """
    Genera recursivamente la mazmorra como un árbol de salas conectadas.
    - Caso base: cuando nivel_actual > profundidad_maxima, retorna None y detiene la recursión.
    - Caso recursivo: crea la sala actual y se llama a sí misma para generar las salas hijas (nivel_actual + 1).
    """
    # 1. CASO BASE
    if nivel_actual > profundidad_maxima:
        return None

    nombre = next(iter_nombres, f"Sala Misteriosa Nivel {nivel_actual}")
    nueva_sala = {
        "nombre": nombre,
        "nivel": nivel_actual,
        "item": None,          # Se llenará en las salas más profundas
        "jefe": False,
        "conexiones": []       # Lista de salas hijas conectadas
    }

    # 2. CASO RECURSIVO: Ramificación de 2 caminos por sala (crea 1 + 2 + 4 = 7 salas en profundidad 2)
    sala_izquierda = generar_mazmorra_recursiva(nivel_actual + 1, profundidad_maxima, iter_nombres)
    sala_derecha = generar_mazmorra_recursiva(nivel_actual + 1, profundidad_maxima, iter_nombres)

    if sala_izquierda is not None:
        nueva_sala["conexiones"].append(sala_izquierda)
    if sala_derecha is not None:
        nueva_sala["conexiones"].append(sala_derecha)

    return nueva_sala

# --- 2 ADAPTACIONES DE LA GUÍA 7 ---
def marcar_salas_profundas(nodo_sala, profundidad_objetivo, iter_objetos):
    """
    Adaptación 1 (Guía 7): Recorre recursivamente la mazmorra y marca las salas más profundas
    colocando tesoros/objetos del inventario y designando la sala del jefe.
    """
    if nodo_sala is None:
        return

    if nodo_sala["nivel"] == profundidad_objetivo:
        datos_item = next(iter_objetos, ("Fragmento de Cuarzo", "Material"))
        nodo_sala["item"] = {"nombre": datos_item[0], "categoria": datos_item[1], "cantidad": 1}
        if "Altar" in nodo_sala["nombre"]:
            nodo_sala["jefe"] = True

    for sala_hija in nodo_sala["conexiones"]:
        marcar_salas_profundas(sala_hija, profundidad_objetivo, iter_objetos)

def contar_salas_por_nivel(nodo_sala, conteo=None):
    """
    Adaptación 2 (Guía 7): Cuenta recursivamente cuántas salas existen en cada nivel de profundidad.
    """
    if conteo is None:
        conteo = {}
    if nodo_sala is None:
        return conteo

    nivel = nodo_sala["nivel"]
    conteo[nivel] = conteo.get(nivel, 0) + 1

    for sala_hija in nodo_sala["conexiones"]:
        contar_salas_por_nivel(sala_hija, conteo)

    return conteo

def calcular_profundidad_real(nodo_sala):
    """Adaptación extra (Guía 7): Calcula recursivamente la profundidad máxima real alcanzada."""
    if nodo_sala is None or not nodo_sala["conexiones"]:
        return 0
    return 1 + max(calcular_profundidad_real(hija) for hija in nodo_sala["conexiones"])

def mostrar_arbol_mazmorra(nodo_sala, sangria=""):
    """Imprime en consola el árbol jerárquico de la mazmorra con sangría."""
    if nodo_sala is None:
        return
    extra = ""
    if nodo_sala["item"]:
        extra += f" [🎁 Item: {nodo_sala['item']['nombre']}]"
    if nodo_sala["jefe"]:
        extra += " [💀 JEFE]"
    print(f"{sangria}└── {nodo_sala['nombre']} (Nivel {nodo_sala['nivel']}){extra}")
    for hija in nodo_sala["conexiones"]:
        mostrar_arbol_mazmorra(hija, sangria + "    ")