"""
Archivo central de Aventura Algorítmica (Awakening of Makhai) - Checkpoint 2.
Integra Inventario (Listas), Historial (Pila LIFO), Eventos/Turnos (Cola FIFO) y Mazmorra (Recursividad).
"""
import pygame
import sys
from historial import HistorialAcciones
from inventario import Inventario
from buscador import BuscadorInventario
from eventos import ColaEventos
from jugador import Jugador
import mazmorra as maz

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
        """Inicializa Pygame, las estructuras de datos del Checkpoint 2 y las entidades del juego."""
        pygame.init()
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Awakening of Makhai - Checkpoint 2")
        self.reloj = pygame.time.Clock()
        self.corriendo = True

        # --- 1. ESTRUCTURAS DE DATOS (CHECKPOINT 1 Y 2) ---
        self.historial = HistorialAcciones()
        self.mochila = Inventario(capacidad_maxima=10)
        self.gestor_eventos = ColaEventos()

        # Generación recursiva de la mazmorra (Profundidad 2 = 7 salas)
        iter_nombres = iter(maz.NOMBRES_SALAS_MAKHAI)
        iter_objetos = iter(maz.OBJETOS_SALAS_PROFUNDAS)
        self.profundidad_max = 2
        self.raiz_mazmorra = maz.generar_mazmorra_recursiva(0, self.profundidad_max, iter_nombres)
        
        # Aplicamos las 2 adaptaciones de la Guía 7 al iniciar
        maz.marcar_salas_profundas(self.raiz_mazmorra, self.profundidad_max, iter_objetos)
        self.conteo_niveles = maz.contar_salas_por_nivel(self.raiz_mazmorra)
        self.total_salas = sum(self.conteo_niveles.values())

        # Diccionario auxiliar para buscar referencias de salas por nombre al hacer backtracking
        self.registro_salas = {}
        self._indexar_salas(self.raiz_mazmorra)
        self.sala_actual = self.raiz_mazmorra

        # Mensajes de inicio en consola (idéntico al formato esperado en la guía)
        print("\n=== Awakening of Makhai: La Cripta del Cuarzo ===")
        print(f"Mazmorra generada: {self.total_salas} salas, profundidad {maz.calcular_profundidad_real(self.raiz_mazmorra)}")
        print(f"Salas por nivel: {self.conteo_niveles}")
        print(f"Estás en: {self.sala_actual['nombre']}")
        print("Controles Pygame: [WASD] Mover | [1/2] Cambiar de sala | [BACKSPACE] Deshacer | [F] Recoger | [I] Mochila | [T] Turno | [H] Historial | [M] Menú Consola\n")

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

    def _indexar_salas(self, nodo):
        """Guarda cada nodo del árbol en un diccionario para acceso rápido durante el backtracking."""
        if nodo is not None:
            self.registro_salas[nodo["nombre"]] = nodo
            for hija in nodo["conexiones"]:
                self._indexar_salas(hija)

    def viajar_a_sala(self, indice_conexion):
        """Mueve al jugador a una sala conectada, registra en la pila y procesa un evento de la cola."""
        conexiones = self.sala_actual["conexiones"]
        if not conexiones:
            print("[!] Caso límite: Esta sala es el fondo de la rama, no hay más salas hacia adelante. ¡Usa Deshacer (BACKSPACE)!")
            self.ultimo_mensaje_evento = "Sin salida adelante. ¡Usa BACKSPACE para retroceder!"
            return

        # Validación de rango seguro (evita índices inválidos o negativos)
        if indice_conexion < 0 or indice_conexion >= len(conexiones):
            print(f"[!] Caso límite: Sala no conectada. Elige un índice válido entre 1 y {len(conexiones)}.")
            return

        nueva_sala = conexiones[indice_conexion]
        
        # 1. Registrar acción en la Pila (Guía 5) guardando sala y coordenadas actuales
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

        # 3. Disparar el siguiente evento de la Cola con popleft() (Guía 6)
        ev = self.gestor_eventos.procesar_siguiente_evento_mapa()
        if ev:
            self.ultimo_mensaje_evento = f"Evento ({ev['tipo']}): {ev['texto']}"
        else:
            self.ultimo_mensaje_evento = "La sala está en calma (Cola de eventos vacía)."

        # Revivir o posicionar enemigo si hay jefe o evento de enemigo
        if self.sala_actual["jefe"] or (ev and ev["tipo"] == "enemigo"):
            self.enemigo_vivo = True
            self.enemigo_hp = 100

    def deshacer_ultimo_movimiento(self):
        """Extrae de la pila con pop() y devuelve de verdad al jugador a la sala y posición anterior."""
        accion = self.historial.deshacer_accion()
        if accion is not None:
            # Backtracking real a la sala de origen
            nombre_origen = accion["sala_origen"]
            if nombre_origen in self.registro_salas:
                self.sala_actual = self.registro_salas[nombre_origen]
            self.jugador.x, self.jugador.y = accion["pos_origen"]
            self.ultimo_mensaje_evento = f"Deshiciste acción -> Volviste a: {self.sala_actual['nombre']}"
            print(f"[<] Backtracking completado: estás de vuelta en '{self.sala_actual['nombre']}'.")
        else:
            self.ultimo_mensaje_evento = "Historial vacío: no hay movimientos que deshacer."

    def recoger_objeto_sala(self):
        """Recoge el objeto de la sala actual (si hay) o un objeto de prueba y lo guarda en el Inventario."""
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
        print("   MODO CONSOLA INTERACTIVA (EVIDENCIA CHECKPOINT 2)   ")
        print("=======================================================")
        while True:
            print(f"\nEstás en: {self.sala_actual['nombre']} (Nivel {self.sala_actual['nivel']})")
            if self.sala_actual["item"]:
                print(f"Objeto en el suelo: {self.sala_actual['item']['nombre']}")
            print("1. Moverse  2. Ver inventario / Recoger  3. Deshacer movimiento")
            print("4. Ver historial y estadísticas  5. Ver/Simular turnos  6. Ver árbol de mazmorra  7. Volver a ventana Pygame")

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
                # Cambiar a salas conectadas con teclas 1 y 2
                if evento.key == pygame.K_1:
                    self.viajar_a_sala(0)
                elif evento.key == pygame.K_2:
                    self.viajar_a_sala(1)

                # Esquive (Dash) con Alt Izquierdo
                elif evento.key == pygame.K_LALT:
                    if "ataque" not in self.jugador.estado_actual and self.jugador.estado_actual != "dash":
                        self.jugador.cambiar_estado("dash")

                # Deshacer (Backtracking real) con Backspace
                elif evento.key == pygame.K_BACKSPACE:
                    self.deshacer_ultimo_movimiento()

                # Recoger objeto de la sala con F
                elif evento.key == pygame.K_f:
                    self.recoger_objeto_sala()

                # Abrir/Cerrar UI de inventario con I
                elif evento.key == pygame.K_i:
                    self.inventario_abierto = not self.inventario_abierto

                # Buscar/Filtrar inventario con B
                elif evento.key == pygame.K_b:
                    BuscadorInventario.buscar_por_nombre(self.mochila.items, "Corazón de Cuarzo Roto")
                    BuscadorInventario.filtrar_por_categoria(self.mochila.items, "Objeto Clave")

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

            # Sistema de combate con combos (Clic Izquierdo)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    if self.jugador.estado_actual == "ataque_1":
                        if not self.jugador.combo_solicitado:
                            self.jugador.combo_solicitado = True
                            self.gestor_eventos.agregar_evento("ATAQUE", self.jugador.direccion_actual)
                            print("[*] ¡Input Buffer: Combo Guardado en Memoria!")
                    elif "ataque" not in self.jugador.estado_actual:
                        self.jugador.cambiar_estado("ataque_1")
                        self.jugador.combo_solicitado = False
                        self.gestor_eventos.agregar_evento("ATAQUE", self.jugador.direccion_actual)
                        print("[*] ¡Ataque 1 Iniciado!")

    def actualizar(self):
        """Actualiza la física del jugador, animaciones, puertas y colisiones de combate."""
        teclas = pygame.key.get_pressed()
        se_esta_moviendo = False

        # A) Física del Dash
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

        # B) Movimiento en 8 direcciones (incluyendo diagonal)
        elif "ataque" not in self.jugador.estado_actual:
            vel_x = 0
            vel_y = 0
            if teclas[pygame.K_d]:
                vel_x = self.jugador.velocidad
                self.jugador.direccion_actual = "derecha"
                se_esta_moviendo = True
            elif teclas[pygame.K_a]:
                vel_x = -self.jugador.velocidad
                self.jugador.direccion_actual = "izquierda"
                se_esta_moviendo = True

            if teclas[pygame.K_w]:
                vel_y = -self.jugador.velocidad
                se_esta_moviendo = True
                if vel_x == 0:
                    self.jugador.direccion_actual = "arriba"
            elif teclas[pygame.K_s]:
                vel_y = self.jugador.velocidad
                se_esta_moviendo = True
                if vel_x == 0:
                    self.jugador.direccion_actual = "abajo"

            self.jugador.x += vel_x
            self.jugador.y += vel_y

            if se_esta_moviendo:
                self.jugador.cambiar_estado("correr")
            else:
                self.jugador.cambiar_estado("idle")

        # Mantener al jugador dentro de los muros de la sala
        self.jugador.x = max(50, min(self.jugador.x, 680))
        self.jugador.y = max(90, min(self.jugador.y, 450))

        self.jugador.actualizar_animacion()

        # Procesar cola de combate en tiempo real
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
        # 1. Dibujar suelo y muros estilo mazmorra (inspirado en tu mapas.py)
        self.pantalla.fill((45, 45, 50)) # Suelo de piedra
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 0, 800, 90))   # Muro superior (HUD)
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 540, 800, 60)) # Muro inferior
        pygame.draw.rect(self.pantalla, (90, 90, 100), (0, 0, 50, 600))   # Muro izquierdo
        pygame.draw.rect(self.pantalla, (90, 90, 100), (750, 0, 50, 600)) # Muro derecho

        # Dibujar puertas si la sala tiene conexiones hijas
        conexiones = self.sala_actual["conexiones"]
        if len(conexiones) >= 1:
            pygame.draw.rect(self.pantalla, (139, 69, 19), (750, 180, 50, 80)) # Puerta 1
        if len(conexiones) >= 2:
            pygame.draw.rect(self.pantalla, (139, 69, 19), (750, 360, 50, 80)) # Puerta 2

        # Dibujar objeto brillante en la sala si existe (Salas profundas Nivel 2)
        if self.sala_actual["item"] is not None:
            pygame.draw.circle(self.pantalla, (0, 255, 255), (400, 300), 14)
            txt_item = self.fuente_pequena.render(f"[F] {self.sala_actual['item']['nombre']}", True, (0, 255, 255))
            self.pantalla.blit(txt_item, (330, 265))

        # 2. Dibujar Jugador y Enemigo
        self.jugador.dibujar(self.pantalla)
        if self.enemigo_vivo:
            pygame.draw.rect(self.pantalla, (220, 40, 40), (self.enemigo_x, self.enemigo_y, self.enemigo_tamano, self.enemigo_tamano))

        # 3. Dibujar HUD Superior con información del Checkpoint 2
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
        self.pantalla.blit(txt_turno, (20, 560))

        # 4. Dibujar Mochila desplegable si está abierta (Tecla I)
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