import random

# ENTORNO DEL RÍO (MDP)

def crear_river_strength(n: int):
    """
    Crea un diccionario river_strength con la fuerza de la corriente del rio
    - Columnas borde (primera y última): 0.0
    - Columnas interiores: random (0.06,0.94)

    Returns:
        dict[int -> float]

    """
    river_strength = {}
    for j in range(1, n + 1):
        if j == 1 or j == n:
            river_strength[j] = 0.0
        else:
            river_strength[j] = round(random.uniform(0.06, 0.94), 1)
    return river_strength

def generar_rio(n_filas: int, n_columnas: int, n_islas: int = 2,):
    """
    Genera el entorno del río:
      - "R": casilla segura de río
      - "I": isla (no segura)
      - "E": salida
      - "CWCK": posición inicial (para imprimir CWCK, de normal, R)
      - "O": Orilla (para imprimir: " ")

    Inicio siempre en (1,1)

    Returns:
      dicc_rio, inicio, final, river_strength

    """
    river_strength = crear_river_strength(n_columnas)

    # Generamos el río primero todo seguro (R)
    dicc_rio = {}
    for i in range(1, n_filas + 1):
        for j in range(1, n_columnas + 1):
            if j == 1 or j == n_columnas:
                dicc_rio[(i, j)] = "O" # Orilla
            else:
                dicc_rio[(i, j)] = "R"  

    inicio = (1, 1)
    final = (random.randint(1,n_filas), n_columnas) # En la orilla final, en cualquier posición/fila
    dicc_rio[final] = "E"

    # Colocar islas
    islas = set()
    while True:
        i = random.randint(2, n_filas - 1)  # no primera ni última fila
        j = random.randint(1, n_columnas - 1)

        if (i, j) in islas:
            continue

        islas.add((i, j))
        if len(islas) == n_islas:
            break

    for pos in islas:
        dicc_rio[pos] = "I"

    return dicc_rio, inicio, final, river_strength

def imprimir_rio(dicc_rio: dict, n_filas: int, n_columnas: int, pos_actual: tuple[int, int], inicio: tuple[int, int], final: tuple[int, int]):
    """
    Imprime el río por consola.
    - CWCK en la posición actual
    - E en salida
    - I para islas
    - R para río seguro
    - " " para orillas

    """
    print()
    cab = "   "
    for j in range(1, n_columnas + 1):
        cab += f"{j}   "
    print(cab)

    for i in range(1, n_filas + 1):
        fila = f"{i} "
        for j in range(1, n_columnas + 1):
            pos = (i, j)
            if pos == pos_actual:
                s = "CWCK"
            else:
                s = dicc_rio[pos]
                if s == "O":
                    s = " "
            fila += f"|{s}| "
        print(fila)
    print()

    """
    Devuelve si una casilla es válida o segura (está dentro del tablero y no es isla).
    
    """
    (i, j) = pos
    if i < 1 or i > n_filas or j < 1 or j > n_columnas:
        return False
    if dicc_rio[(i, j)] == "I":
        return False
    return True

def mover_determinista(pos: tuple[int, int], accion: str):
    """
    Movimiento (sin corriente).
    """
    (i, j) = pos
    if accion == "up":
        return (i - 1, j)
    if accion == "down":
        return (i + 1, j)
    if accion == "left":
        return (i, j - 1)
    if accion == "right":
        return (i, j + 1)
    if accion == "stay":
        return (i, j)
    return (i, j)

def dentro_limites(n_filas: int, n_columnas: int, pos: tuple[int, int]):
    i, j = pos
    return 1 <= i <= n_filas and 1 <= j <= n_columnas

def es_isla(dicc_rio: dict, pos: tuple[int, int]):
    return dicc_rio[pos] == "I"

def funcion_transicion(dicc_rio: dict, n_filas: int, n_columnas: int,river_strength: dict, s: tuple[int, int], a: str,final: tuple[int, int]):
    """
    Devuelve lista de salidas posibles desde un estado s y una acción a: [(s', prob, recompensa), ...]

    OJO: Si el movimiento que intentamos (acción) lleva a una isla => NO nos "quedamos" en la isla,
    te quedas en s (estado anterior) con probabilidad 1, recompensa -100.

    Lo mismo pasa con los bordes del tablero, pero la recompensa es -1.

    +100 si llegamos al final, y -1 en cualquier otro caso de movimiento normal.

    Ahora, sobre la corriente:
      - Si accion != "down" y la acción es válida, entonces:
           con prob pdir vas a la dirección deseada
           con prob pdown intentas ir hacia abajo por la corriente
        Si el empuje hacia abajo apunta a isla/borde, esa parte se convierte en "stay".

    Aclaración: con s_dir nos referimos al estado que alcanzamos si nos movemos en la dirección de acción a,
    mientras que s_down es el estado al que llegamos si nos movemos hacia abajo (down), ya sea por corriente o por decisión.

    Lo mismo con pdown (probabilidad de que la corriente te arrastre) y pdir (probabilidad de ir hacia donde tu querías).

    """
    (i, j) = s

    # Devuelve +100 si es la salida y -1 si no es salida
    def recompensa_final(s):
        if s == final:
            return 100
        return -1

    # Terminal: si ya estás en final, te quedas ahí
    if s == final:
        return [(final, 1.0, 0)]

    # a == "down"
    if a == "down":
        s_dir = mover_determinista(s, "down")

        if not dentro_limites(n_filas, n_columnas, s_dir):
            return [(s, 1.0, -1)]

        if es_isla(dicc_rio, s_dir):
            return [(s, 1.0, -100)]

        return [(s_dir, 1.0, recompensa_final(s_dir))]

    # a != "down" 
    pdown = river_strength[j]
    pdir = 1.0 - pdown

    s_dir = mover_determinista(s, a)

    if not dentro_limites(n_filas, n_columnas, s_dir):
        return [(s, 1.0, -1)]

    if es_isla(dicc_rio, s_dir):
        return [(s, 1.0, -100)]

    salidas_posibles = []

    # Movimiento en la dirección deseada
    salidas_posibles.append((s_dir, pdir, recompensa_final(s_dir)))

    # Empuje por corriente hacia abajo 
    s_down = mover_determinista(s, "down")

    if not dentro_limites(n_filas, n_columnas, s_down):
        salidas_posibles.append((s, pdown, -1))
    elif es_isla(dicc_rio, s_down):
        salidas_posibles.append((s, pdown, -100))
    else:
        salidas_posibles.append((s_down, pdown, recompensa_final(s_down)))

    return salidas_posibles

