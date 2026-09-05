import pygame
import sys
from historial import HistorialAcciones
from inventario import Inventario
from buscador import BuscadorInventario
from eventos import ColaEventos 
from jugador import Jugador
""" from mapas import sala_inicio, TAMANO_TILE, COLUMNAS, FILAS, ANCHO_VENTANA, ALTO_VENTANA """

class Juego:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mi Juego Algorítmico")
        self.reloj = pygame.time.Clock()
        self.corriendo = True
        
        # Instancia de tu algoritmo de pila
        self.historial = HistorialAcciones()
        self.mochila = Inventario(capacidad_maxima=5)
        self.gestor_eventos = ColaEventos() # <-- Agrega esto
        
        # --- NUEVAS VARIABLES DEL JUGADOR ---
        self.jugador = Jugador(400, 300)
        # Usamos 40 píxeles de velocidad para que se mueva en "cuadrículas" 
        # y el efecto de deshacer sea muy evidente
        self.jugador_velocidad = 5 
        
        self.frames_vfx = [
            pygame.image.load("assets/warrior_skill2_frame1.png"),
            pygame.image.load("assets/warrior_skill2_frame2.png"),
            pygame.image.load("assets/warrior_skill2_frame3.png"),
            pygame.image.load("assets/warrior_skill2_frame4.png"),
            pygame.image.load("assets/warrior_skill2_frame5.png"),
            pygame.image.load("assets/warrior_skill2_frame6.png"),
            pygame.image.load("assets/warrior_skill2_frame7.png"),
            pygame.image.load("assets/warrior_skill2_frame8.png"), 
            pygame.image.load("assets/warrior_skill2_frame9.png")
        ]
        
        # Variables de control
        self.vfx_activo = False      # Nos dice si la animación se está reproduciendo
        self.vfx_indice_actual = 0   # En qué cuadro de la lista estamos
        self.vfx_x = 0               # Dónde se dibujará el efecto
        self.vfx_y = 0
        
        self.direccion_actual = "derecha"
    
        pygame.font.init() 
        self.fuente = pygame.font.SysFont("Arial", 24) 
        
        # ¡ESTA ES LA LÍNEA QUE TE FALTA!
        self.inventario_abierto = False
        
        # --- SISTEMA DE ENEMIGOS ---
        # Lo colocamos a la derecha de la pantalla
        self.enemigo_x = 600
        self.enemigo_y = 300
        self.enemigo_tamano = 40
        self.enemigo_hp = 100
        self.enemigo_vivo = True
        
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.corriendo = False
            
            # Detectar cuando se presiona una tecla
            elif evento.type == pygame.KEYDOWN:
    
                # --- SISTEMA DE MOVIMIENTO Y GUARDADO ---
                if evento.key == pygame.K_d:
                # Guardamos la tupla con las coordenadas NUEVAS
                    self.historial.guardar_accion((self.jugador.x, self.jugador.y))
                    self.jugador.x += self.jugador.velocidad
                    self.jugador.direccion_actual = "derecha"
                
                elif evento.key == pygame.K_a:
                    self.historial.guardar_accion((self.jugador.x, self.jugador.y))
                    self.jugador.x -= self.jugador.velocidad
                    self.jugador.direccion_actual = "izquierda"

                elif evento.key == pygame.K_s:
                    self.historial.guardar_accion((self.jugador.x, self.jugador.y))
                    self.jugador.y += self.jugador.velocidad
                    self.jugador.direccion_actual = "abajo"
                
                elif evento.key == pygame.K_w:
                    self.historial.guardar_accion((self.jugador.x, self.jugador.y))
                    self.jugador.y -= self.jugador.velocidad
                    self.jugador.direccion_actual = "arriba"
                    
                # --- SISTEMA DE ESQUIVE (DASH) ---
                elif evento.key == pygame.K_LALT:
                    # Solo podemos esquivar si NO estamos atacando y si NO estamos ya en pleno dash
                    if "ataque" not in self.jugador.estado_actual and self.jugador.estado_actual != "dash":
                        self.jugador.cambiar_estado("dash")
                
                # --- SISTEMA DE DESHACER (REBOBINAR) ---
                elif evento.key == pygame.K_BACKSPACE:
                    posicion_anterior = self.historial.deshacer_accion()
                    
                    # Si la pila no está vacía, teletransportamos al jugador
                    if posicion_anterior is not None:
                        # Extraemos la X y la Y de la tupla guardada
                        self.jugador_x, self.jugador_y = posicion_anterior
                
                # --- SISTEMA DE INVENTARIO ---
                elif evento.key == pygame.K_f:
                    # Simulamos recoger una llave antigua
                    exito = self.mochila.agregar_item("Llave Antigua", "Objeto Clave", 1)
                    
                    if exito:
                        # Si se agregó con éxito, imprimimos el inventario para verlo
                        self.mochila.mostrar_inventario()
                 
                # --- NUEVO: TECLA PARA VER EL INVENTARIO ---
                elif evento.key == pygame.K_i:
                    # Esto invierte el valor (Si es False pasa a True, y viceversa)
                    self.inventario_abierto = not self.inventario_abierto 
                    
                # --- SISTEMA DE BÚSQUEDA ---
                elif evento.key == pygame.K_b:
                    # Extraemos la lista pura de la mochila
                    lista_actual = self.mochila.items

                    # Probamos el algoritmo de búsqueda lineal
                    BuscadorInventario.buscar_por_nombre(lista_actual, "Llave Antigua")

                    # Probamos el algoritmo de filtrado
                    BuscadorInventario.filtrar_por_categoria(lista_actual, "Arma")
                        
                # --- SISTEMA DE COMBATE CON COMBOS ---
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Clic izquierdo
                        
                        # CASO A: Ya estamos a mitad del primer tajo
                    if self.jugador.estado_actual == "ataque_1":
                            # Si es el primer doble clic, lo guardamos. Si hace 10 clics extra, los ignoramos.
                        if not self.jugador.combo_solicitado:
                                self.jugador.combo_solicitado = True 
                                # ¡Encolamos el daño del segundo tajo!
                                self.gestor_eventos.agregar_evento("ATAQUE", self.jugador.direccion_actual)
                                print("[*] ¡Input Buffer: Combo Guardado en Memoria!")
                            
                        # CASO B: El personaje está tranquilo, iniciamos el combate normal
                    elif "ataque" not in self.jugador.estado_actual:
                            self.jugador.cambiar_estado("ataque_1")
                            self.jugador.combo_solicitado = False
                            
                            # Registramos el golpe del primer tajo
                            self.gestor_eventos.agregar_evento("ATAQUE", self.jugador.direccion_actual)
                            print("[*] ¡Ataque 1 Iniciado!")
                            
                

    def actualizar(self):
        # --- 1. LÓGICA DE MOVIMIENTO Y ESTADOS ---
        teclas = pygame.key.get_pressed()
        se_esta_moviendo = False
        
        # A) FÍSICA DEL DASH: Si estamos esquivando, el motor nos empuja automáticamente
        if self.jugador.estado_actual == "dash":
            multiplicador_dash = 2  # Viajará 2 veces más rápido que caminando
            
            if self.jugador.direccion_actual == "derecha":
                self.jugador.x += self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "izquierda":
                self.jugador.x -= self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "abajo":
                self.jugador.y += self.jugador.velocidad * multiplicador_dash
            elif self.jugador.direccion_actual == "arriba":
                self.jugador.y -= self.jugador.velocidad * multiplicador_dash

        # B) MOVIMIENTO NORMAL: Solo funciona si NO estamos atacando NI esquivando
        elif "ataque" not in self.jugador.estado_actual:
            if teclas[pygame.K_d]:
                self.jugador.x += self.jugador.velocidad
                self.jugador.direccion_actual = "derecha"
                se_esta_moviendo = True
            elif teclas[pygame.K_a]:
                self.jugador.x -= self.jugador.velocidad
                self.jugador.direccion_actual = "izquierda"
                se_esta_moviendo = True
            elif teclas[pygame.K_w]:
                self.jugador.y -= self.jugador.velocidad
                self.jugador.direccion_actual = "arriba"
                se_esta_moviendo = True
            elif teclas[pygame.K_s]:
                self.jugador.y += self.jugador.velocidad
                self.jugador.direccion_actual = "abajo"
                se_esta_moviendo = True

            if se_esta_moviendo:
                self.jugador.cambiar_estado("correr")
            else:
                self.jugador.cambiar_estado("idle")

        # Avanzamos el fotograma de la animación actual
        self.jugador.actualizar_animacion()

        # --- PROCESAR LA COLA DE EVENTOS Y COLISIONES ---
        eventos_pendientes = self.gestor_eventos.procesar_eventos()
         
        for evento in eventos_pendientes:
            if evento["tipo"] == "ATAQUE":
                
                # Solo calculamos el golpe si el enemigo sigue vivo
                if self.enemigo_vivo:
                    # 1. AQUÍ CREAMOS LAS VARIABLES PARA QUE EXISTAN
                    hitbox_enemigo = pygame.Rect(self.enemigo_x, self.enemigo_y, self.enemigo_tamano, self.enemigo_tamano)
                    hitbox_ataque = pygame.Rect(0, 0, 50, 50)
                    
                    # 2. ACTUALIZADO: Ahora usamos self.jugador.x y self.jugador.y
                    centro_x = self.jugador.x + (self.jugador.tamano // 2)
                    centro_y = self.jugador.y + (self.jugador.tamano // 2)
                    
                    offset = 35
                    if evento["datos"] == "derecha":
                        hitbox_ataque.center = (centro_x + offset, centro_y)
                    elif evento["datos"] == "izquierda":
                        hitbox_ataque.center = (centro_x - offset, centro_y)
                    elif evento["datos"] == "abajo":
                        hitbox_ataque.center = (centro_x, centro_y + offset)
                    elif evento["datos"] == "arriba":
                        hitbox_ataque.center = (centro_x, centro_y - offset)

                    # 3. EL CÁLCULO DE COLISIÓN (Indentado correctamente)
                    if hitbox_ataque.colliderect(hitbox_enemigo):
                        self.enemigo_hp -= 25 
                        print(f"[!] ¡Impacto! Vida del enemigo: {self.enemigo_hp}")
                        
                        if self.enemigo_hp <= 0:
                            self.enemigo_vivo = False
                            print("[+] ¡Enemigo derrotado!")
                    else:
                        print("[-] Fallaste. Ataque al aire.") 

    def dibujar(self):
        self.pantalla.fill((0, 0, 0))
        
        # Dibuja al jugador (tu placeholder)
        self.jugador.dibujar(self.pantalla)
        
        # --- DIBUJAR ENEMIGO ---
        if self.enemigo_vivo:
            # Color (255, 0, 0) es rojo puro
            pygame.draw.rect(self.pantalla, (255, 0, 0), (self.enemigo_x, self.enemigo_y, self.enemigo_tamano, self.enemigo_tamano))
        
        # Dibuja el VFX si está activo
        # (Dentro de def dibujar)
        # (Dentro de def dibujar)    
        # 3. Dibujar el ataque SOLO si está activo
        if self.vfx_activo:
            imagen_actual = self.frames_vfx[int(self.vfx_indice_actual)]
            
            # ---------------------------------------------------------
            # 1. MODIFICA EL ÁNGULO AQUÍ (Para quitar lo diagonal)
            # ---------------------------------------------------------
            # Prueba con 45, 60 o hasta 90 para enderezar esa media luna.
            angulo_extra = -60
            
            # (Tu bloque de if/elif de self.direccion_actual va aquí sin cambios)
            if self.direccion_actual == "derecha":
                imagen_rotada = pygame.transform.rotate(imagen_actual, angulo_extra)
            elif self.direccion_actual == "izquierda":
                imagen_espejo = pygame.transform.flip(imagen_actual, True, False)
                imagen_rotada = pygame.transform.rotate(imagen_espejo, -angulo_extra)
            elif self.direccion_actual == "arriba":
                imagen_rotada = pygame.transform.rotate(imagen_actual, 90 + angulo_extra)
            elif self.direccion_actual == "abajo":
                imagen_rotada = pygame.transform.rotate(imagen_actual, -90 + angulo_extra)

            rectangulo_vfx = imagen_rotada.get_rect()
            centro_jugador_x = self.jugador_x + (self.jugador_tamano // 2)
            centro_jugador_y = self.jugador_y + (self.jugador_tamano // 2)
            
            # ---------------------------------------------------------
            # 2. MODIFICA LA POSICIÓN AQUÍ (Para que abrace al cubo)
            # ---------------------------------------------------------
            # Distancia hacia adelante (Si es muy grande, se aleja del cubo)
            offset_frente = 10  
            
            # Distancia lateral (Si la media luna queda muy arriba o muy abajo del cubo)
            offset_lateral = 0  

            # Aplicamos los offsets según la dirección
            if self.direccion_actual == "derecha":
                rectangulo_vfx.center = (centro_jugador_x + offset_frente, centro_jugador_y + offset_lateral)
            elif self.direccion_actual == "izquierda":
                rectangulo_vfx.center = (centro_jugador_x - offset_frente, centro_jugador_y + offset_lateral)
            elif self.direccion_actual == "abajo":
                rectangulo_vfx.center = (centro_jugador_x + offset_lateral, centro_jugador_y + offset_frente)
            elif self.direccion_actual == "arriba":
                rectangulo_vfx.center = (centro_jugador_x + offset_lateral, centro_jugador_y - offset_frente)

            # Dibujamos en pantalla
            self.pantalla.blit(imagen_rotada, rectangulo_vfx.topleft)
    # --- DIBUJAR INTERFAZ DE INVENTARIO ---
        if self.inventario_abierto:
                        # 1. Dibujamos el título
                        # render("Texto", Antialiasing(suavizado), (R, G, B))
                        titulo = self.fuente.render("--- MOCHILA ---", True, (255, 255, 0)) # Amarillo
                        self.pantalla.blit(titulo, (20, 20)) # Coordenadas X, Y en la esquina superior izquierda
                        
                        # 2. Dibujamos los objetos
                        posicion_y = 60 # Empezamos un poco más abajo del título
                        
                        if not self.mochila.items:
                            texto_vacio = self.fuente.render("El inventario está vacío", True, (200, 200, 200)) # Gris
                            self.pantalla.blit(texto_vacio, (20, posicion_y))
                        else:
                            for item in self.mochila.items:
                                texto = f"{item['nombre']} x{item['cantidad']} ({item['categoria']})"
                                texto_renderizado = self.fuente.render(texto, True, (255, 255, 255)) # Blanco
                                self.pantalla.blit(texto_renderizado, (20, posicion_y))
                                posicion_y += 30 # Bajamos 30 píxeles para el siguiente objeto        
        
            
        # 4. Actualizar pantalla SIEMPRE (Pegado a la izquierda, alineado con el fill)    
        pygame.display.flip()
        
    def ejecutar(self):
        while self.corriendo:
            self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            self.reloj.tick(60)

        pygame.quit()
        sys.exit()
        
    # --- SISTEMA DE INTERFAZ (UI) ---
        pygame.font.init() # Inicializa el motor de texto
        # Usamos Arial, tamaño 24. Si pones None, usa la fuente por defecto.
        self.fuente = pygame.font.SysFont("Arial", 24) 
        
        # Variable booleana para saber si dibujamos el inventario o no
        self.inventario_abierto = False

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()