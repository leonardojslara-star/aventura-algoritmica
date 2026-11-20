"""
Archivo central de Aventura Algorítmica (Awakening of Makhai) - Checkpoint 3.
Integra Inventario (Listas), Historial (Pila LIFO), Eventos/Turnos (Cola FIFO),
Mazmorra (Recursividad), Grafo (BFS/DFS), Árboles (Preorden/Postorden/Niveles) y Diccionario (Estado).
"""
import pygame
import sys
import textwrap
from historial import HistorialAcciones
from inventario import Inventario
from buscador import BuscadorInventario
from eventos import ColaEventos
from jugador import Jugador
import mazmorra as maz
from arboles import construir_arbol_misiones
from grafo import construir_mapa_makhai
from estado_mundo import EstadoMundo


def pedir_opcion_consola(mensaje, minimo, maximo):
    """
    Valida la entrada del usuario en consola manejando casos límite:
    texto no numérico, 0, números negativos y números fuera de rango.
    """
    while True:
        entrada = input(mensaje).strip()
        try:
            opcion = int(entrada)
            if minimo <= opcion <= maximo:
                return opcion
            else:
                print(f"[!] Opción no válida. Elige un número entre {minimo} y {maximo}.")
        except ValueError:
            print("[!] Entrada inválida: debes ingresar un número entero, no texto.")


