"""Cinematica del brazo para las animaciones: la misma de los cuadernos.

Las animaciones no dibujan numeros a mano. Todo lo que aparece en pantalla sale
de aca, y esto es una copia fiel de `brazo_control/cinematica.py`, que a su vez
sale de `brazo_parametros.py`. Si cambia una cota, cambia el video.

Unidades: metros y grados.
"""
import math

L1, L2, L3 = 0.120, 0.120, 0.085
H_HOMBRO = 0.190
CAJA_W, CAJA_D, CAJA_H = 0.164, 0.154, 0.100
R_GUARDA = 0.113
Z_GARRA, VASO_D, VASO_H = 0.070, 0.055, 0.090
R_VASO = 0.250

EJES = ('base', 'hombro', 'codo', 'muneca')
VENTANAS = {'base': (-180.0, 180.0), 'hombro': (50.0, 110.0),
            'codo': (0.0, 120.0), 'muneca': (-108.0, 40.0)}


def articulaciones(q2, q3, q4):
    """(r, z) de hombro, codo, muneca y punta, en el plano del brazo. Radianes."""
    a23, a234 = q2 + q3, q2 + q3 + q4
    codo = (L1*math.sin(q2), H_HOMBRO + L1*math.cos(q2))
    mun = (codo[0] + L2*math.sin(a23), codo[1] + L2*math.cos(a23))
    return [(0.0, H_HOMBRO), codo, mun,
            (mun[0] + L3*math.sin(a234), mun[1] + L3*math.cos(a234))]


def libre(q2, q3, q4):
    return all(z >= 0.0 and not (z < CAJA_H and abs(r) < R_GUARDA)
               for r, z in articulaciones(q2, q3, q4))


def en_ventana(q):
    return [n for n, v in zip(EJES, q)
            if not VENTANAS[n][0] - 1e-9 <= v <= VENTANAS[n][1] + 1e-9]


def construir(x, y, z, alfa=90.0):
    """Todas las cantidades intermedias de la inversa, que es lo que se anima."""
    q1 = math.degrees(math.atan2(y, x))
    r = math.hypot(x, y)
    a = math.radians(alfa)
    rm, zm = r - L3*math.sin(a), z - L3*math.cos(a)
    d = math.hypot(rm, zm - H_HOMBRO)
    paso = {'q1': q1, 'r': r, 'z': z, 'alfa': alfa, 'rm': rm, 'zm': zm, 'd': d,
            'alcanza': d <= L1 + L2, 'ramas': [], 'elegida': None,
            'motivo': 'fuera de alcance'}
    if not paso['alcanza']:
        return paso
    paso['semi'] = math.acos(min(1.0, d/(L1 + L2)))
    paso['medio'] = math.atan2(rm, zm - H_HOMBRO)
    for s in (1, -1):
        q2, q3 = paso['medio'] - s*paso['semi'], 2*s*paso['semi']
        q4 = a - q2 - q3
        q = [q1] + [math.degrees(v) for v in (q2, q3, q4)]
        fuera = en_ventana(q)
        choca = not fuera and not libre(q2, q3, q4)
        paso['ramas'].append({
            'nombre': 'codo abajo' if s > 0 else 'codo arriba', 'q': q,
            'pts': articulaciones(q2, q3, q4), 'sirve': not fuera and not choca,
            'fuera': fuera, 'choca': choca})
    paso['elegida'] = next((b for b in paso['ramas'] if b['sirve']), None)
    if paso['elegida']:
        paso['motivo'] = 'ok'
    elif any(b['choca'] for b in paso['ramas']):
        paso['motivo'] = 'chocaria la caja'
    else:
        paso['motivo'] = 'fuera de ventana'
    return paso


def plano(r, z, q1):
    """De coordenadas del plano del brazo a (x, y, z) del mundo. q1 en grados."""
    a = math.radians(q1)
    return (r*math.cos(a), r*math.sin(a), z)


def directa(q1, q2, q3, q4):
    """La cinematica directa, con los pasos intermedios que se animan.

    Los tres eslabones se suman como vectores, cada uno con su angulo absoluto
    medido desde la vertical: a2 = q2, a23 = q2+q3, a234 = q2+q3+q4. Todo en
    grados a la entrada; metros y grados a la salida.
    """
    angs = [q2, q2 + q3, q2 + q3 + q4]
    r, z, pasos = 0.0, H_HOMBRO, []
    for L, a in zip((L1, L2, L3), angs):
        rad = math.radians(a)
        dr, dz = L*math.sin(rad), L*math.cos(rad)
        pasos.append({'L': L, 'ang': a, 'dr': dr, 'dz': dz,
                      'desde': (r, z), 'hasta': (r + dr, z + dz)})
        r, z = r + dr, z + dz
    q = [q1, q2, q3, q4]
    return {'q': q, 'angs': angs, 'pasos': pasos, 'r': r, 'z': z,
            'alfa': angs[2], 'q1': q1,
            'x': r*math.cos(math.radians(q1)), 'y': r*math.sin(math.radians(q1)),
            'pts': articulaciones(*[math.radians(v) for v in (q2, q3, q4)]),
            'fuera': en_ventana(q),
            'choca': not libre(*[math.radians(v) for v in (q2, q3, q4)])}


