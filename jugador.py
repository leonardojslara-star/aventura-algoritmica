import pygame

class Jugador:
    def __init__(self, x, y):
        # Propiedades físicas
        self.x = x
        self.y = y
        self.tamano = 100
        self.velocidad = 2.5
        
        # --- LA MÁQUINA DE ESTADOS ---
        # El personaje siempre debe saber qué está haciendo y hacia dónde mira
        self.estado_actual = "idle"  # Puede ser: "idle", "correr", "ataque_1", "ataque_2"
        self.direccion_actual = "derecha" # Puede ser: "derecha", "izquierda", "arriba", "abajo"
        self.combo_solicitado = False
        
        # --- SISTEMA DE ANIMACIÓN ---
        self.indice_frame = 0
        self.velocidad_animacion = 0.4
        
        frames_dash_base = self.cortar_spritesheet_cuadricula("assets/jugador/RUN/dash.png", 4, 2, 7, escala_personalizada=(60, 60))
        
        # Diccionario principal: Aquí cargaremos todas tus imágenes ordenadas
        self.animaciones = {
            "idle_derecha": self.cortar_spritesheet("assets/jugador/IDLE/idle_right.png", 8),
            "idle_izquierda": self.cortar_spritesheet("assets/jugador/IDLE/idle_left.png", 8),
            "idle_arriba": self.cortar_spritesheet("assets/jugador/IDLE/idle_up.png", 8),
            "idle_abajo": self.cortar_spritesheet("assets/jugador/IDLE/idle_down.png", 8),
            "correr_derecha": self.cortar_spritesheet("assets/jugador/RUN/run_right.png", 8),
            "correr_izquierda": self.cortar_spritesheet("assets/jugador/RUN/run_left.png", 8),
            "correr_arriba": self.cortar_spritesheet("assets/jugador/RUN/run_up.png", 8),
            "correr_abajo": self.cortar_spritesheet("assets/jugador/RUN/run_down.png", 8),
            "ataque_1_derecha": self.cortar_spritesheet("assets/jugador/ATTACK_1/attack1_right.png", 8),
            "ataque_1_izquierda": self.cortar_spritesheet("assets/jugador/ATTACK_1/attack1_left.png", 8),
            "ataque_1_arriba": self.cortar_spritesheet("assets/jugador/ATTACK_1/attack1_up.png", 8),
            "ataque_1_abajo": self.cortar_spritesheet("assets/jugador/ATTACK_1/attack1_down.png", 8),
            "ataque_2_derecha": self.cortar_spritesheet("assets/jugador/ATTACK_2/attack2_right.png", 8),
            "ataque_2_izquierda": self.cortar_spritesheet("assets/jugador/ATTACK_2/attack2_left.png", 8),
            "ataque_2_arriba": self.cortar_spritesheet("assets/jugador/ATTACK_2/attack2_up.png", 8),
            "ataque_2_abajo": self.cortar_spritesheet("assets/jugador/ATTACK_2/attack2_down.png", 8),
            "dash_derecha": frames_dash_base,
            "dash_izquierda": self.transformar_frames(frames_dash_base, voltear_x=True),
            
            # ¡Le pedimos que corte el polvo ANTES de rotar!
            "dash_arriba": self.transformar_frames(frames_dash_base, angulo=90, recortar_abajo=25),
            "dash_abajo": self.transformar_frames(frames_dash_base, angulo=-90, recortar_abajo=25),
        }
        
        # Placeholder temporal para no romper el juego mientras metes las imágenes reales
        self.placeholder = pygame.Surface((self.tamano, self.tamano))
        self.placeholder.fill((0, 255, 0))

    def cambiar_estado(self, nuevo_estado):
        """Evita que la animación se reinicie si ya estamos en ese estado."""
        if self.estado_actual != nuevo_estado:
            self.estado_actual = nuevo_estado
            self.indice_frame = 0 # Reiniciamos el contador al cambiar de acción

    def actualizar_animacion(self):
        """Avanza los fotogramas y gestiona el fin de las animaciones."""
        clave = f"{self.estado_actual}_{self.direccion_actual}"
        frames = self.animaciones.get(clave, [])
        
        # --- ¡ESTAS DOS LÍNEAS ERAN LAS QUE FALTABAN! ---
        if len(frames) > 0:
            self.indice_frame += self.velocidad_animacion
        
            # ¿Qué pasa cuando el fotograma llega al final?
            if self.indice_frame >= len(frames):
                    
                # Si terminamos el Ataque 1 y el jugador pidió un combo...
                if self.estado_actual == "ataque_1" and self.combo_solicitado:
                    self.cambiar_estado("ataque_2")
                    self.combo_solicitado = False # Limpiamos la memoria
                        
                # Si terminamos cualquier ataque pero NO hay combo, regresamos a idle
                elif "ataque" in self.estado_actual:
                    self.cambiar_estado("idle")
                    self.combo_solicitado = False
                    
                # Si terminamos cualquier ataque pero NO hay combo, regresamos a idle
                elif "ataque" in self.estado_actual:
                    self.cambiar_estado("idle")
                    self.combo_solicitado = False
                
                # --- NUEVO: Si terminamos de esquivar, volvemos a idle ---
                elif self.estado_actual == "dash":
                    self.cambiar_estado("idle")
                        
                # Si es idle o correr, hacemos un bucle infinito
                else:
                    self.indice_frame = 0

            
                    
    def cortar_spritesheet(self, ruta, cantidad_frames):
        """Toma una tira de imágenes y la recorta en fotogramas individuales."""
        # 1. Cargamos la imagen larga
        hoja_completa = pygame.image.load(ruta).convert_alpha()
        
        # 2. Medimos cuánto mide de ancho y de alto en total
        ancho_total = hoja_completa.get_width()
        alto_total = hoja_completa.get_height()
        
        # 3. Calculamos el ancho de UN SOLO personaje
        ancho_frame = ancho_total // cantidad_frames
        
        frames_recortados = []
        
        # 4. Hacemos los cortes
        for i in range(cantidad_frames):
            # pygame.Rect(posicion_x, posicion_y, ancho, alto)
            rectangulo_corte = pygame.Rect(i * ancho_frame, 0, ancho_frame, alto_total)
            
            # subsurface "recorta" la imagen usando el rectángulo
            frame = hoja_completa.subsurface(rectangulo_corte)
            
            # (Opcional) Escalamos el recorte al tamaño de tu hitbox (40x40)
            frame_escalado = pygame.transform.scale(frame, (self.tamano, self.tamano))
            
            frames_recortados.append(frame_escalado)
            
        return frames_recortados
    
    def cortar_spritesheet_cuadricula(self, ruta, columnas, filas, total_frames, escala_personalizada=None):
        """Recorta spritesheets que vienen en formato de matriz (filas y columnas)."""
        hoja_completa = pygame.image.load(ruta).convert_alpha()
        
        ancho_total = hoja_completa.get_width()
        alto_total = hoja_completa.get_height()
        
        ancho_frame = ancho_total // columnas
        alto_frame = alto_total // filas
        
        frames_recortados = []
        frames_extraidos = 0
        
        # Si no le pasamos un tamaño especial, usa el tamaño base del jugador (100)
        t_ancho = escala_personalizada[0] if escala_personalizada else self.tamano
        t_alto = escala_personalizada[1] if escala_personalizada else self.tamano
        
        for fila in range(filas):
            for columna in range(columnas):
                if frames_extraidos >= total_frames:
                    break
                    
                rect_x = columna * ancho_frame
                rect_y = fila * alto_frame
                rectangulo_corte = pygame.Rect(rect_x, rect_y, ancho_frame, alto_frame)
                
                frame = hoja_completa.subsurface(rectangulo_corte)
                
                # --- AQUÍ APLICAMOS EL NUEVO TAMANO ---
                frame_escalado = pygame.transform.scale(frame, (t_ancho, t_alto))
                frames_recortados.append(frame_escalado)
                
                frames_extraidos += 1
                
        return frames_recortados
    
    def transformar_frames(self, frames, voltear_x=False, voltear_y=False, angulo=0, recortar_abajo=0):
        """Toma una lista de fotogramas y los recorta, voltea o rota matemáticamente."""
        frames_modificados = []
        for frame in frames:
            frame_actual = frame
            
            # 1. ¡NUEVO! Recortar el "polvo" de la parte inferior
            if recortar_abajo > 0:
                ancho = frame_actual.get_width()
                alto = frame_actual.get_height()
                
                # Asegurarnos de no intentar cortar más de lo que mide la imagen
                if recortar_abajo < alto:
                    # Hacemos un rectángulo que va desde arriba (0,0) pero que de alto mide menos
                    rect_corte = pygame.Rect(0, 0, ancho, alto - recortar_abajo)
                    frame_actual = frame_actual.subsurface(rect_corte)
            
            # 2. Aplicamos el efecto espejo (Flip)
            frame_actual = pygame.transform.flip(frame_actual, voltear_x, voltear_y)
            
            # 3. Aplicamos la rotación
            if angulo != 0:
                frame_actual = pygame.transform.rotate(frame_actual, angulo)
                
            frames_modificados.append(frame_actual)
            
        return frames_modificados

    def dibujar(self, pantalla):
        """Dibuja el fotograma correcto en la pantalla, encimando el dash si es necesario."""
        
        # 1. CASO ESPECIAL: Si está haciendo un dash, primero dibujamos al personaje corriendo
        if self.estado_actual == "dash":
            # Buscamos los frames de correr en la dirección actual para el cuerpo del personaje
            clave_cuerpo = f"correr_{self.direccion_actual}"
            frames_cuerpo = self.animaciones.get(clave_cuerpo, [])
            
            if len(frames_cuerpo) > 0:
                idx_cuerpo = int(self.indice_frame) % len(frames_cuerpo)
                pantalla.blit(frames_cuerpo[idx_cuerpo], (self.x, self.y))
                
            # Ahora buscamos el efecto visual del dash para encimarlo
            clave_efecto = f"dash_{self.direccion_actual}"
            frames_efecto = self.animaciones.get(clave_efecto, [])
            
            if len(frames_efecto) > 0:
                idx_efecto = int(self.indice_frame) % len(frames_efecto)
                
                # --- VARIABLES DE AJUSTE (OFFSETS) ---
                offset_x = 0
                offset_y = 0
                
                if self.direccion_actual == "derecha":
                    offset_x = -5
                    offset_y = 30
                elif self.direccion_actual == "izquierda":
                    offset_x = 45
                    offset_y = 25
                elif self.direccion_actual == "abajo":
                    offset_x = 30
                    offset_y = 0
                elif self.direccion_actual == "arriba":
                    offset_x = 30
                    offset_y = 50
                
                # Dibujamos el efecto aplicando el desfase matemático
                pantalla.blit(frames_efecto[idx_efecto], (self.x + offset_x, self.y + offset_y))

        # 2. CASO NORMAL: ¡ESTA ES LA PARTE QUE TE FALTABA!
        else:
            clave = f"{self.estado_actual}_{self.direccion_actual}"
            frames = self.animaciones.get(clave, [])
            
            if len(frames) > 0:
                imagen_actual = frames[int(self.indice_frame)]
                pantalla.blit(imagen_actual, (self.x, self.y))
            else:
                # Si la lista está vacía, dibuja el cuadro verde de seguridad
                pantalla.blit(self.placeholder, (self.x, self.y))