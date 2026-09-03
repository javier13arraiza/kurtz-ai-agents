import random
import numpy as np
from queue import Queue


# MODELO Y GENERACIÓN

class Celda:
    """
    Representa una celda del entorno (el palacio).

    Atributos:
        celda (str): Contenido visual de la celda ("⬜", "🟧", "🟩", " S", " P", "CK").
        brisa (bool): Indica si hay brisa (cerca de precipicio).
        ronquido (bool): Indica si se oye ronquido (cerca de soldado).
        resplandor (bool): Indica si hay luz (cerca de salida).
        pared_N/S/E/O (bool): Indican si hay una pared en una de las direcciones.
        grito (bool): Indica si la celda del soldado donde se arroja la granada es transitable (es decir, "matamos" a este soldado).
        es_salida (bool): True si la celda es la salida.
        tengo_CK (bool): True si el capitán lleva al coronel con él.
    
    """
    def __init__(self):
        self.celda = "⬜"
        self.brisa = False
        self.ronquido = False
        self.resplandor = False
        self.pared_N = False
        self.pared_S = False
        self.pared_E = False
        self.pared_O = False
        self.grito = False
        self.es_salida = False
        self.tengo_CK = False

def pos_capitan(dicc_entorno:dict[tuple[int,int], Celda]):
    """
    Busca dónde está el capitán (🟧) en el diccionario del entorno.

    Devuelve la posicion (tupla) del Capitan Willard

    """
    for (x, y) in dicc_entorno.keys():
        if dicc_entorno[(x,y)].celda == "🟧":
            return (x, y)

def actualizar_matriz(dicc_entorno: dict[tuple[int,int], Celda]):
    """
    Convierte el diccionario del entorno en una matriz tipo lista de strings
    para mostrarla en pantalla.

    Inputs:
        dicc_entorno (dict): Diccionario de coordenadas a objetos Celda.

    Returns:
        list[str]: filas de la matriz con los emojis de cada celda.

    """
    matriz_entorno = []
    for i in range(int(np.sqrt(len(dicc_entorno)))):
        fila = f"{i+1:<3} "   # coordenada de fila
        for j in range(int(np.sqrt(len(dicc_entorno)))):
            fila = fila + dicc_entorno[(i+1,j+1)].celda
        matriz_entorno.append(fila)

    return matriz_entorno

def imprimir_matriz(matriz: list[str]):
    """
    Imprime en consola una matriz representada como lista de strings.

    """
    n = 6  # número de celdas aproximado
    cabecera = "     "
    for j in range(1, n + 1):
        cabecera += f"{j:^2}" 
    print(cabecera)

    for fila in matriz:
        print(fila)

def comprobaciones(dicc_entorno: dict[tuple[int,int], Celda], campo_comprobacion: str, celda_mod:str, modo: bool):
    """
    Marca celdas adyacentes con un atributo booleano (brisa, ronquido, resplandor).

    Inputs:
        dicc_entorno (dict): Entorno del palacio.
        campo_comprobacion (str): Nombre del atributo a modificar.
        celda_mod (str): Tipo de celda que genera el efecto (ej. " P" para brisa).
        modo(bool)

    """
    for (i,j), celda in dicc_entorno.items():
        if celda.celda == celda_mod:
            celdas_ady = [(i+1,j), (i-1,j), (i,j+1), (i,j-1), (i,j)]
            for celda_pos in celdas_ady:
                try:
                    setattr(dicc_entorno[celda_pos], campo_comprobacion, modo)
                except:
                    pass

    return dicc_entorno

