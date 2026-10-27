"""Perfil temporal de los movimientos: de un camino a una trayectoria.

Un camino es una secuencia de puntos; una trayectoria es ese camino con marca
temporal, y se le exige ser suave —velocidad y aceleracion continuas—. Acá eso
se resuelve con el polinomio de quinto orden

    s(t) = 10 t^3 - 15 t^4 + 6 t^5,   t = tiempo / duracion

que arranca y termina con velocidad y aceleracion nulas. Sus picos salen de la
forma, no del recorrido: v = 1,875 D/T y a = 5,77 D/T^2.

Por que importa: el dimensionamiento del brazo supone movimiento cuasi-estatico,
con un tope de aceleracion de la punta de 0,98 m/s^2 que sale del criterio del
10 % para despreciar el termino dinamico. Una interpolacion lineal entre dos
angulos tiene velocidad discontinua en los extremos, o sea aceleracion infinita
en el papel, y viola ese supuesto.
"""
import math

from . import cinematica as cin

A_TOPE = 0.98                      # m/s2, tope de aceleracion de la punta
K_V, K_A = 1.875, 5.7735           # picos del quintico, por unidad de recorrido


def s(t):
    """El perfil normalizado, con t de 0 a 1."""
    t = min(1.0, max(0.0, t))
    return t*t*t*(10.0 + t*(-15.0 + 6.0*t))


def duracion_minima(q_desde, q_hasta):
    """Duracion [s] mas corta que respeta el tope de aceleracion y los de velocidad.

    Manda el mas exigente de dos criterios: la aceleracion de la punta, que mira
    cuanto se mueve el TCP en el espacio, y la velocidad de cada articulacion,
    que no son iguales entre si.
    """
    p0, p1 = cin.directa(q_desde), cin.directa(q_hasta)
    recorrido = math.dist(p0, p1)
    t = math.sqrt(K_A*recorrido/A_TOPE) if recorrido > 1e-9 else 0.0
    for nombre, a, b in zip(cin.EJES, q_desde, q_hasta):
        salto = math.radians(abs(b - a))
        if salto > 1e-9:
            t = max(t, K_V*salto/cin.VEL_MAX[nombre])
    return max(t, 0.25)            # ningun tramo instantaneo, por prolijidad


def muestrear(q_desde, q_hasta, duracion, periodo=0.02):
    """[(t, q)] de la trayectoria, con el perfil suave entre las dos poses."""
    n = max(1, int(round(duracion/periodo)))
    salida = []
    for i in range(n + 1):
        t = min(duracion, i*periodo)
        u = s(t/duracion) if duracion > 1e-9 else 1.0
        salida.append((t, [a + (b - a)*u for a, b in zip(q_desde, q_hasta)]))
    return salida


def picos(q_desde, q_hasta, duracion):
    """(velocidad, aceleracion) maximas de la punta [m/s, m/s2], para informar."""
    recorrido = math.dist(cin.directa(q_desde), cin.directa(q_hasta))
    if duracion <= 1e-9:
        return float('inf'), float('inf')
    return K_V*recorrido/duracion, K_A*recorrido/duracion**2
