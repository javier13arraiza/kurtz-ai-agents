import random
import river_mdp


# MODELO Y GENERACIÓN

class Celda:
    """
    Representa una celda del entorno (el palacio).

    Atributos:
        celda (str): Contenido visual de la celda ("⬜", "🟧", "🟩", " S", " P", "CK").

        fuego/pinchos/dardos (bool): Indica si hay una trampa de fuego/pinchos/dardos en alguna celda adyacente.
        
        ronquido (bool): Indica si se oye ronquido (cerca de soldado).
        es_salida (bool): True si la celda es la salida.
        tengo_CK (bool): True si el capitán lleva al coronel con él.

        pared_N/S/E/O (bool): Indican si hay una pared en una de las direcciones.
        grito (bool): Indica si la celda del soldado donde se arroja la granada es transitable (es decir, "matamos" a este soldado).
        
    """
    def __init__(self):
        self.celda = ["⬜"]

        self.fuego_ady = False
        self.pinchos_ady = False
        self.dardos_ady = False

        self.ronquido = False
        self.es_salida = False
        self.tengo_CK = False

        self.pared_N = False
        self.pared_S = False
        self.pared_E = False
        self.pared_O = False
        self.grito = False
        self.resplandor = False

def pos_capitan(dicc_entorno: dict[tuple[int, int], Celda]):
    """
    Busca dónde está el capitán (🟧) en el diccionario del entorno.

    Devuelve la posicion (tupla) del Capitan Willard

    """
    for (x, y) in dicc_entorno.keys():
        if "🟧" in dicc_entorno[(x,y)].celda:
            return (x, y)
    return None

# Funciones que me ayudan para no repetir la lógica todo el rato
def eliminar(celda_obj: Celda, item: str):
    """
    Elimina un item del atributo celda (contenido visual) de una Celda.
    Si la celda se queda vacía, vuelve a ["⬜"].

    """
    if item in celda_obj.celda:
        celda_obj.celda.remove(item)
    if len(celda_obj.celda) == 0:
        celda_obj.celda = ["⬜"]

def añadir(celda_obj: Celda, item: str):
    """
    Añade un item al tributo celda (contenido visual) de una Celda.
    Si estaba vacía ["⬜"], la sustituye directamente por item.

    """
    if "⬜" in celda_obj.celda:
        celda_obj.celda = [item]
    else:
        if item not in celda_obj.celda:
            celda_obj.celda.append(item)

def es_adyacente(pos_actual: tuple[int, int],pos_ady:tuple[int, int]):
    """
    Devuelve True si pos_ady está a distancia Manhattan 1 de pos_actual (arriba/abajo/izquierda/derecha)
    
    """
    if abs(pos_actual[0] - pos_ady[0]) == 0 and abs(pos_actual[1] - pos_ady[1]) == 1:
        return True
    if abs(pos_actual[0] - pos_ady[0]) == 1 and abs(pos_actual[1] - pos_ady[1]) == 0:
        return True
    else:
        return False


def celda_caja(contenido: list[str]) -> str:
    """
    Convierte contenido (list[str]) a formato compacto tipo [  |  |  ].

    - Trampas (F,P,D): Fuego, Pinchos, Dardos
    - Personas (M, CK): Militar y Coronel Kurtz
    - Bloques vacíos -> espacios
    - Entrada -> 🟧
    - Salida -> 🟩

    """
    # Blanco
    if contenido == ["⬜"]:
        return "[  |  |  ]" 

    # Entrada
    if "🟧" in contenido:
        return "[🟧|  |  ]"

    trampas_lista = [" "," "," "]
    # Trampas
    if "F" in contenido:
        trampas_lista[trampas_lista.index(" ")] = "F"
    if "P" in contenido:
        trampas_lista[trampas_lista.index(" ")] = "P"
    if "D" in contenido:
        trampas_lista[trampas_lista.index(" ")] = "D"

    caja_str = f"[{trampas_lista[0]} |{trampas_lista[1]} |{trampas_lista[2]} ]"

    # Personas y salida
    if "🟩" in contenido:
        caja_str = "[🟩|  |  ]" 
    if "CK" in contenido and not "M" in contenido:
        if "🟩" in contenido:
            caja_str = "[🟩|CK|  ]" 
        else:
            caja_str = "[CK|  |  ]" 
    if "M" in contenido and not "CK" in contenido:
        if "🟩" in contenido:
            caja_str = "[🟩|M |  ]" 
        else:
            caja_str = "[M |  |  ]"
    if "M" in contenido and "CK" in contenido:  # CK al tener dos caracteres daba problemas
        if "🟩" in contenido:
            caja_str = "[🟩|CK|M ]" 
        else:
            caja_str = "[CK|M |  ]"
  
    return caja_str