def entorno_del_palacio(n:int):
    """
    Genera un tablero NxN con elementos del juego colocados aleatoriamente.

    Inputs:
        n (int): Dimensiones del tablero (n x n).

    Returns:
        dict: Diccionario cuya clave es (x,y) y valor es una Celda(). (base del juego)

    """
    dicc_entorno = {}
    for i in range(n):
        for j in range(n):
            dicc_entorno[(i+1,j+1)] = Celda()

    # Coloca entrada
    (x_entrada, y_entrada) = (1,1)
    dicc_entorno[(x_entrada, y_entrada)].celda = "🟧"

    # Coloca salida
    (x_salida, y_salida) = (x_entrada, y_entrada)
    while (x_salida, y_salida) == (x_entrada, y_entrada):
        (x_salida, y_salida) = (random.randint(1,n), random.randint(1,n))
    dicc_entorno[(x_salida, y_salida)].celda = "🟩"
    dicc_entorno[(x_salida, y_salida)].es_salida = True

    # Precipicios
    for _ in range(3):
        (x_precipicio, y_precipicio) = (random.randint(1,n), random.randint(1,n))
        while dicc_entorno[(x_precipicio, y_precipicio)].celda != "⬜":
            (x_precipicio, y_precipicio) = (random.randint(1,n), random.randint(1,n))
        dicc_entorno[(x_precipicio, y_precipicio)].celda =  " P"

    # Soldado
    (x_soldado, y_soldado) = (random.randint(1,n), random.randint(1,n))
    while dicc_entorno[(x_soldado, y_soldado)].celda != "⬜":
        (x_soldado, y_soldado) = (random.randint(1,n), random.randint(1,n))
    dicc_entorno[(x_soldado, y_soldado)].celda =  " S"
    
    # Kurtz
    (x_coronel, y_coronel) = (random.randint(1,n), random.randint(1,n))
    while dicc_entorno[(x_coronel, y_coronel)].celda != "⬜":
        (x_coronel, y_coronel) = (random.randint(1,n), random.randint(1,n))
    dicc_entorno[(x_coronel, y_coronel)].celda = "CK"

    # Paredes y percepciones
    for (i, j), celda in dicc_entorno.items():
        if i == 1: celda.pared_N = True
        if i == n: celda.pared_S = True
        if j == 1: celda.pared_O = True
        if j == n: celda.pared_E = True

    dicc_entorno = comprobaciones(dicc_entorno, "brisa", " P", True)
    dicc_entorno = comprobaciones(dicc_entorno, "ronquido", " S", True)
    dicc_entorno = comprobaciones(dicc_entorno, "resplandor", "🟩", True)

    return dicc_entorno


# ACCIONES DEL JUEGO

def accion_mover(dicc_entorno:dict[tuple[int,int], Celda], mov_vertical:int, mov_horizonal:int):
    """
    Mueve al capitán en la dirección indicada si no hay pared ni muerte.

    Inputs:
        dicc_entorno (dict)
        mov_vertical (int): -1 arriba, 1 abajo, 0 sin cambio
        mov_horizonal (int): -1 izquierda, 1 derecha, 0 sin cambio

    Returns:
        (tuple, dict): ((nx,ny), diccionario actualizado)

    """
    # Localizamos la posición del capitán
    (x_actual, y_actual) = pos_capitan(dicc_entorno)

    celda_actual = dicc_entorno[(x_actual, y_actual)]

    # Paredes
    if mov_vertical == -1 and celda_actual.pared_N: return (x_actual, y_actual), dicc_entorno
    if mov_vertical == 1 and celda_actual.pared_S:  return (x_actual, y_actual), dicc_entorno
    if mov_horizonal == -1 and celda_actual.pared_O: return (x_actual, y_actual), dicc_entorno
    if mov_horizonal == 1 and celda_actual.pared_E:  return (x_actual, y_actual), dicc_entorno

    nx, ny = x_actual + mov_vertical, y_actual + mov_horizonal
    if (nx, ny) not in dicc_entorno:
        return (x_actual, y_actual), dicc_entorno

    celda_destino = dicc_entorno[(nx, ny)]

    # Salimos de la celda actual
    if celda_actual.celda == "🟧":
        celda_actual.celda = "⬜"
        if celda_actual.tengo_CK:
            celda_destino.tengo_CK = True

    if celda_actual.es_salida:
        celda_actual.celda = "🟩"

    # Entramos en la celda nueva
    if celda_destino.es_salida:
        celda_destino.celda = "🟧"
        return (nx,ny), dicc_entorno

    # Muere por precipicio o soldado
    if celda_destino.celda == " P": return (nx,ny), dicc_entorno
    if celda_destino.celda == " S": return (nx,ny), dicc_entorno

    # Marcamos que estamos ya con CK
    if celda_destino.celda == "CK":
        celda_destino.celda = "🟧"
        celda_destino.tengo_CK = True
    else:
        celda_destino.celda = "🟧"

    return (nx, ny), dicc_entorno

