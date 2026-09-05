# Entregable: Aventura Algorítmica (Semanas 1 a 3)

## 1. Concepto del Juego
**Aventura Algorítmica** es un juego de acción y exploración en 2D con vista cenital (top-down). El jugador asume el rol de un guerrero capaz de explorar mazmorras, enfrentarse a enemigos usando un sistema de combate con combos, y esquivar ataques mediante un "dash" rápido. 

El juego integra mecánicas de estructuras de datos, incluyendo:
*   **Sistema de Inventario:** Gestiona los objetos recolectados mediante listas dinámicas, permitiendo apilar objetos repetidos y respetando un límite de capacidad.
*   **Historial de Acciones:** Un sistema de "rebobinado" estilo pila (LIFO) que guarda las coordenadas anteriores del jugador para deshacer movimientos.
*   **Buscador Integrado:** Algoritmos de búsqueda lineal para encontrar objetos específicos y filtros por categoría dentro de la mochila.

## 2. Estructura de Archivos (Guía 1)
La carpeta del proyecto sigue un orden lógico para separar los recursos visuales de la lógica de programación:

*   **assets/**: Recursos gráficos (sprites del jugador y efectos visuales).
*   **main.py**: Bucle principal y renderizado del juego.
*   **inventario.py**: Lógica y almacenamiento de la mochila (Listas).
*   **jugador.py**: Máquina de estados, animación y físicas.
*   **buscador.py**: Algoritmos de búsqueda y filtrado.
*   **historial.py**: Sistema de deshacer movimientos (Pila LIFO).
*   **eventos.py**: Gestor de combos y daños (Cola FIFO).
*   **mapas.py**: Matriz de la sala inicial.
*   **README.md**: Este documento de documentación.

## 3. Diagrama de Flujo y Pseudocódigo (Mecánica: Inventario)
A continuación, se detalla el comportamiento del sistema de inventario, el cual se encarga de recibir objetos, verificar si ya existen para apilarlos, o agregarlos a un nuevo espacio si la capacidad lo permite.

**Pseudocódigo de la función `agregar_item`:**
    INICIO agregar_item(nombre, categoria, cantidad)
        // 1. Verificar si el objeto ya existe para apilarlo
        PARA CADA item EN mochila.items:
            SI item.nombre ES IGUAL A nombre ENTONCES:
                item.cantidad = item.cantidad + cantidad
                MOSTRAR "Se sumaron [cantidad] de [nombre]"
                RETORNAR Verdadero
            FIN SI
        FIN PARA

        // 2. Si no existe, verificar si hay espacio en la mochila
        SI TAMAÑO_DE(mochila.items) < capacidad_maxima ENTONCES:
            NUEVO_ITEM = {nombre, categoria, cantidad}
            AÑADIR NUEVO_ITEM A mochila.items
            MOSTRAR "Nuevo objeto recogido"
            RETORNAR Verdadero
        SINO:
            MOSTRAR "Inventario lleno"
            RETORNAR Falso
        FIN SI
    FIN

*(Nota: El diagrama de flujo correspondiente a este pseudocódigo se basa en las mismas decisiones lógicas: verificar existencia en lista -> si existe, sumar; si no, verificar espacio -> si hay espacio, agregar nuevo; si no, rechazar).*

## 4. Evidencia de Ejecución del Inventario
El sistema de inventario funciona correctamente en el entorno gráfico con listas en Python. Al presionar la tecla **'I'**, se abre la interfaz de la mochila. Al presionar **'F'**, el sistema simula la recolección de una `"Llave Antigua"`, agregándola a la lista subyacente de Python e imprimiendo la confirmación en la consola. La interfaz gráfica se actualiza en tiempo real mostrando los objetos y sus cantidades.