def imprimir_tablero_cajas(dicc_entorno: dict, n: int = 6, con_coordenadas: bool = True):
    """
    Imprime el tablero con celdas compactas tipo [  |  |  ]

    """
    ancho_celda = 9  # '[  |  |  ]' son 9 chars

    if con_coordenadas:
        cab = " " * 4
        for j in range(1, n + 1):
            cab += f"{j:<{ancho_celda}}"
        print(cab)

    for i in range(1, n + 1):
        fila = ""
        for j in range(1, n + 1):
            s = celda_caja(dicc_entorno[(i, j)].celda)
            fila += f"{s:<{ancho_celda}}"
        if con_coordenadas:
            print(f"{i:<3} {fila}")
        else:
            print(fila)

def comprobaciones(dicc_entorno: dict[tuple[int, int], Celda], campo_comprobacion: str, celda_mod:str, modo: bool):
    """
    Marca celdas adyacentes con un atributo booleano (trampas, ronquido, resplandor).

    Inputs:
        dicc_entorno (dict): Entorno del palacio.
        campo_comprobacion (str): Nombre del atributo a modificar.
        celda_mod (str): Tipo de celda que genera el efecto (ej. " P" para brisa).
        modo (bool)

    """
    for (i,j), celda in dicc_entorno.items():
        if celda_mod in celda.celda:
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
    # Funciones que facilitan la creacion del entorno
    def es_entrada(x, y):
        return (x, y) == (1, 1)
    
    def tiene_trampa(x, y):
        contenido_lista = dicc_entorno[(x, y)].celda
        return ("F" in contenido_lista) or ("P" in contenido_lista) or ("D" in contenido_lista)

    dicc_entorno = {}
    for i in range(n):
        for j in range(n):
            dicc_entorno[(i+1,j+1)] = Celda()

    # Coloca entrada
    (x_entrada, y_entrada) = (1,1)
    dicc_entorno[(x_entrada, y_entrada)].celda = ["🟧"]

    # Trampas
    (x_dardos, y_dardos) = (random.randint(1,n), random.randint(1,n))
    (x_fuego, y_fuego) = (random.randint(1,n), random.randint(1,n))
    (x_pinchos, y_pinchos) = (random.randint(1,n), random.randint(1,n)) # Pueden estar las tres trampas juntas

    i=0
    coord_trampas = [(x_dardos, y_dardos), (x_fuego, y_fuego), (x_pinchos, y_pinchos)]  # Importante el orden para saber que trampa es
    for (x,y) in coord_trampas:
        while es_entrada(x,y):  # Queremos que las trampas no coincidan con la entrada
            (x, y) = (random.randint(1,n), random.randint(1,n))
        
        if i == 0:
            añadir(dicc_entorno[(x,y)],"D")
        elif i == 1:
            añadir(dicc_entorno[(x,y)],"F")
        elif i == 2:
            añadir(dicc_entorno[(x,y)],"P")
        i += 1

    # Militar, Kurtz, Salida
    (x_soldado, y_soldado) = (random.randint(1,n), random.randint(1,n))
    (x_coronel, y_coronel) = (random.randint(1,n), random.randint(1,n))
    (x_salida, y_salida) = (random.randint(1,n), random.randint(1,n))

    i = 0
    coord_trampas = [(x_soldado, y_soldado), (x_coronel, y_coronel), (x_salida, y_salida)]
    for (x,y) in coord_trampas:
        while es_entrada(x,y) or tiene_trampa(x,y):
            (x, y) = (random.randint(1,n), random.randint(1,n))

        if i == 0:
            añadir(dicc_entorno[(x,y)],"M")
        elif i == 1:
            añadir(dicc_entorno[(x,y)],"CK")
        elif i == 2:
            añadir(dicc_entorno[(x,y)],"🟩")
            dicc_entorno[(x,y)].es_salida = True
        i += 1

    # Paredes y percepciones
    for (i, j), celda in dicc_entorno.items():
        if i == 1: celda.pared_N = True
        if i == n: celda.pared_S = True
        if j == 1: celda.pared_O = True
        if j == n: celda.pared_E = True

    dicc_entorno = comprobaciones(dicc_entorno, "ronquido", "M", True)
    dicc_entorno = comprobaciones(dicc_entorno, "resplandor", "🟩", True)
    dicc_entorno = comprobaciones(dicc_entorno, "fuego_ady", "F", True)
    dicc_entorno = comprobaciones(dicc_entorno, "pinchos_ady", "P", True)
    dicc_entorno = comprobaciones(dicc_entorno, "dardos_ady", "D", True)

    return dicc_entorno