def accion_granada(dicc_entorno:dict[tuple[int,int], Celda], lanzamiento_vertical:int, lanzamiento_horizontal:int):
    """
    Lanza una granada en una casilla adyacente (solo 1 casilla en línea recta).

    Inputs:
        dicc_entorno (dict)
        lanzamiento_vertical (int)
        lanzamiento_horizontal (int)

    Returns:
        dict: entorno actualizado

    """
    global granada

    if not granada:
        if (lanzamiento_vertical, lanzamiento_horizontal) not in [(1,0),(0,1),(-1,0),(0,-1)]:
            return dicc_entorno
        
        # Localizamos la posición del capitán
        (x_actual, y_actual) = pos_capitan(dicc_entorno)
        
        nx, ny = x_actual + lanzamiento_vertical, y_actual + lanzamiento_horizontal
        if (nx, ny) not in dicc_entorno: return dicc_entorno
        
        if dicc_entorno[(nx,ny)].celda == " S":
            # Quitamos al militar y el ronquido
            dicc_entorno = comprobaciones(dicc_entorno, "ronquido", " S", False)
            dicc_entorno[(nx,ny)].celda = "⬜"
            granada = True
            dicc_entorno[(x_actual, y_actual)].grito = True
        else:
            print("No has acertado... Te has quedado sin granada!")
            granada = True
            
    else:
        print("Ya has utilizado la granada, solo tenias una...")
        return dicc_entorno

    return dicc_entorno

def accion_salir(dicc_entorno:dict[tuple[int,int], Celda]):
    """
    Intenta salir del palacio.

    Inputs:
        dicc_entorno (dict)
    
    Returns:
        dict (solo devuelve dicc_entorno)

    """
    # Localizamos la posición del capitán
    (x_actual, y_actual) = pos_capitan(dicc_entorno)

    if dicc_entorno[(x_actual, y_actual)].es_salida and dicc_entorno[(x_actual, y_actual)].tengo_CK:
        print(f"\nHas ganado! Has conseguido salir con el Coronel Kurtz.")
        dicc_entorno[(x_actual, y_actual)].celda = "⬜"
        return dicc_entorno, True
    elif dicc_entorno[(x_actual, y_actual)].es_salida:
        print(f"\nNo tienes al Coronel Kurtz...")
        return dicc_entorno, False
    elif dicc_entorno[(x_actual, y_actual)].tengo_CK:
        print(f"\nEsa no es la salida...")
        return dicc_entorno, False
    else:
        print(f"\nNo es ni la salida ni tienes al Coronel Kurtz.")
        return dicc_entorno, False

def imprimir_info(dicc_entorno:dict[tuple[int,int], Celda], x:int, y:int):
    print("ESTADO ACTUAL")
    print("-" * 40)
    print(f"Posicion: ({x}, {y})")
    print(f"Brisa      : {dicc_entorno[(x,y)].brisa}")
    print(f"Ronquido   : {dicc_entorno[(x,y)].ronquido}")
    print(f"Resplandor : {dicc_entorno[(x,y)].resplandor}")
    print(f"Grito      : {dicc_entorno[(x,y)].grito}")
    print("-" * 40)
    print("PAREDES")
    print(f"Norte: {dicc_entorno[(x,y)].pared_N} | Sur: {dicc_entorno[(x,y)].pared_S} | Oeste: {dicc_entorno[(x,y)].pared_O} | Este: {dicc_entorno[(x,y)].pared_E}")
    print("-" * 40)
    print("OBJETIVO")
    print(f"Es salida  : {dicc_entorno[(x,y)].es_salida}")
    print(f"Tengo CK   : {dicc_entorno[(x,y)].tengo_CK}")
    print("-" * 40)