def listar_estados(dicc_rio: dict, n_filas: int, n_columnas: int):
    """
    Lista estados alcanzables: todas las casillas que NO son isla.
    """
    estados = []
    for i in range(1, n_filas + 1):
        for j in range(1, n_columnas + 1):
            if dicc_rio[(i, j)] != "I":
                estados.append((i, j))
    return estados


# VALUE ITERATION

def value_iteration(dicc_rio: dict, n_filas: int, n_columnas: int, final: tuple[int, int], river_strength: dict, gamma: float = 1):
    """
    Value Iteration (siguiendo la fórmula):
      V(s) = max_a Σ_{s'} P(s'|s,a) * [ R(s,a,s') + gamma * V(s') ]

    Devuelve:
      V: dicc valor óptimo
      A: dicc acción ótima

    """
    acciones = ["up", "down", "left", "right", "stay"]
    estados = listar_estados(dicc_rio, n_filas, n_columnas)

    # Creamos el diccionario de los valores y acciones (originalmente inicializados a 0.0)
    V, A = {}, {}
    for estado in estados:
        V[estado] = 0.0
        A[estado] = "stay"

    while True:
        controlador = 0.0   # Valor clave que controla la salida del bucle (cuando dejamos de iterar, es porque la mejor opción es cercano a 0.

        for estado in estados:
            if estado == final:
                V[estado] = 0.0
                A[estado] = "stay"
                continue

            valor_opt = None
            accion_opt = None

            for accion in acciones:
                # Calculamos estados posibles, probabilidades y recompensas. Esta función nos devuelve [(s', prob, recompensa)]
                salidas_posibles = funcion_transicion(dicc_rio, n_filas, n_columnas, river_strength, estado, accion, final)
        
                total = 0.0
                for (s, p, r) in salidas_posibles:
                    total += p * (r + gamma * V[s]) # Sumamos esperanzas sobre los posibles estados s' (Ecuación de Bellman)

                if (valor_opt is None) or (total > valor_opt):  # Nos quedamos con la acción maximizadora
                    valor_opt = total
                    accion_opt = accion

            controlador = max(controlador, abs(V[estado] - valor_opt))  # Por último, medimos cuanto ha cambiado el valor de los estados
            V[estado] = valor_opt
            A[estado] = accion_opt

        if controlador < 0.0001:   # Si el cambio es muy pequeño (insignificante), salimos del bucle. Ya no hay casi mejora
            break

    return V, A


# SIMULACIÓN RIO

def sim_rio(n_filas=7, n_columnas=6, n_islas=2, gamma=1):
    """
    1º Genera río aleatorio
    2º Lo imprime
    3º Ejecuta Value Iteration y obtiene política A
    4º Simula la partida siguiendo A
    
    """
    dicc_rio, inicio, final, river_strength = generar_rio(n_filas, n_columnas, n_islas)

    print("river_strength:", river_strength)
    print("Inicio:", inicio, "Final:", final)

    V, A = value_iteration(dicc_rio, n_filas, n_columnas, final, river_strength, gamma=gamma)
    estado = inicio
    total = 0

    imprimir_rio(dicc_rio, n_filas, n_columnas, estado, inicio, final)

    paso = 0
    while True:
        if estado == final:
            print(f"Llegaste a la salida en {paso-1} pasos. Recompensa total: {total}")
            return True
        
        paso += 1

        accion = A.get(estado, "stay")

        outcomes = funcion_transicion(dicc_rio, n_filas, n_columnas, river_strength, estado, accion, final)
        siguiete_estado, _, r = random.choices(outcomes, weights=[p for (_, p, _) in outcomes])[0]
        total += r

        print(f"Paso {paso}: estado = {estado} accion = {accion} -> {siguiete_estado} | r={r} | total = {total}")

        estado = siguiete_estado
        imprimir_rio(dicc_rio, n_filas, n_columnas, estado, inicio, final)