# BAYES: PRIORS, RIESGO, DECISIÓN

def generar_dicc_creencias(dicc_entorno:dict[tuple[int, int], Celda]):
    """
    Genera el diccionario original sobre donde puede estar cada elemento {F,P,D,M,S,CK}.

    Da como resultado un prior uniforme sobre cada elemento (excepto sobre la entrada, que sabemos que no tiene nada).

    Inputs:
        dicc_entorno (dict)

    Returns:
        dict[str -> dict[(i,j)->prob]]

    """
    celdas_validas = []
    for (i, j), celda in dicc_entorno.items():
        if "🟧" not in celda.celda:   # celda inicial (sabemos que no tiene ni trampa ni militar)
            celdas_validas.append((i, j))

    dicc_creencias = {
    "F": {(i,j): 1/35 for (i,j) in celdas_validas},
    "P": {(i,j): 1/35 for (i,j) in celdas_validas},
    "D": {(i,j): 1/35 for (i,j) in celdas_validas},
    "M": {(i,j): 1/35 for (i,j) in celdas_validas},
    "S": {(i,j): 1/35 for (i,j) in celdas_validas},
    "CK": {(i,j): 1/35 for (i,j) in celdas_validas},
    }
    
    for elemento in ["F", "P", "D", "M", "S", "CK"]:    # Sabemos que en la salida no hay nada
        dicc_creencias[elemento][(1,1)] = 0

    return dicc_creencias

def actualizar_creencias(dicc_creencias: dict[tuple[int, int], float], pos_actual:tuple[int, int], percepto:bool):
    """
    Siguiendo el modelo de verosimilitud, si recibimos un estímulo: TODAS LAS CELDAS NO ADYACENTES PASAN A TENER PROBABILIDAD 0.
    
    Si percepto=True:
        - celdas no adyacentes (ni la propia) -> prob 0
    Si percepto=False:
        - celdas adyacentes (y propia) -> prob 0

    Luego normaliza.

    Inputs:
        belief_tau (dict[(i,j)->float])
        pos_actual (tuple[int,int])
        percepto (bool)

    """
    for (i,j) in dicc_creencias.keys():
        if percepto:
            if (i,j)==pos_actual or es_adyacente((i,j), pos_actual):
                dicc_creencias[(i,j)] *= 1 
            else:
                dicc_creencias[(i,j)] = 0
        else:
            if (i,j)==pos_actual or es_adyacente((i,j), pos_actual):
                dicc_creencias[(i,j)] = 0 
            else:
                dicc_creencias[(i,j)] *= 1

    # Normalizamos
    total = sum(dicc_creencias.values())
    for k in dicc_creencias.keys():
        dicc_creencias[k] = dicc_creencias[k] / total

def actualizar_todas_creencias(dicc_creencias: dict[tuple[int, int], float], dicc_entorno: dict[tuple[int, int], Celda], pos_actual: tuple[int, int]) -> None:
    """
    Actualiza TODAS las creencias (F,P,D,M,S) usando los perceptos de la celda actual.

    Inputs:
        dicc_creencias (dict)
        dicc_entorno (dict)
        pos_actual (tuple)

    """
    celda = dicc_entorno[pos_actual]

    actualizar_creencias(dicc_creencias["F"], pos_actual, celda.fuego_ady)
    actualizar_creencias(dicc_creencias["P"], pos_actual, celda.pinchos_ady)
    actualizar_creencias(dicc_creencias["D"], pos_actual, celda.dardos_ady)
    actualizar_creencias(dicc_creencias["M"], pos_actual, celda.ronquido)
    actualizar_creencias(dicc_creencias["S"], pos_actual, celda.resplandor)

def riesgo_celda(dicc_creencias:dict[tuple[int, int], float], celda:tuple[int, int]):
    """
    Devuelve la probabilidad de riesgo (Ya sea por militar o por trampa) de cada celda.
    
    Inputs:
        dicc_creencias (dict)
        celda (tuple[int,int])

    """
    p_trampa = dicc_creencias["F"][celda] + dicc_creencias["P"][celda] + dicc_creencias["D"][celda]
    p_militar = dicc_creencias["M"][celda]
    return p_trampa + p_militar


# ACCIONES DEL JUEGO 