class Juego:
    def __init__(self):
        """Inicializa Pygame, las estructuras de datos del Checkpoint 2 y 3 y las entidades del juego."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Awakening of Makhai - Checkpoint 3")
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # --- 1. ESTRUCTURAS DE DATOS (CHECKPOINT 1, 2 Y 3) ---
        self.historial = HistorialAcciones()
        self.mochila = Inventario(capacidad_maxima=10)
        self.gestor_eventos = ColaEventos()

        self.mapa = construir_mapa_makhai()
        self.arbol_misiones = construir_arbol_misiones()
        self.estado_mundo = EstadoMundo()
        self.pila_deshacer = []  # Pila para revertir acciones en el grafo y estado del mundo

        # Variables para el HUD interactivo y alertas de casos límite en pantalla
        self.mostrar_hud_estructuras = False
        self.mensaje_alerta = "Presiona [TAB] para ver Mapa (Grafo), Misiones (Árbol) y Estado"
        self.color_alerta = (220, 220, 220)
        self.fuente_hud = pygame.font.SysFont("consolas", 16)
        self.fuente_titulo = pygame.font.SysFont("consolas", 18, bold=True)

        # Generación recursiva de la mazmorra (Profundidad 2 = 7 salas)
        iter_nombres = iter(maz.NOMBRES_SALAS_MAKHAI)
        iter_objetos = iter(maz.OBJETOS_SALAS_PROFUNDAS)
        self.profundidad_max = 2
        self.raiz_mazmorra = maz.generar_mazmorra_recursiva(0, self.profundidad_max, iter_nombres)

        # Adaptaciones de la Guía 7 al iniciar
        maz.marcar_salas_profundas(self.raiz_mazmorra, self.profundidad_max, iter_objetos)
        self.conteo_niveles = maz.contar_salas_por_nivel(self.raiz_mazmorra)
        self.total_salas = sum(self.conteo_niveles.values())

        # Diccionario auxiliar para buscar referencias de salas por nombre al hacer backtracking
        self.registro_salas = {}
        self._indexar_salas(self.raiz_mazmorra)
        self.sala_actual = self.raiz_mazmorra

        # Mensajes de inicio en consola
        print("\n=== Awakening of Makhai: La Cripta del Cuarzo ===")
        print(f"Mazmorra generada: {self.total_salas} salas, profundidad {maz.calcular_profundidad_real(self.raiz_mazmorra)}")
        print(f"Salas por nivel: {self.conteo_niveles}")
        print(f"Estás en: {self.sala_actual['nombre']}")
        print("Controles Pygame: [WASD] Mover | [1/2] Mazmorra | [BACKSPACE] Deshacer Mazmorra | [TAB] Panel Estructuras | [F1-F5] Grafo BFS | [C] Misión | [B] Bloqueo/Buscar | [U] Deshacer Mundo | [M] Consola\n")

        # --- 2. JUGADOR Y COMBATE EN PYGAME ---
        self.jugador = Jugador(150, 260)
        self.jugador.velocidad = 5

        self.enemigo_x = 600
        self.enemigo_y = 280
        self.enemigo_tamano = 48
        self.enemigo_hp = 100
        self.enemigo_vivo = True

        # --- 3. INTERFAZ GRÁFICA (HUD) ---
        pygame.font.init()
        self.fuente = pygame.font.SysFont("Arial", 20, bold=True)
        self.fuente_pequena = pygame.font.SysFont("Arial", 16)
        self.inventario_abierto = False
        self.ultimo_mensaje_evento = "Explora la mazmorra. Presiona [1] o [2] para avanzar de sala."
        self.turno_en_pantalla = self.gestor_eventos.cola_turnos[0]

    def mostrar_notificacion(self, texto, es_error=False):
        """Muestra avisos en pantalla y consola sin detener Pygame (manejo de casos límite)."""
        self.mensaje_alerta = texto
        self.color_alerta = (255, 95, 95) if es_error else (110, 240, 150)
        print(texto)

    def viajar_region_grafo(self, sala_destino):
        """
        Conecta Grafo (BFS) + Diccionario (Estado) + Árbol (Misiones) + Pila (Deshacer).
        """
        sala_actual = self.estado_mundo.consultar("sala_actual")
        if sala_destino == sala_actual:
            self.mostrar_notificacion(f"[i] Ya te encuentras en '{sala_actual}'.", es_error=True)
            return

        bloqueados = {"Cámara de Makhai"} if self.estado_mundo.consultar("camara_makhai_bloqueada", True) else set()
        ruta = self.mapa.bfs_ruta_corta(sala_actual, sala_destino, bloqueados)

        # Caso límite: sala inexistente o puerta bloqueada
        if not ruta:
            self.mostrar_notificacion(f"[!] Acceso denegado a '{sala_destino}': sala bloqueada o sin ruta.", es_error=True)
            return

        # Guardar snapshot en la pila del Checkpoint 2 antes de cambiar el estado
        self.pila_deshacer.append({
            "sala": sala_actual,
            "recompensa": self.estado_mundo.consultar("recompensa_acumulada", 0),
            "llave_lunar": self.estado_mundo.consultar("llave_lunar", False),
            "bloqueada": self.estado_mundo.consultar("camara_makhai_bloqueada", True)
        })

        # Actualizar diccionario de estado del mundo
        self.estado_mundo.actualizar("sala_actual", sala_destino)
        self.estado_mundo.consultar("salas_visitadas", set()).add(sala_destino)

        # Impacto cruzado entre salas del grafo y nodos del árbol de misiones
        if sala_destino == "Forja de Obsidiana":
            # INSERCIÓN de clave temporal en el diccionario
            self.estado_mundo.actualizar("buff_forja", True)
            if self.arbol_misiones.completar_mision("1. Despertar en el Umbral de Piedra"):
                oro = self.estado_mundo.consultar("recompensa_acumulada", 0) + 50
                self.estado_mundo.actualizar("recompensa_acumulada", oro)
                self.mostrar_notificacion(f"[+] Ruta BFS: {' -> '.join(ruta)} | ¡Misión 1 completada (+50 oro) y Buff de Forja obtenido!")
                return
        elif sala_destino == "Santuario Lunar":
            # ELIMINACIÓN de clave temporal del diccionario al consumir el buff
            tenia_buff = self.estado_mundo.eliminar("buff_forja")
            self.estado_mundo.actualizar("llave_lunar", True)
            self.estado_mundo.actualizar("camara_makhai_bloqueada", False)
            extra = " (Buff de Forja consumido)" if tenia_buff else ""
            self.mostrar_notificacion(f"[+] ¡Llave Lunar obtenida{extra}! Cámara de Makhai desbloqueada.")
            return

        self.mostrar_notificacion(f"[+] Viajaste por ruta BFS: {' -> '.join(ruta)}")

    def intentar_completar_siguiente_mision(self):
        """Completa la primera misión disponible o prueba el bloqueo si se intenta saltar etapas."""
        disponibles = self.arbol_misiones.misiones_disponibles()
        if not disponibles:
            self.mostrar_notificacion("[i] Todas las misiones del árbol están completadas.")
            return

        mision_objetivo = disponibles[0]
        if self.arbol_misiones.completar_mision(mision_objetivo):
            oro = self.estado_mundo.consultar("recompensa_acumulada", 0) + 50
            self.estado_mundo.actualizar("recompensa_acumulada", oro)
            self.mostrar_notificacion(f"[+] Misión completada: {mision_objetivo} (+50 oro)")

    def deshacer_accion_mundo(self):
        """Revierte el último movimiento en el grafo usando la pila de estados."""
        if not self.pila_deshacer:
            self.mostrar_notificacion("[i] Pila vacía: no hay movimientos recientes para deshacer.", es_error=True)
            return

        anterior = self.pila_deshacer.pop()
        self.estado_mundo.actualizar("sala_actual", anterior["sala"])
        self.estado_mundo.actualizar("recompensa_acumulada", anterior["recompensa"])
        self.estado_mundo.actualizar("llave_lunar", anterior["llave_lunar"])
        self.estado_mundo.actualizar("camara_makhai_bloqueada", anterior["bloqueada"])
        self.mostrar_notificacion(f"[<-] Deshacer: regresaste a '{anterior['sala']}'.")

    def _indexar_salas(self, nodo):
        """Guarda cada nodo del árbol en un diccionario para acceso rápido durante el backtracking."""
        if nodo is not None:
            self.registro_salas[nodo["nombre"]] = nodo
            for hija in nodo["conexiones"]:
                self._indexar_salas(hija)

    def viajar_a_sala(self, indice_conexion):
        """Mueve al jugador a una sala conectada de la mazmorra recursiva, registra en la pila y procesa un evento."""
        conexiones = self.sala_actual["conexiones"]
        if not conexiones:
            print("[!] Caso límite: Esta sala es el fondo de la rama, no hay más salas hacia adelante. ¡Usa Deshacer (BACKSPACE)!")
            self.ultimo_mensaje_evento = "Sin salida adelante. ¡Usa BACKSPACE para retroceder!"
            return

        if indice_conexion < 0 or indice_conexion >= len(conexiones):
            print(f"[!] Caso límite: Sala no conectada. Elige un índice válido entre 1 y {len(conexiones)}.")
            return

        nueva_sala = conexiones[indice_conexion]

        # 1. Registrar acción en la Pila guardando sala y coordenadas actuales
        self.historial.guardar_accion(
            "movimiento",
            f"Avanzó a '{nueva_sala['nombre']}'",
            self.sala_actual["nombre"],
            (self.jugador.x, self.jugador.y)
        )

        # 2. Cambiar de sala y posicionar a Makhai en la entrada izquierda
        self.sala_actual = nueva_sala
        self.jugador.x, self.jugador.y = 120, 260
        print(f"\n[>] Te mueves a: {self.sala_actual['nombre']} (Nivel {self.sala_actual['nivel']})")
        if self.sala_actual["item"]:
            print(f"[*] ¡Brilla un objeto en esta sala!: {self.sala_actual['item']['nombre']} (Presiona F o usa opción Recoger)")

        # 3. Disparar el siguiente evento de la Cola con popleft()
        ev = self.gestor_eventos.procesar_siguiente_evento_mapa()
        if ev:
            self.ultimo_mensaje_evento = f"Evento ({ev['tipo']}): {ev['texto']}"
        else:
            self.ultimo_mensaje_evento = "La sala está en calma (Cola de eventos vacía)."

        if self.sala_actual["jefe"] or (ev and ev["tipo"] == "enemigo"):
            self.enemigo_vivo = True
            self.enemigo_hp = 100

    def deshacer_ultimo_movimiento(self):
        """Extrae de la pila con pop() y devuelve de verdad al jugador a la sala y posición anterior."""
        accion = self.historial.deshacer_accion()
        if accion is not None:
            nombre_origen = accion["sala_origen"]
            if nombre_origen in self.registro_salas:
                self.sala_actual = self.registro_salas[nombre_origen]
            self.jugador.x, self.jugador.y = accion["pos_origen"]
            self.ultimo_mensaje_evento = f"Deshiciste acción -> Volviste a: {self.sala_actual['nombre']}"
            print(f"[<] Backtracking completado: estás de vuelta en '{self.sala_actual['nombre']}'.")
        else:
            self.ultimo_mensaje_evento = "Historial vacío: no hay movimientos que deshacer."

    def recoger_objeto_sala(self):
        """Recoge el objeto de la sala actual (si hay) y lo guarda en el Inventario."""
        if self.sala_actual["item"] is not None:
            item_sala = self.sala_actual["item"]
            exito = self.mochila.agregar_item(item_sala["nombre"], item_sala["categoria"], item_sala["cantidad"])
            if exito:
                self.historial.guardar_accion(
                    "recoger",
                    f"Recogió '{item_sala['nombre']}'",
                    self.sala_actual["nombre"],
                    (self.jugador.x, self.jugador.y)
                )
                self.ultimo_mensaje_evento = f"¡Recogiste {item_sala['nombre']}!"
                self.sala_actual["item"] = None
        else:
            print("[!] Caso límite: No hay objetos tirados en esta sala para recoger.")
            self.ultimo_mensaje_evento = "No hay objetos en esta sala (Explora hasta el Nivel 2)."

    def menu_consola_interactivo(self):
        """
        Ejecuta el menú de consola interactivo dentro del ciclo para demostrar todos los requisitos
        y casos límite de la rúbrica (textos, 0, negativos, fuera de rango, cola vacía, pila vacía).
        """
        print("\n=======================================================")
        print("   MODO CONSOLA INTERACTIVA (CHECKPOINT 2 Y 3)         ")
        print("=======================================================")
        while True:
            print(f"\nEstás en: {self.sala_actual['nombre']} (Nivel {self.sala_actual['nivel']})")
            if self.sala_actual["item"]:
                print(f"Objeto en el suelo: {self.sala_actual['item']['nombre']}")
            print("1. Moverse (Mazmorra)  2. Ver inventario / Recoger  3. Deshacer movimiento")
            print("4. Ver historial y estadísticas  5. Ver/Simular turnos  6. Ver árbol de mazmorra  7. Volver a Pygame")

            opcion = pedir_opcion_consola("Opción: ", 1, 7)

            if opcion == 1:
                conexiones = self.sala_actual["conexiones"]
                if not conexiones:
                    print("No hay más salas hacia adelante desde aquí. Usa la opción 3 (Deshacer) para retroceder.")
                    continue
                texto_salas = "  ".join([f"{i+1}) {s['nombre']}" for i, s in enumerate(conexiones)])
                print(f"Salas conectadas: {texto_salas}")
                eleccion = pedir_opcion_consola("Elige una sala: ", 1, len(conexiones))
                self.viajar_a_sala(eleccion - 1)

            elif opcion == 2:
                if self.sala_actual["item"]:
                    self.recoger_objeto_sala()
                self.mochila.mostrar_inventario()

            elif opcion == 3:
                self.deshacer_ultimo_movimiento()

            elif opcion == 4:
                self.historial.consultar_ultima()
                self.historial.mostrar_historial()
                self.historial.contar_acciones_de_tipo("movimiento")
                self.gestor_eventos.contar_eventos_de_tipo("enemigo")

            elif opcion == 5:
                self.gestor_eventos.simular_turnos(3)
                self.turno_en_pantalla = self.gestor_eventos.cola_turnos[0]

            elif opcion == 6:
                print("\n--- ÁRBOL DE LA MAZMORRA RECURSIVA ---")
                maz.mostrar_arbol_mazmorra(self.raiz_mazmorra)

            elif opcion == 7:
                print("[*] Regresando al control en tiempo real de Pygame...\n")
                break

    def manejar_eventos(self):
        """Gestiona las entradas de teclado y ratón en la ventana de Pygame."""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False

            elif evento.type == pygame.KEYDOWN:
                # Abrir / cerrar el panel de estructuras (Grafo, Árbol, Diccionario)
                if evento.key == pygame.K_TAB:
                    self.mostrar_hud_estructuras = not self.mostrar_hud_estructuras

                # Teclas 1 y 2: Avanzar en la mazmorra recursiva (Checkpoint 2)
                elif evento.key == pygame.K_1:
                    self.viajar_a_sala(0)
                elif evento.key == pygame.K_2:
                    self.viajar_a_sala(1)

                # Teclas F1 al F5: Viajar entre salas del Grafo usando BFS (Checkpoint 3)
                elif evento.key == pygame.K_F1:
                    self.viajar_region_grafo("Umbral de Piedra")
                elif evento.key == pygame.K_F2:
                    self.viajar_region_grafo("Forja de Obsidiana")
                elif evento.key == pygame.K_F3:
                    self.viajar_region_grafo("Puente Antiguo")
                elif evento.key == pygame.K_F4:
                    self.viajar_region_grafo("Santuario Lunar")
                elif evento.key == pygame.K_F5:
                    self.viajar_region_grafo("Cámara de Makhai")

                # Tecla C: Completar siguiente misión disponible en el Árbol
                elif evento.key == pygame.K_c:
                    self.intentar_completar_siguiente_mision()

                # Tecla B: Probar bloqueo en Árbol + Búsqueda en Inventario
                elif evento.key == pygame.K_b:
                    exito = self.arbol_misiones.completar_mision("8. Confrontar al Señor de Makhai")
                    if not exito:
                        self.mostrar_notificacion("[!] Bloqueo activo: completa las misiones previas del árbol.", es_error=True)
                    BuscadorInventario.buscar_por_nombre(self.mochila.items, "Corazón de Cuarzo Roto")
                    BuscadorInventario.filtrar_por_categoria(self.mochila.items, "Objeto Clave")

                # Tecla U: Deshacer último movimiento en el Grafo/Mundo (Checkpoint 3)
                elif evento.key == pygame.K_u:
                    self.deshacer_accion_mundo()

                # Esquive (Dash) con Alt Izquierdo
                elif evento.key == pygame.K_LALT:
                    if "ataque" not in self.jugador.estado_actual and self.jugador.estado_actual != "dash":
                        self.jugador.cambiar_estado("dash")

                # Deshacer (Backtracking real en mazmorra) con Backspace
                elif evento.key == pygame.K_BACKSPACE:
                    self.deshacer_ultimo_movimiento()

                # Recoger objeto de la sala con F
                elif evento.key == pygame.K_f:
                    self.recoger_objeto_sala()

                # Abrir/Cerrar UI de inventario con I
                elif evento.key == pygame.K_i:
                    self.inventario_abierto = not self.inventario_abierto

                # Rotar turno con T
                elif evento.key == pygame.K_t:
                    actual = self.gestor_eventos.avanzar_turno()
                    if actual:
                        self.turno_en_pantalla = actual

                # Mostrar historial y estadísticas en consola con H
                elif evento.key == pygame.K_h:
                    self.historial.consultar_ultima()
                    self.historial.mostrar_historial()
                    self.historial.contar_acciones_de_tipo("movimiento")

                # Abrir menú interactivo de consola con M
                elif evento.key == pygame.K_m:
                    self.menu_consola_interactivo()

            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clic izquierdo
                    dir_ataque = self.jugador.direccion_actual

                    if "abajo" in dir_ataque:
                        dir_ataque = "abajo"
                    elif "arriba" in dir_ataque:
                        dir_ataque = "arriba"
                    elif "derecha" in dir_ataque:
                        dir_ataque = "derecha"
                    elif "izquierda" in dir_ataque:
                        dir_ataque = "izquierda"

                    self.jugador.direccion_actual = dir_ataque

                    # CASO A: Input Buffer (Guardar el combo)
                    if self.jugador.estado_actual == "ataque_1":
                        if not self.jugador.combo_solicitado:
                            self.jugador.combo_solicitado = True
                            self.gestor_eventos.agregar_evento("ATAQUE", dir_ataque)
                            print("[*] ¡Input Buffer: Combo Guardado en Memoria!")

                    # CASO B: Iniciar el ataque normal
                    elif "ataque" not in self.jugador.estado_actual:
                        self.jugador.cambiar_estado("ataque_1")
                        self.jugador.combo_solicitado = False
                        self.gestor_eventos.agregar_evento("ATAQUE", dir_ataque)
                        print(f"[*] ¡Ataque 1 Iniciado hacia: {dir_ataque}!")

    def actualizar(self):
        """Actualiza la física del jugador, animaciones, puertas y colisiones de combate."""
        teclas = pygame.key.get_pressed()
        se_esta_moviendo = False

        if self.jugador.estado_actual == "dash":
            multiplicador_dash = 2
            if self.jugador.direccion_actual == "derecha":
                self.jugador.x += self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "izquierda":
                self.jugador.x -= self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "abajo":
                self.jugador.y += self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "arriba":
                self.jugador.y -= self.jugador.velocidad * multiplicador_dash

        elif "ataque" not in self.jugador.estado_actual:
            vel_x = 0
            vel_y = 0

            mov_derecha = teclas[pygame.K_d]
            mov_izquierda = teclas[pygame.K_a]
            mov_arriba = teclas[pygame.K_w]
            mov_abajo = teclas[pygame.K_s]

            if mov_derecha:
                vel_x = self.jugador.velocidad
                self.jugador.direccion_actual = "derecha"
                se_esta_moviendo = True
            elif mov_izquierda:
                vel_x = -self.jugador.velocidad
                self.jugador.direccion_actual = "izquierda"
                se_esta_moviendo = True

            if mov_arriba:
                vel_y = -self.jugador.velocidad
                se_esta_moviendo = True
                self.jugador.direccion_actual = "arriba"
            elif mov_abajo:
                vel_y = self.jugador.velocidad
                se_esta_moviendo = True
                self.jugador.direccion_actual = "abajo"

            if mov_abajo and mov_derecha:
                self.jugador.direccion_actual = "abajo_derecha"
            elif mov_abajo and mov_izquierda:
                self.jugador.direccion_actual = "abajo_izquierda"
            elif mov_arriba and mov_derecha:
                self.jugador.direccion_actual = "derecha"
            elif mov_arriba and mov_izquierda:
                self.jugador.direccion_actual = "izquierda"

            self.jugador.x += vel_x
            self.jugador.y += vel_y

            if se_esta_moviendo:
                self.jugador.cambiar_estado("correr")
            else:
                if "abajo" in self.jugador.direccion_actual:
                    self.jugador.direccion_actual = "abajo"
                self.jugador.cambiar_estado("idle")

        self.jugador.x = max(50, min(self.jugador.x, 680))
        self.jugador.y = max(90, min(self.jugador.y, 450))

        self.jugador.actualizar_animacion()

        eventos_pendientes = self.gestor_eventos.procesar_eventos()
        for evento in eventos_pendientes:
            if evento["tipo"] == "ATAQUE" and self.enemigo_vivo:
                hitbox_enemigo = pygame.Rect(self.enemigo_x, self.enemigo_y, self.enemigo_tamano, self.enemigo_tamano)
                hitbox_ataque = pygame.Rect(0, 0, 60, 60)
                centro_x = self.jugador.x + (self.jugador.tamano // 2)
                centro_y = self.jugador.y + (self.jugador.tamano // 2)
                offset = 40

                if evento["datos"] == "derecha":
                    hitbox_ataque.center = (centro_x + offset, centro_y)
                elif evento["datos"] == "izquierda":
                    hitbox_ataque.center = (centro_x - offset, centro_y)
                elif evento["datos"] == "abajo":
                    hitbox_ataque.center = (centro_x, centro_y + offset)
                elif evento["datos"] == "arriba":
                    hitbox_ataque.center = (centro_x, centro_y - offset)

                if hitbox_ataque.colliderect(hitbox_enemigo):
                    self.enemigo_hp -= 25
                    print(f"[!] ¡Impacto! Vida del enemigo: {self.enemigo_hp}")
                    if self.enemigo_hp <= 0:
                        self.enemigo_vivo = False
                        print("[+] ¡Enemigo derrotado!")
                else:
                    print("[-] Fallaste. Ataque al aire.")

    def dibujar(self):
        """Renderiza el mapa de fondo, las entidades y la interfaz de las estructuras de datos."""
        self.pantalla.fill((45, 45, 50))
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 0, 800, 90))
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 540, 800, 60))
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 0, 50, 600))
        pygame.draw.rect(self.pantalla, (90, 90, 100), (750, 0, 50, 600))

        conexiones = self.sala_actual["conexiones"]
        if len(conexiones) >= 1:
            pygame.draw.rect(self.pantalla, (139, 69, 19), (750, 180, 50, 80))
        if len(conexiones) >= 2:
            pygame.draw.rect(self.pantalla, (139, 69, 19), (750, 360, 50, 80))

        if self.sala_actual["item"] is not None:
            pygame.draw.circle(self.pantalla, (0, 255, 255), (400, 300), 14)
            txt_item = self.fuente_pequena.render(f"[F] {self.sala_actual['item']['nombre']}", True, (0, 255, 255))
            self.pantalla.blit(txt_item, (330, 265))

        self.jugador.dibujar(self.pantalla)
        if self.enemigo_vivo:
            pygame.draw.rect(self.pantalla, (220, 40, 40), (self.enemigo_x, self.enemigo_y, self.enemigo_tamano, self.enemigo_tamano))

        txt_sala = self.fuente.render(f"Sala: {self.sala_actual['nombre']} (Nivel {self.sala_actual['nivel']})", True, (255, 215, 0))
        self.pantalla.blit(txt_sala, (20, 10))

        if conexiones:
            salas_str = " | ".join([f"[{i+1}] {s['nombre']}" for i, s in enumerate(conexiones)])
        else:
            salas_str = "Sala más profunda alcanzada. Usa [BACKSPACE] para deshacer y volver."
        txt_conex = self.fuente_pequena.render(f"Salidas: {salas_str}", True, (220, 220, 220))
        self.pantalla.blit(txt_conex, (20, 38))

        txt_ev = self.fuente_pequena.render(f"{self.ultimo_mensaje_evento}", True, (150, 255, 150))
        self.pantalla.blit(txt_ev, (20, 62))

        txt_turno = self.fuente_pequena.render(f"Turno [T]: {self.turno_en_pantalla} | Pila: {len(self.historial.pila)} | [M] Menú Consola", True, (255, 200, 100))
        self.pantalla.blit(txt_turno, (20, 540))

        if self.inventario_abierto:
            pygame.draw.rect(self.pantalla, (20, 20, 30), (20, 100, 360, 220))
            pygame.draw.rect(self.pantalla, (255, 215, 0), (20, 100, 360, 220), 2)
            titulo = self.fuente.render("--- MOCHILA (INVENTARIO) ---", True, (255, 255, 0))
            self.pantalla.blit(titulo, (35, 110))
            pos_y = 145
            if not self.mochila.items:
                self.pantalla.blit(self.fuente_pequena.render("El inventario está vacío", True, (200, 200, 200)), (35, pos_y))
            else:
                for item in self.mochila.items:
                    linea = f"- {item['nombre']} x{item['cantidad']} ({item['categoria']})"
                    self.pantalla.blit(self.fuente_pequena.render(linea, True, (255, 255, 255)), (35, pos_y))
                    pos_y += 25

        # Barra inferior fija con el estado actual y alertas de casos límite
        barra = pygame.Surface((self.pantalla.get_width(), 32), pygame.SRCALPHA)
        barra.fill((10, 12, 20, 210))
        self.pantalla.blit(barra, (0, self.pantalla.get_height() - 32))
        txt_alerta = self.fuente_hud.render(self.mensaje_alerta, True, self.color_alerta)
        self.pantalla.blit(txt_alerta, (12, self.pantalla.get_height() - 25))

        # Panel desplegable con [TAB] mostrando Grafo, Árbol y Diccionario en vivo
        if self.mostrar_hud_estructuras:
            panel = pygame.Surface((760, 460), pygame.SRCALPHA)
            panel.fill((15, 18, 30, 235))
            pygame.draw.rect(panel, (100, 160, 255), panel.get_rect(), 2)
            self.pantalla.blit(panel, (20, 20))

            sala_act = self.estado_mundo.consultar("sala_actual")
            bloqueados = {"Cámara de Makhai"} if self.estado_mundo.consultar("camara_makhai_bloqueada", True) else set()
            alcanzables = sorted(list(self.mapa.dfs_zonas_alcanzables(sala_act, bloqueados)))
            ruta_jefe = self.mapa.bfs_ruta_corta(sala_act, "Cámara de Makhai", bloqueados)
            disponibles = self.arbol_misiones.misiones_disponibles()
            total_recompensas = self.arbol_misiones.postorden_recompensas()
            etapas = self.arbol_misiones.recorrido_por_niveles()

            lineas = [
                ("ESTADO DEL MUNDO (Diccionario)", (255, 215, 100)),
                (f"  {self.estado_mundo.resumen_progreso()}", (235, 235, 235)),
                (f"  Banderas activas: {self.estado_mundo.filtrar_estados_activos()}", (200, 220, 255)),
                ("", (255, 255, 255)),
                ("MAPA DE SALAS (Grafo - BFS y DFS)", (120, 220, 255)),
                (f"  Zonas alcanzables (DFS): {', '.join(alcanzables)}", (235, 235, 235)),
                (f"  Ruta al Jefe (BFS): {' -> '.join(ruta_jefe) if ruta_jefe else 'BLOQUEADA (Requiere Llave Lunar)'}", (235, 235, 235)),
                ("  Viajar: [F1] Umbral [F2] Forja [F3] Puente [F4] Santuario [F5] Cámara", (170, 185, 210)),
                ("", (255, 255, 255)),
                ("ÁRBOL DE MISIONES (Preorden / Postorden / Niveles)", (140, 255, 160)),
                (f"  Disponibles ahora: {', '.join(disponibles) if disponibles else 'Ninguna'}", (235, 235, 235)),
                (f"  Recompensa total del árbol (Postorden): {total_recompensas} oro", (235, 235, 235)),
                (f"  Niveles del árbol (Por niveles): {len(etapas)} etapas activas", (200, 220, 255)),
                ("  Acciones: [C] Completar misión  [B] Probar bloqueo  [U] Deshacer", (170, 185, 210)),
            ]

            y_offset = 32
            for texto, color in lineas:
                if not texto:
                    y_offset += 14
                    continue
                sublineas = textwrap.wrap(texto, width=82, subsequent_indent="    ")
                for sub in sublineas:
                    superficie_txt = self.fuente_hud.render(sub, True, color)
                    self.pantalla.blit(superficie_txt, (35, y_offset))
                    y_offset += 22

        pygame.display.flip()

    def ejecutar(self):
        """Ejecuta el bucle principal a 60 FPS."""
        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()
