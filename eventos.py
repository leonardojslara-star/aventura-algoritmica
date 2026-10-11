"""Módulo de eventos del mapa y sistema de turnos con Colas (FIFO) - Semana 6 / Guía 6."""
from collections import deque

class ColaEventos:
    def __init__(self):
        """Inicializa la cola de eventos del mapa, la cola de combate y la cola de turnos usando deque."""
        # Cola de eventos narrativos/exploración de la mazmorra (Requisito Guía 6)
        self.cola_mapa = deque([
            {"tipo": "enemigo", "texto": "Un Centinela de Cuarzo emerge de las sombras y bloquea el paso."},
            {"tipo": "trampa", "texto": "Pisas una baldosa hundida: dardos antiguos cruzan el pasillo."},
            {"tipo": "cofre", "texto": "Descubres un cofre oxidado con suministros olvidados."},
            {"tipo": "mensaje", "texto": "Inscripción en el muro: 'Jarek cayó donde el eco se divide'."},
            {"tipo": "enemigo", "texto": "Una Sombra de Ceniza te acecha desde las columnas."},
            {"tipo": "trampa", "texto": "El suelo tiembla y una fisura mágica libera energía oscura."}
        ])
        
        # Cola de turnos para al menos 3 participantes (Requisito Guía 6)
        self.cola_turnos = deque(["Makhai (Jugador)", "Jarek (Aliado)", "Centinela de Cuarzo (Enemigo)"])
        
        # Cola rápida para tus impactos de combate en tiempo real en Pygame
        self.cola_combate = deque()

    # --- GESTIÓN DE EVENTOS DEL MAPA (FIFO con popleft) ---
    def encolar_evento_mapa(self, tipo, texto):
        """Agrega un nuevo evento del mapa al final de la cola con append()."""
        self.cola_mapa.append({"tipo": tipo, "texto": texto})

    def procesar_siguiente_evento_mapa(self):
        """Extrae y procesa el evento más antiguo del mapa con popleft() en O(1)."""
        if len(self.cola_mapa) > 0:
            evento = self.cola_mapa.popleft()
            print(f"⚡ Evento [{evento['tipo'].upper()}]: {evento['texto']} (Quedan {len(self.cola_mapa)} eventos)")
            return evento
        else:
            print("[!] Caso límite: No quedan más eventos en la cola de la mazmorra.")
            return None

    # --- SISTEMA DE TURNOS (Rotación con popleft y append) ---
    def avanzar_turno(self):
        """Rota el turno actual: saca al primero con popleft() y lo reingresa al final con append()."""
        if len(self.cola_turnos) > 0:
            participante_actual = self.cola_turnos.popleft()
            self.cola_turnos.append(participante_actual)
            print(f"🔄 Turno actual: {participante_actual} | Siguiente en fila: {self.cola_turnos[0]}")
            return participante_actual
        return None

    # --- 2 FUNCIONES ADAPTADAS DE LA GUÍA 6 ---
    def contar_eventos_de_tipo(self, tipo_buscado):
        """Cuenta cuántos eventos pendientes de un tipo específico quedan en la cola del mapa."""
        cantidad = sum(1 for ev in self.cola_mapa if ev["tipo"].lower() == tipo_buscado.lower())
        print(f"[#] Eventos pendientes de tipo '{tipo_buscado}': {cantidad}")
        return cantidad

    def simular_turnos(self, cantidad_turnos=3):
        """Simula varios turnos seguidos rotando a los participantes."""
        if cantidad_turnos <= 0:
            print("[!] Caso límite: La cantidad de turnos a simular debe ser mayor a 0.")
            return
        print(f"\n--- ⚔️ SIMULACIÓN DE {cantidad_turnos} TURNOS DE COMBATE ---")
        for i in range(cantidad_turnos):
            actua = self.cola_turnos.popleft()
            self.cola_turnos.append(actua)
            print(f"  Turno {i+1}: Actúa -> {actua} (En espera: {', '.join(self.cola_turnos)})")
        print("--------------------------------------------------\n")

    # --- COMPATIBILIDAD CON TU SISTEMA DE COMBATE EN PYGAME ---
    def agregar_evento(self, tipo_evento, datos):
        """Encola ataques en tiempo real desde Pygame."""
        self.cola_combate.append({"tipo": tipo_evento, "datos": datos})

    def procesar_eventos(self):
        """Saca todos los eventos de combate pendientes usando popleft() en O(1)."""
        eventos_a_resolver = []
        while len(self.cola_combate) > 0:
            eventos_a_resolver.append(self.cola_combate.popleft())
        return eventos_a_resolver