def accion_mover(dicc_entorno:dict[tuple[int, int], Celda], mov_vertical:int, mov_horizonal:int):
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
    pos = pos_capitan(dicc_entorno)
    if pos is None:
        return None, dicc_entorno

    x_actual, y_actual = pos
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

    # Muere por trampa
    if ("F" in celda_destino.celda) or ("P" in celda_destino.celda) or ("D" in celda_destino.celda):
        return (nx, ny), dicc_entorno

    # Muere por militar
    if "M" in celda_destino.celda:
        return (nx, ny), dicc_entorno

    # Marcamos que estamos ya con CK
    if "CK" in celda_destino.celda:
        celda_destino.tengo_CK = True
        eliminar(celda_destino, "CK")

    añadir(celda_destino, "🟧") # Entramos en la celda nueva
    eliminar(celda_actual, "🟧")    # Salimos de la celda actual


    if celda_actual.tengo_CK:
            celda_destino.tengo_CK = True

    return (nx, ny), dicc_entorno

def accion_granada(dicc_entorno:dict[tuple[int, int], Celda], lanzamiento_vertical:int, lanzamiento_horizontal:int):
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
            print("Dirección inválida.")
            return dicc_entorno
        
        # Localizamos la posición del capitán
        x_actual, y_actual = pos_capitan(dicc_entorno)
        
        nx, ny = x_actual + lanzamiento_vertical, y_actual + lanzamiento_horizontal
        if (nx, ny) not in dicc_entorno.keys(): return dicc_entorno
        
        if "M" in dicc_entorno[(nx, ny)].celda:
            # Quitamos al militar y el ronquido
            eliminar(dicc_entorno[(nx,ny)], "M")
            dicc_entorno = comprobaciones(dicc_entorno, "ronquido", "M", False)
            granada = True
            dicc_entorno[(x_actual, y_actual)].grito = True
        else:
            print("No has acertado... Te has quedado sin granada!")
            granada = True

    else:
        print("Ya has utilizado la granada, solo tenias una...")

    return dicc_entorno

def accion_salir(dicc_entorno:dict[tuple[int, int], Celda]):
    """
    Intenta salir del palacio.

    Inputs:
        dicc_entorno (dict)
    
    Returns:
        dict_entorno (dict), salida_ok (bool)

    """
    # Localizamos la posición del capitán
    x_actual, y_actual = pos_capitan(dicc_entorno)
    celda_capitan = dicc_entorno[(x_actual,y_actual)]

    if celda_capitan.es_salida and celda_capitan.tengo_CK:
        print(f"\nHas ganado! Has conseguido salir con el Coronel Kurtz.")
        eliminar(celda_capitan, "🟧")
        return dicc_entorno, True
    
    elif celda_capitan.es_salida:
        print(f"\nNo tienes al Coronel Kurtz...")
        return dicc_entorno, False
    elif celda_capitan.tengo_CK:
        print(f"\nEsa no es la salida...")
        return dicc_entorno, False
    else:
        print(f"\nNo es ni la salida ni tienes al Coronel Kurtz.")
        return dicc_entorno, False

def imprimir_info(dicc_entorno:dict[tuple[int, int], Celda], x:int, y:int):
    print("ESTADO ACTUAL")
    print("-" * 40)
    print(f"Posicion: ({x}, {y})")
    print(f"Queroseno (fuego adyacente)  : {dicc_entorno[(x,y)].fuego_ady}")
    print(f"Crujidos (pinchos adyacentes)  : {dicc_entorno[(x,y)].pinchos_ady}")
    print(f"Cables (dardos adyacentes)  : {dicc_entorno[(x,y)].dardos_ady}")
    print(f"Ronquido (militar adyacentes)   : {dicc_entorno[(x,y)].ronquido}")
    print(f"Grito       : {dicc_entorno[(x,y)].grito}")
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
        mapa_visible (bool): Imprime el mapa visual si es True

    """
    global granada
    granada = False
    dicc_entorno = entorno_del_palacio(n)
    dicc_creencias = generar_dicc_creencias(dicc_entorno)
    (x, y) = (1,1)

    print("\n--- INICIO DEL JUEGO ---\n")

    while True:

        actualizar_todas_creencias(dicc_creencias, dicc_entorno, pos_capitan(dicc_entorno))
        imprimir_info(dicc_entorno, x, y)

        for (x,y) in dicc_entorno.keys():
            if es_adyacente(pos_capitan(dicc_entorno), (x,y)):
                print(f""" Riesgo de celda {(x,y)}:
        - Fuego : {dicc_creencias["F"][(x,y)]}
        - Pinchos : {dicc_creencias["P"][(x,y)]}
        - Dardos : {dicc_creencias["D"][(x,y)]}
        - Militar : {dicc_creencias["M"][(x,y)]}
