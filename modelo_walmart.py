from pulp import LpProblem, LpMinimize, LpVariable, lpSum, value, PULP_CBC_CMD

# ── Nodos ────────────────────────────────────────────────────
NODOS = {
    1:  "CEDI Coyol",
    2:  "Heredia",
    3:  "Escazú",
    4:  "San José",
    5:  "Cartago",
    6:  "Tarrazú",
    7:  "San Isidro",
    8:  "Atenas",
    9:  "Orotina",
    10: "Jacó",
    11: "Quepos",
    12: "Dominical",
    13: "Pérez Zeledón",
}

ORIGEN  = 1
DESTINO = 13

# ── Arcos base (desde, hasta): minutos ───────────────────────
ARCOS_BASE = {
    (1,  2):  28,
    (1,  3):  32,
    (1,  8):  25,
    (2,  4):  45,
    (3,  4):  35,
    (4,  5):  55,
    (4,  6):  85,
    (5,  7):  90,
    (6,  7):  75,
    (7,  13): 45,
    (8,  9):  20,
    (9,  10): 40,
    (10, 11): 55,
    (11, 12): 45,
    (12, 13): 45,
}

# Coordenadas aproximadas para el mapa (lon, lat)
COORDS = {
    1:  (-84.22, 10.00),   # CEDI Coyol
    2:  (-84.12, 10.00),   # Heredia
    3:  (-84.14,  9.93),   # Escazú
    4:  (-84.08,  9.93),   # San José
    5:  (-83.92,  9.86),   # Cartago
    6:  (-84.00,  9.65),   # Tarrazú
    7:  (-83.71,  9.39),   # San Isidro
    8:  (-84.39,  9.98),   # Atenas
    9:  (-84.53,  9.90),   # Orotina
    10: (-84.63,  9.73),   # Jacó
    11: (-84.16,  9.44),   # Quepos
    12: (-83.90,  9.25),   # Dominical
    13: (-83.71,  9.37),   # Pérez Zeledón
}


def resolver(tiempos: dict = None) -> dict:
    """
    Resuelve el camino más corto de CEDI Coyol a Pérez Zeledón.

    Parámetros
    ----------
    tiempos : dict opcional {(desde, hasta): minutos}
              Si no se pasa, usa ARCOS_BASE.

    Retorna
    -------
    dict con ruta óptima, tiempo total, arcos activos y estado.
    """
    t = tiempos if tiempos is not None else ARCOS_BASE.copy()

    modelo = LpProblem("Walmart_CaminoCorto", LpMinimize)

    # Variables binarias por arco
    x = {arco: LpVariable(f"x_{arco[0]}_{arco[1]}", cat="Binary") for arco in t}

    # Función objetivo
    modelo += lpSum(t[arco] * x[arco] for arco in t), "TiempoTotal"

    # Restricciones de flujo en cada nodo
    for n in NODOS:
        sale   = lpSum(x[arco] for arco in t if arco[0] == n)
        entra  = lpSum(x[arco] for arco in t if arco[1] == n)
        if n == ORIGEN:
            modelo += (sale - entra) == 1,  f"flujo_{n}"
        elif n == DESTINO:
            modelo += (sale - entra) == -1, f"flujo_{n}"
        else:
            modelo += (sale - entra) == 0,  f"flujo_{n}"

    modelo.solve(PULP_CBC_CMD(msg=0))

    arcos_activos = [arco for arco in t if x[arco].varValue is not None and x[arco].varValue > 0.5]

    # Reconstruir ruta ordenada
    mapa_siguiente = {a: b for (a, b) in arcos_activos}
    ruta = [ORIGEN]
    actual = ORIGEN
    for _ in range(len(NODOS)):
        siguiente = mapa_siguiente.get(actual)
        if siguiente is None:
            break
        ruta.append(siguiente)
        actual = siguiente
        if actual == DESTINO:
            break

    return {
        "estado":        modelo.status,
        "tiempo_total":  value(modelo.objective),
        "arcos_activos": arcos_activos,
        "ruta":          ruta,
        "tiempos":       t,
    }
