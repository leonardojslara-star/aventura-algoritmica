import pygame
import sys

# LEYENDA DEL MAPA - TILESET CAINOS 
# 0 = Suelo transitable (Pasto o baldosas de piedra)
# 1 = Muro de piedra (Colisión - No caminable)
# 2 = Obstáculo interno (Ej. La estatua o los faroles/pilares de piedra)
# 3 = Transición a otra sala (Ej. Las escaleras que se ven en la imagen)
# 8 = Objeto especial: El Corazón de Cuarzo Roto
# 9 = Spawn de Jarek 
# 10 = Spawn de Makhai

# Inicializar Pygame
pygame.init()

# ¡NUEVA CONFIGURACIÓN! Tamaño nativo del tileset
TAMANO_TILE = 32
COLUMNAS = 15  # Aumentamos un poco la matriz para que la sala no sea tan chica
FILAS = 11
ANCHO_VENTANA = COLUMNAS * TAMANO_TILE
ALTO_VENTANA = FILAS * TAMANO_TILE

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Mazmorra - Sala de Inicio")

# Colores temporales para probar tu matriz
COLOR_SUELO = (50, 50, 50)     
COLOR_MURO = (100, 100, 100)   
COLOR_PUERTA = (139, 69, 19)   
COLOR_SPAWN = (0, 255, 0)      

# MATRIZ AMPLIADA (15x11)
sala_inicio = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3], # 9 = Jarek, 3 = Puerta
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3], # Puerta más ancha (2 bloques)
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

ejecutando = True
while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            valor = sala_inicio[fila][columna]
            x = columna * TAMANO_TILE
            y = fila * TAMANO_TILE

            if valor == 0:
                pygame.draw.rect(pantalla, COLOR_SUELO, (x, y, TAMANO_TILE, TAMANO_TILE))
            elif valor == 1:
                pygame.draw.rect(pantalla, COLOR_MURO, (x, y, TAMANO_TILE, TAMANO_TILE))
            elif valor == 3:
                pygame.draw.rect(pantalla, COLOR_PUERTA, (x, y, TAMANO_TILE, TAMANO_TILE))
            elif valor == 9:
                pygame.draw.rect(pantalla, COLOR_SPAWN, (x, y, TAMANO_TILE, TAMANO_TILE))

            pygame.draw.rect(pantalla, (0, 0, 0), (x, y, TAMANO_TILE, TAMANO_TILE), 1)

    pygame.display.flip()

pygame.quit()
sys.exit()