def _por(A, B):
    """Producto de dos matrices 4x4, con listas y sin dependencias."""
    return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)]
            for i in range(4)]


def matriz_dh(theta, d, a, alfa):
    """A_i = Rot_z(theta) Tz(d) Tx(a) Rot_x(alfa). Angulos en grados, largos en m."""
    ct, st = math.cos(math.radians(theta)), math.sin(math.radians(theta))
    ca, sa = math.cos(math.radians(alfa)), math.sin(math.radians(alfa))
    return [[ct, -st*ca,  st*sa, a*ct],
            [st,  ct*ca, -ct*sa, a*st],
            [0.0,    sa,     ca,    d],
            [0.0,   0.0,    0.0,  1.0]]


def tabla_dh(q1, q2, q3, q4):
    """Las cuatro filas de la tabla, con los angulos de este brazo puestos.

    De los cuatro parametros de cada fila uno es la variable —siempre theta,
    porque las cuatro articulaciones son de giro— y los otros tres son
    constantes de construccion. La unica torsion del brazo es la de la base: es
    la que convierte el eje vertical en el eje horizontal del hombro.
    """
    return [('base',   q1,         H_HOMBRO, 0.0, -90.0),
            ('hombro', q2 - 90.0,  0.0,      L1,    0.0),
            ('codo',   q3,         0.0,      L2,    0.0),
            ('muneca', q4,         0.0,      L3,    0.0)]


def cadena_dh(q1, q2, q3, q4):
    """Los cinco sistemas, del 0 en la base al 4 en la punta de los dedos."""
    T = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    marcos = [T]
    for _, theta, d, a, alfa in tabla_dh(q1, q2, q3, q4):
        T = _por(T, matriz_dh(theta, d, a, alfa))
        marcos.append(T)
    return marcos


def origen(T):
    return (T[0][3], T[1][3], T[2][3])


def eje(T, k):
    """El versor del eje k (0=x, 1=y, 2=z) de ese sistema, en el mundo."""
    return (T[0][k], T[1][k], T[2][k])


def desvio_dh(q1, q2, q3, q4):
    """Cuanto se apartan los cinco origenes de DH de la cuenta geometrica.

    No compara solo la punta: tambien el codo y la muñeca, que son los que mira
    la guarda contra la caja. Verificar los sistemas intermedios es verificar la
    guarda, no solo el resultado final.
    """
    geo = articulaciones(*[math.radians(v) for v in (q2, q3, q4)])
    marcos = cadena_dh(q1, q2, q3, q4)
    return [math.dist(origen(T), plano(r, z, q1))
            for T, (r, z) in zip(marcos[1:], geo)]


def espacio(paso=2.0):
    """Los puntos (r, z) que alcanza la punta con las ventanas puestas.

    Recorre el hombro, el codo y la muñeca dentro de sus topes y se queda con
    las poses que ademas no invaden la guarda de la caja. Devuelve los puntos
    alcanzables y, aparte, los que descarta la guarda: la diferencia entre los
    dos es lo que cuesta tener la fuente abajo.
    """
    def rango(eje):
        lo, hi = VENTANAS[eje]
        return [lo + i*paso for i in range(int((hi - lo)/paso) + 1)]

    libres, vetados = [], []
    for q2 in rango('hombro'):
        for q3 in rango('codo'):
            for q4 in rango('muneca'):
                a2, a3, a4 = (math.radians(v) for v in (q2, q3, q4))
                punta = articulaciones(a2, a3, a4)[3]
                (libres if libre(a2, a3, a4) else vetados).append(punta)
    return libres, vetados


def limite_alcance(z, alfa=90.0):
    """El radio donde d = L1+L2: el brazo estirado. Mas afuera no hay solucion.

    d^2 = rm^2 + (zm - Z0)^2 con rm = r - L3 sen(alfa) y zm = z - L3 cos(alfa),
    asi que despejar r es directo.
    """
    a = math.radians(alfa)
    zm = z - L3*math.cos(a)
    dentro = (L1 + L2)**2 - (zm - H_HOMBRO)**2
    if dentro <= 0.0:
        return 0.0
    return L3*math.sin(a) + math.sqrt(dentro)


def banda(z, alfa=90.0, paso=0.0001):
    """El tramo de radios con solucion aceptada, a esa altura y esa muñeca.

    Lo mide en vez de declararlo: recorre el radio y se queda con el primero y
    el ultimo que pasan las ventanas y la guarda de la caja. Asi el video no
    puede desmentir al cuaderno.
    """
    utiles = [round(i*paso, 6)
              for i in range(1, int(limite_alcance(z, alfa)/paso) + 1)
              if construir(*plano(i*paso, z, 0.0), alfa)['elegida']]
    return (min(utiles), max(utiles)) if utiles else (0.0, 0.0)
