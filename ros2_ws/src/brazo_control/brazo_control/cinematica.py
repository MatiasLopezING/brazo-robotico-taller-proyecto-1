"""Cinematica del brazo del Grupo 3: directa, inversa y los limites.

Es la misma matematica de los cuadernos `Cinematica_brazo.ipynb`,
`Cinematica_inversa_brazo.ipynb` y `Jacobiano_brazo.ipynb`, escrita una sola vez
para que la usen los nodos. No depende de ROS ni de numpy: solo `math`, asi que
se puede probar con pytest sin levantar nada.

Unidades: metros y radianes hacia afuera; los angulos de articulacion se
manejan en GRADOS, que es como estan documentados.
"""
import math

# ---- cotas adoptadas (brazo_parametros.py, en metros) ---------------------
L1, L2, L3 = 0.120, 0.120, 0.085
H_HOMBRO = 0.190
CAJA_H, R_GUARDA = 0.100, 0.113
Z_GARRA = 0.070
ALFA_CON_VASO = 90.0                 # grados: la pinza va horizontal con el vaso

EJES = ('base', 'hombro', 'codo', 'muneca')
VENTANAS = {'base': (-180.0, 180.0), 'hombro': (50.0, 110.0),
            'codo': (0.0, 120.0), 'muneca': (-108.0, 40.0)}
VEL_MAX = {'base': 1.74, 'hombro': 1.96, 'codo': 3.92, 'muneca': 8.82}  # rad/s


def directa(q):
    """(x, y, z) [m] de la punta para q = (base, hombro, codo, muneca) [grados]."""
    q1, q2, q3, q4 = (math.radians(v) for v in q)
    a23, a234 = q2 + q3, q2 + q3 + q4
    r = L1*math.sin(q2) + L2*math.sin(a23) + L3*math.sin(a234)
    z = H_HOMBRO + L1*math.cos(q2) + L2*math.cos(a23) + L3*math.cos(a234)
    return r*math.cos(q1), r*math.sin(q1), z


def articulaciones(q2, q3, q4):
    """(r, z) de hombro, codo, muneca y punta, en el plano del brazo. Radianes."""
    a23, a234 = q2 + q3, q2 + q3 + q4
    codo = (L1*math.sin(q2), H_HOMBRO + L1*math.cos(q2))
    mun = (codo[0] + L2*math.sin(a23), codo[1] + L2*math.cos(a23))
    return [(0.0, H_HOMBRO), codo, mun,
            (mun[0] + L3*math.sin(a234), mun[1] + L3*math.cos(a234))]


def libre(q2, q3, q4):
    """La guarda de ADR-010: nada bajo la tapa dentro del radio de esquina."""
    return all(z >= 0.0 and not (z < CAJA_H and abs(r) < R_GUARDA)
               for r, z in articulaciones(q2, q3, q4))


def en_ventana(q):
    """Los ejes que se salieron de su ventana de recorrido, en orden."""
    return [n for n, v in zip(EJES, q)
            if not VENTANAS[n][0] - 1e-9 <= v <= VENTANAS[n][1] + 1e-9]


def inversa(x, y, z, alfa=ALFA_CON_VASO):
    """Angulos [grados] para la punta en (x, y, z) [m] con la pinza a alfa.

    Devuelve (q, motivo). Si no hay solucion, q es None y motivo dice por que,
    que es lo que el nodo informa al rechazar la meta (ADR-011).
    """
    q1 = math.degrees(math.atan2(y, x))
    r = math.hypot(x, y)
    a = math.radians(alfa)
    rm, zm = r - L3*math.sin(a), z - L3*math.cos(a)        # desacople de muneca
    d = math.hypot(rm, zm - H_HOMBRO)
    if d > L1 + L2:
        return None, 'fuera de alcance'

    semi = math.acos(min(1.0, d/(L1 + L2)))                # L1 = L2: isosceles
    medio = math.atan2(rm, zm - H_HOMBRO)
    ejes_fuera, choca = [], False
    for s in (1, -1):                                      # codo abajo y arriba
        q2, q3 = medio - s*semi, 2*s*semi
        q4 = a - q2 - q3
        q = [q1] + [math.degrees(v) for v in (q2, q3, q4)]
        fuera = en_ventana(q)
        if fuera:
            ejes_fuera += [e for e in fuera if e not in ejes_fuera]
            continue
        if not libre(q2, q3, q4):
            choca = True
            continue
        return q, 'ok'
    # ninguna de las dos ramas sirve: se informa la razon, que es lo que el nodo
    # devuelve al rechazar la meta
    if choca:
        return None, 'el brazo chocaria la caja'
    return None, 'fuera de ventana: ' + ', '.join(ejes_fuera)


def alcanzable(q):
    """Una pose en angulos: (sirve, motivo). Para validar poses memorizadas."""
    fuera = en_ventana(q)
    if fuera:
        return False, 'fuera de ventana: ' + ', '.join(fuera)
    if not libre(*(math.radians(v) for v in q[1:])):
        return False, 'el brazo chocaria la caja'
    return True, 'ok'