# JUEGO INTERACTIVO

def juego_interactivo(n:int, mapa_visible:bool=True):
    """
    Juego controlado por el usuario mediante teclado.

    Inputs:
        n (int): tamaño del tablero.
        mapa_visible (bool): Si True, imprime el mapa.
   
    """
    global granada
    granada = False
    dicc_entorno = entorno_del_palacio(n)
    (x, y) = (1,1)

    print("\n--- INICIO DEL JUEGO ---\n")

    while True:

        imprimir_info(dicc_entorno, x, y)

        if mapa_visible:
            imprimir_matriz(actualizar_matriz(dicc_entorno))

        accion = input("Acción: W,A,S,D,G(granada),X(intenatar salir) ")

        if accion.upper() in ["W","A","S","D"]:
            if accion.upper()=="W": (x,y),dicc_entorno = accion_mover(dicc_entorno,-1,0)
            if accion.upper()=="A": (x,y),dicc_entorno = accion_mover(dicc_entorno,0,-1)
            if accion.upper()=="S": (x,y),dicc_entorno = accion_mover(dicc_entorno,1,0)
            if accion.upper()=="D": (x,y),dicc_entorno = accion_mover(dicc_entorno,0,1)

            if dicc_entorno[(x,y)].celda in [" P", " S"]:
                if dicc_entorno[(x,y)].celda == " P":
                    print(f"\nHas perdido... Has caido en un precipicio.")
                elif dicc_entorno[(x,y)].celda == " S":
                    print(f"\nHas perdido... Te ha encontrado un soldado.")
                break
                

        elif accion.upper()=="G":
            movimiento_str = input("Donde lanzar: (W,A,S,D) ")
            if movimiento_str.upper() == "W":
                dicc_entorno = accion_granada(dicc_entorno, -1, 0)
            elif movimiento_str.upper() == "A":
                dicc_entorno = accion_granada(dicc_entorno, 0, -1)
            elif movimiento_str.upper() == "S":
                dicc_entorno = accion_granada(dicc_entorno, 1, 0)
            elif movimiento_str.upper() == "D":
                dicc_entorno = accion_granada(dicc_entorno, 0, 1)
            else:
                print("No he entendido la direccion.")
            

        elif accion.upper()=="X":
            tupla_salir = accion_salir(dicc_entorno)
            dicc_entorno = tupla_salir[0]
            if tupla_salir[1]:
                break
        else:
            print(f"\nUPS! No he entendido eso.")


# JUEGO AUTOMÁTICO

def construir_celdas_seguras(dicc_entorno:dict[tuple[int,int], Celda]):
    """
    Construye un conjunto de celdas consideradas seguras.

    Inputs:
        dicc_entorno (dict)

    Returns:
        set: coordenadas seguras

    """
    seguras = set()
    for (x, y), celda in dicc_entorno.items():
        if celda.celda not in [" P", " S"]:
            seguras.add((x, y))
    return seguras

def buscar_objetos(dicc_entorno:dict[tuple[int,int], Celda], objeto:str):
    """
    Busca posiciones clave en el tablero.

    Inputs:
        dicc_entorno (dict)
        objeto (str): "Inicio", "Kurtz", "Salida"

    Returns:
        tuple[int,int] | None

    """
    for (x, y) in dicc_entorno.keys():
        contenido = dicc_entorno[(x, y)].celda
        if objeto=="Inicio" and contenido=="🟧":
            return (x,y)
        elif objeto =="Kurtz" and contenido=="CK":
            return (x,y)
        elif objeto=="Salida" and contenido=="🟩":
            return (x,y)
    return None