""")

        if mapa_visible:
            imprimir_tablero_cajas((dicc_entorno))

        accion = input("Acción: W,A,S,D,G(granada),X(salir) ")

        if accion.upper() in ["W","A","S","D"]:
            if accion.upper()=="W": (x,y),dicc_entorno = accion_mover(dicc_entorno,-1,0)
            if accion.upper()=="A": (x,y),dicc_entorno = accion_mover(dicc_entorno,0,-1)
            if accion.upper()=="S": (x,y),dicc_entorno = accion_mover(dicc_entorno,1,0)
            if accion.upper()=="D": (x,y),dicc_entorno = accion_mover(dicc_entorno,0,1)

            if "M" in dicc_entorno[(x,y)].celda:
                print(f"\nHas perdido... Te ha encontrado un militar.")
                return False
            if "P" in dicc_entorno[(x,y)].celda:
                print(f"\nHas perdido... Has caido en los pinchos.")
                return False 
            if "D" in dicc_entorno[(x,y)].celda:
                print(f"\nHas perdido... Has caido en los dardos venenosos.")
                return False 
            if "F" in dicc_entorno[(x,y)].celda:
                print(f"\nHas perdido... Has caido en el fuego.")
                return False 
                

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
                print("No he entendido la direccion")
            

        elif accion.upper()=="X":
            tupla_salir = accion_salir(dicc_entorno)
            dicc_entorno = tupla_salir[0]
            if tupla_salir[1]:
                return True

        else:
            print(f"\nUPS! No he entendido eso.")


# JUEGO BAYES

def vecinos_validos(dicc_entorno:dict[tuple[int, int], Celda], pos:tuple[int, int]):
    """
    Devuelve lista de vecinos (accion, nx, ny) a los que se puede intentar mover
    (respetando paredes).

    Inputs:
        dicc_entorno: entorno
        pos: (x,y)

    Returns:
        lista de trios (accion, nx, ny) con accion en {"W","S","A","D"}

    """
    x, y = pos
    celda = dicc_entorno[pos]

    candidatos = [("W", x-1, y), ("S", x+1, y), ("A", x, y-1), ("D", x, y+1)]
    vecinos = []

    for trio in candidatos: 

        if trio[0] == "W" and celda.pared_N:
            continue
        if trio[0] == "S" and celda.pared_S:
            continue
        if trio[0] == "A" and celda.pared_O:
            continue
        if trio[0] == "D" and celda.pared_E:
            continue

        vecinos.append(trio)

    return vecinos

def elegir_vecino_menor_riesgo(dicc_entorno:dict[tuple[int, int], Celda], dicc_creencias:dict[tuple[int, int], float], pos:tuple[int, int], casillas_vis:set[tuple[int,int]]):
    """
    Elige el vecino válido con:
        1) menor riesgo
        2) en empate, iremos hacia abajo

    """
    if casillas_vis is None:
        casillas_vis = set()

    vecinos = vecinos_validos(dicc_entorno, pos)

    dicc_riesgos = {}
    for vecino in vecinos:
        riesgo = riesgo_celda(dicc_creencias, (vecino[1], vecino[2]))
        if vecino not in casillas_vis:
            try:
                dicc_riesgos[riesgo].append(vecino)
            except:
                dicc_riesgos[riesgo] = [vecino]

    riesgo_min = min(dicc_riesgos.keys()) 
    riesgo_min = next(iter(dicc_riesgos))
    return dicc_riesgos[riesgo_min][0]

def construir_celdas_aceptables_bayes(dicc_entorno:dict[tuple[int, int], Celda], dicc_creencias:dict[tuple[int, int], float], p_umbral: float):
    """
    Construye conjunto de celdas a las que se permite entrar según Bayes:
        riesgo_celda < p_umbral

    Inputs:
        dicc_entorno (dict)
        dicc_creencias (dict) 
        p_umbral (float)

    Returns:
        set[(int,int)]

    """
    aceptables = set()
    for (x,y) in dicc_entorno.keys():
        riesgo = riesgo_celda(dicc_creencias, (x,y))
        if riesgo < p_umbral:
            aceptables.add((x,y))
    return aceptables

def buscar_objetos_lista(dicc_entorno:dict[tuple[int, int], Celda], objeto: str):
    """
    Busca posiciones clave en el tablero.

    Inputs:
        dicc_entorno (dict)
        objeto (str): "Inicio", "Kurtz", "Salida"

    Returns:
        tuple[int,int] | None
        
    """
    for (x, y) in dicc_entorno.keys():
        contenido = dicc_entorno[(x,y)].celda
        if objeto == "Inicio" and "🟧" in contenido:
            return (x, y)
        if objeto == "Kurtz" and "CK" in contenido:
            return (x, y)
        if objeto == "Salida" and "🟩" in contenido:
            return (x, y)
    return None

def bfs_plan_bayes(dicc_entorno:dict[tuple[int, int], Celda], dicc_creencias:dict[tuple[int, int], float], celdas_aceptables, inicio:tuple[int, int], objetivo:tuple[int, int]):
    """
    Algoritmo BFS (Breadth First Search) para encontrar camino considerando celdas aceptables.
    Ordenamos acciones por menor riesgo.
    
    Inputs:
        dicc_entorno (dict)
        dicc_creencias (dict)
        celdas_aceptables (set)
        inicio (tuple)
        objetivo (tuple)
    
    Returns:
        list[str] | None: lista de acciones ["W","S","A","D"] o None si imposible
    
    """
    from queue import Queue
    
    cola = Queue()
    cola.put(inicio)
    
    visitado = {inicio}
    padre = {inicio: None}
    accion_padre = {inicio: None}
    
    while not cola.empty():
        (x, y) = cola.get()
        
        # Si llegamos al objetivo, reconstruimos el camino
        if (x, y) == objetivo:
            plan = []
            estado = (x, y)
            while accion_padre[estado] is not None:
                plan.append(accion_padre[estado])
                estado = padre[estado]
            plan.reverse()
            return plan
        
        acciones = [("W", -1, 0), ("S", 1, 0), ("A", 0, -1), ("D", 0, 1)]
               
        # Ordenamos las acciones por menor riesgo y menor distancia al objetivo
        def clave_accion(acc):
            _, dx, dy = acc
            nx, ny = x + dx, y + dy
            if (nx, ny) not in dicc_entorno or (nx, ny) not in celdas_aceptables:
                return (float('inf'), float('inf'))
            
            # Prioridad 1: menor riesgo
            riesgo = riesgo_celda(dicc_creencias, (nx, ny))
            # Prioridad 2: menor distancia Manhattan al objetivo
            distancia = abs(objetivo[0] - nx) + abs(objetivo[1] - ny)
            
            return (riesgo, distancia)
        
        # Ordenamos por menor riesgo y distancia
        acciones_ordenadas = sorted(acciones, key=clave_accion)
        
        for accion, dx, dy in acciones_ordenadas:
            nx, ny = x + dx, y + dy
            
            # Verificamos si la nueva posición es válida
            if (nx, ny) not in dicc_entorno or (nx, ny) not in celdas_aceptables or (nx, ny) in visitado:
                continue
            
            # Verificamos si podemos entrar (no hay pared)
            celda_actual = dicc_entorno[(x, y)]
            if dx == -1 and celda_actual.pared_N:
                continue
            if dx == 1 and celda_actual.pared_S:
                continue
            if dy == -1 and celda_actual.pared_O:
                continue
            if dy == 1 and celda_actual.pared_E:
                continue
            
            # Marcamos como visitado y guardamos información del camino
            visitado.add((nx, ny))
            padre[(nx, ny)] = (x, y)
            accion_padre[(nx, ny)] = accion
            cola.put((nx, ny))
    
    return None

# def bfs_plan_bayes(dicc_entorno, dicc_creencias, celdas_aceptables,inicio, objetivo):
    """
    Algoritmo BFS (Breadth First Search) para encontrar, pero con CELDAS ACEPTABLES (riesgo < p_umbral):
        Inicio → Kurtz → Salida

    Inputs:
        dicc_entorno (dict)
        celdas_seguras (set)

    Returns:
        list[str] | None: lista de acciones ["A","S",...] o None si imposible
    """

    cola = Queue()
    cola.put(inicio)

    padre = {inicio: None}
    accion_padre = {inicio: None}

    while not cola.empty():
        (x, y) = cola.get()

        if (x, y) == objetivo:
            plan = []
            estado = ((x, y))
            while accion_padre[estado] is not None:
                plan.append(accion_padre[estado])
                estado = padre[estado]
            plan.reverse()
            return plan
        
        acciones = [("W", -1, 0), ("S", 1, 0), ("A", 0, -1), ("D", 0, 1)]

        def clave(accion):
            _, dx, dy = accion
            nx, ny = x + dx, y + dy
            if (nx, ny) not in dicc_entorno or (nx, ny) not in celdas_aceptables:
                return (float("inf"), float("inf"))
            r = riesgo_celda(dicc_creencias, (nx, ny))
            d = abs(objetivo[0]-nx) + abs(objetivo[1]-ny)
            return (r, d)

        acciones.sort(key=clave)

        for accion, dx, dy in acciones:
            nx, ny = x + dx, y + dy
            nueva_pos = (nx, ny)

            if nueva_pos not in dicc_entorno:
                continue

            if nueva_pos not in celdas_aceptables:
                continue

            if nueva_pos not in padre:
                padre[nueva_pos] = ((x, y))
                accion_padre[nueva_pos] = accion
                cola.put(nueva_pos)

    return None


    """
    Ejecuta plan, pero antes de entrar a cada celda comprueba:
        riesgo_celda(nueva_pos) < p_umbral

    Además, actualiza creencias al llegar a cada celda.

    Inputs:
        dicc_entorno (dict)
        plan (list[str])
        mapa_visible (bool)

    Returns:
        (dicc_entorno, exito)
    """
    pos_actual = pos_capitan(dicc_entorno)
    if pos_actual is None:
        return dicc_entorno, False

    for accion in plan:
        actualizar_todas_creencias(dicc_creencias, dicc_entorno, pos_actual)

        if accion == "W": dx, dy = -1, 0
        elif accion == "S": dx, dy = 1, 0
        elif accion == "A": dx, dy = 0, -1
        elif accion == "D": dx, dy = 0, 1

        nx, ny = pos_actual[0] + dx, pos_actual[1] + dy
        if (nx, ny) not in dicc_entorno:    # Fuera de límites
            return dicc_entorno, False

        # Checkeamos el riesgo antes de entrar!
        riesgo = riesgo_celda(dicc_creencias, (nx, ny))
        if riesgo >= p_umbral:
            print(f"Riesgo {riesgo} >= p_umbral {p_umbral} para entrar en {(nx,ny)}")
            return dicc_entorno, False

        dicc_entorno = accion_mover(dicc_entorno, dx, dy)[1]
        
        pos_actual = pos_capitan(dicc_entorno)

        if mapa_visible:
            imprimir_tablero_cajas(dicc_entorno)

    return dicc_entorno, True

def juego_automatico_bayes(n: int, p_umbral: float = 0.2, mapa_visible:bool=True):
    """
    Juega solo:
        · genera mapa y priors
        · actualizaa creencias (creencias iniciales uniformes)
        · calcula BFS 
        · lo ejecuta automáticamente

        IMPORTANTE:
        · Si no hay plan (no hay vecinos con riesgo 0.0), entra en modo "arriesgado": elige vecino con menor riesgo
        · Si se sospecha que el riesgo viene del militar y queda granada, la usa

    """
    global granada
    granada = False

    dicc_entorno = entorno_del_palacio(n)
    dicc_creencias = generar_dicc_creencias(dicc_entorno)
    pos_antes = None

    while True:
        # Actualizamos la posición del capitán
        pos = pos_capitan(dicc_entorno)

        casillas_vis = set()
        if pos_antes is not None:
            casillas_vis.add(pos_antes)

        # Actualizamos nuestras creencias según los perceptos
        actualizar_todas_creencias(dicc_creencias, dicc_entorno, pos)

        if mapa_visible:
            imprimir_tablero_cajas(dicc_entorno)

        # Comprobams victoria
        if dicc_entorno[pos].es_salida and dicc_entorno[pos].tengo_CK:
            dicc_entorno, salir = accion_salir(dicc_entorno)
            if salir:
                return True

        # Actualizamos objetivo    
        if dicc_entorno[pos].tengo_CK:
            objetivo = buscar_objetos_lista(dicc_entorno, "Salida")
        else:
            objetivo = buscar_objetos_lista(dicc_entorno, "Kurtz")

        # Si el militar está en la misma casilla que Kurtz o salida, lanzamos granada
        if "M" in dicc_entorno[objetivo].celda and es_adyacente(pos, objetivo):
            lanzamiento_vertical = objetivo[0] - pos[0]
            lanzamiento_horizontal = objetivo[1] - pos[1]

            print("Coincide el militar con la salida o el Coronel Kurtz, por tanto, debemos tirar la granada.")
            accion_granada(dicc_entorno, lanzamiento_vertical, lanzamiento_horizontal)
            continue
        
        # Intento "prudente" (sin tomar riesgos por debajo del umbral)
        celdas_aceptables = construir_celdas_aceptables_bayes(dicc_entorno, dicc_creencias, p_umbral)
        celdas_aceptables.add(pos)
        celdas_aceptables.add(objetivo)

        if pos_antes is not None and pos_antes != objetivo:
            celdas_aceptables.discard(pos_antes)

        plan = bfs_plan_bayes(dicc_entorno, dicc_creencias, celdas_aceptables, pos, objetivo)
        
        # Intento "arriesgado"
        modo_arriesgado = False
        if plan is None or len(plan) == 0:
            modo_arriesgado = True
            primer_paso, nx, ny = elegir_vecino_menor_riesgo(dicc_entorno, dicc_creencias, pos, casillas_vis)
        else:
            primer_paso = plan[0]
            if primer_paso == "W": nx, ny = pos[0]-1, pos[1]
            if primer_paso == "S": nx, ny = pos[0]+1, pos[1]
            if primer_paso == "A": nx, ny = pos[0], pos[1]-1
            if primer_paso == "D": nx, ny = pos[0], pos[1]+1

        # Convertimos acción a dx,dy
        if primer_paso == "W": dx, dy = -1, 0
        elif primer_paso == "S": dx, dy = 1, 0
        elif primer_paso == "A": dx, dy = 0, -1
        elif primer_paso == "D": dx, dy = 0, 1

        riesgo_intentado = riesgo_celda(dicc_creencias, (nx, ny))
        print(f"Voy a entrar en {(nx,ny)} con acción {primer_paso} y riesgo={riesgo_intentado}")

        if modo_arriesgado and (not granada):
            prob_M = dicc_creencias["M"][(nx, ny)]
            prob_Trap = dicc_creencias["F"][(nx, ny)] + dicc_creencias["P"][(nx, ny)] + dicc_creencias["D"][(nx, ny)]

            if prob_M > 0 and prob_M >= prob_Trap:  # Probabilidad domina el riesgo de esa celda
                print("Usamos granada")
                accion_granada(dicc_entorno, dx, dy)
                continue

        pos_antes = pos
        pos_nueva, dicc_entorno = accion_mover(dicc_entorno, dx, dy)

        if pos_nueva == pos_antes:
            vecinos = vecinos_validos(dicc_entorno, pos_antes)

            vecinos_buenos = []
            for vecino in vecinos:
                if (vecino[1], vecino[2]) != (nx, ny):
                    vecinos_buenos.append(vecino)
            if not vecinos_buenos:
                return False
            
            # elegimos el siguiente mejor
            dicc_riesgos = {}
            for vecino in vecinos_buenos:
                riesgo = riesgo_celda(dicc_creencias, (vecino[1], vecino[2]))
                try:
                    dicc_riesgos[riesgo].append(vecino)
                except:
                    dicc_riesgos[riesgo] = [vecino]

            riesgo_min = min(dicc_riesgos.keys()) 
            accion_alt, dx2, dy2 = dicc_riesgos[riesgo_min][0]

            pos_nueva2, dicc_entorno = accion_mover(dicc_entorno, dx2, dy2)
            if pos_nueva2 is None or pos_nueva2 == pos_antes:
                return False
            pos_nueva = pos_nueva2

        # Si está en celda mortal muere
        contenido = dicc_entorno[pos_nueva].celda
        if ("M" in contenido) or ("F" in contenido) or ("P" in contenido) or ("D" in contenido):
            print(f"Has perdido al entrar en {pos_nueva}. Contenido: {contenido}")
            return False
        

# MAIN

def main():

    n = 6
    print("--- MENU ---")
    print("1: Interactivo")
    print("2: Bayes (decisión bajo incertidumbre)")
    modo = input("Modo: ").strip()

    mapa = input("Mapa visible? (Y/N): ").upper()
    if mapa == "Y":
        mapa_visible = True
    elif mapa == "N":
        mapa_visible = False
    else:
        mapa_visible = True

    if modo == "1":
        if juego_interactivo(n, mapa_visible=mapa):
            print("Ahora te toca salir del rio...")
            river_mdp.sim_rio()
    elif modo == "2":
        p = input("Umbral p de riesgo (ej 0.2): ").strip()
        try:
            p = float(p)
        except:
            p = 0.2
        if juego_automatico_bayes(n, p_umbral=p, mapa_visible=mapa_visible):
            print("Ahora te toca salir del rio...")
            river_mdp.sim_rio()
    else:
        print("Opción inválida.")

if __name__=="__main__":

    main()