def bfs_plan(dicc_entorno:dict[tuple[int,int], Celda], celdas_seguras:set):
    """
    Algoritmo BFS (Breadth First Search) para encontrar:
        Inicio → Kurtz → Salida

    Inputs:
        dicc_entorno (dict)
        celdas_seguras (set)

    Returns:
        list[str] | None: lista de acciones ["A","S",...] o None si imposible

    """
    pos_inicial = buscar_objetos(dicc_entorno,"Inicio")
    pos_kurtz = buscar_objetos(dicc_entorno,"Kurtz")
    pos_salida = buscar_objetos(dicc_entorno,"Salida")

    if pos_inicial is None or pos_kurtz is None or pos_salida is None:
        return None

    estado_inicial = (pos_inicial, False)

    cola = Queue()
    cola.put(estado_inicial)

    padre = {estado_inicial: None}
    accion_padre = {estado_inicial: None}

    while not cola.empty():
        (x,y), tengo_ck = cola.get()

        if tengo_ck and (x, y) == pos_salida:
            plan = []
            estado = ((x, y), tengo_ck)
            while accion_padre[estado] is not None:
                plan.append(accion_padre[estado])
                estado = padre[estado]
            plan.reverse()
            return plan

        for accion, dx, dy in [("W", -1, 0),("S", 1, 0),("A", 0, -1),("D", 0, 1)]:
            nx,ny = x+dx, y+dy
            nueva_pos = (nx,ny)

            if nueva_pos not in dicc_entorno:
                continue

            if nueva_pos not in celdas_seguras:
                continue

            nuevo_tengo_ck = tengo_ck or (nueva_pos == pos_kurtz)
            nuevo_estado = (nueva_pos, nuevo_tengo_ck)

            if nuevo_estado not in padre:
                padre[nuevo_estado] = ((x,y),tengo_ck)
                accion_padre[nuevo_estado] = accion
                cola.put(nuevo_estado)

    return None

def ejecutar_plan(dicc_entorno:dict[tuple[int,int], Celda], plan:list, mapa_visible:bool=True):
    """
    Ejecuta en el tablero una lista de acciones generada por BFS.

    Inputs:
        dicc_entorno (dict)
        plan (list[str])
        mapa_visible (bool)

    Returns:
        dict: entorno final tras ejecutar el plan

    """
    pos_inicial = buscar_objetos(dicc_entorno, "Inicio")
    if pos_inicial is None:
        return dicc_entorno

    for accion in plan:
        if accion == "W": dx, dy = -1, 0
        elif accion == "S": dx, dy = 1, 0
        elif accion == "A": dx, dy = 0, -1
        elif accion == "D": dx, dy = 0, 1

        dicc_entorno = accion_mover(dicc_entorno, dx, dy)[1]

        if mapa_visible:
            print()
            imprimir_matriz(actualizar_matriz(dicc_entorno))

    return dicc_entorno

def juego_automatico(n:int, mapa_visible:bool=True):
    """
    Juega solo:
        · genera mapa
        · calcula BFS
        · lo ejecuta automáticamente

    """
    dicc_entorno = entorno_del_palacio(n)

    celdas_seguras = construir_celdas_seguras(dicc_entorno)
    plan = bfs_plan(dicc_entorno, celdas_seguras)

    print(f"Plan: {plan}")

    if mapa_visible:
        imprimir_matriz(actualizar_matriz(dicc_entorno))

    if plan is None:
        print("No hay plan seguro.")
        return

    ejecutar_plan(dicc_entorno, plan, mapa_visible)
    tupla_salir = accion_salir(dicc_entorno)
    dicc_entorno = tupla_salir[0]
    if tupla_salir[1]:
        return            


# MAIN

def main():

    print("--- MENU ---\n1: Interactivo\n2: BFS")
    tipo = input("Modo: ")

    if tipo=="1":
        m = input("Mapa visible? (Y/N) ")
        juego_interactivo(6, m.upper()=="Y")
    elif tipo=="2":
        m = input("Mapa visible? (Y/N) ")
        juego_automatico(6, m.upper()=="Y")

if __name__=="__main__":
    main()

