"""Pruebas de la cinemática y del perfil. Corren con `colcon test`, sin ROS."""
import math

from brazo_control import cinematica as cin
from brazo_control import perfil


def test_directa_casos_de_control():
    """Los mismos tres casos que verifica el cuaderno de cinemática directa."""
    x, y, z = cin.directa([0.0, 0.0, 0.0, 0.0])          # brazo vertical
    assert abs(z - 0.515) < 1e-9 and abs(x) < 1e-9 and abs(y) < 1e-9
    x, y, z = cin.directa([0.0, 90.0, 0.0, 0.0])         # estirado horizontal
    assert abs(x - 0.325) < 1e-9 and abs(z - cin.H_HOMBRO) < 1e-9
    x, y, z = cin.directa([90.0, 90.0, 0.0, 0.0])        # base a 90 grados
    assert abs(y - 0.325) < 1e-9


def test_inversa_deshace_la_directa():
    """Componer las dos tiene que devolver el punto, en todo el alcanzable."""
    peor = 0.0
    for grados in range(-180, 180, 7):
        for mm in range(200, 290, 5):
            r = mm/1000.0
            x = r*math.cos(math.radians(grados))
            y = r*math.sin(math.radians(grados))
            q, motivo = cin.inversa(x, y, cin.Z_GARRA)
            if q is None:
                continue
            p = cin.directa(q)
            peor = max(peor, math.dist(p, (x, y, cin.Z_GARRA)))
    assert peor < 1e-9, f'error maximo {peor} m'


def test_la_inversa_es_una_funcion():
    """La ventana del codo deja una sola rama: nunca hay que elegir (ADR-011)."""
    for mm in range(200, 290, 5):
        q, _ = cin.inversa(mm/1000.0, 0.0, cin.Z_GARRA)
        assert q is not None and 0.0 <= q[2] <= 120.0


def test_rechazos_con_motivo():
    """Cada frontera del espacio de trabajo informa su propia razón."""
    assert cin.inversa(0.400, 0.0, cin.Z_GARRA)[1] == 'fuera de alcance'
    assert 'caja' in cin.inversa(0.197, 0.0, cin.Z_GARRA)[1]
    assert 'ventana' in cin.inversa(0.291, 0.0, cin.Z_GARRA)[1]


def test_guarda_contra_la_caja():
    """La pose que mete la muñeca en la caja con los cuatro ejes en ventana."""
    ok, motivo = cin.alcanzable([0.0, 110.0, 88.0, -108.0])
    assert not ok and 'caja' in motivo


def test_perfil_arranca_y_termina_quieto():
    assert perfil.s(0.0) == 0.0 and abs(perfil.s(1.0) - 1.0) < 1e-12
    h = 1e-6
    assert perfil.s(h)/h < 1e-4                     # velocidad inicial nula
    assert (1.0 - perfil.s(1.0 - h))/h < 1e-4       # y final también


def test_duracion_minima_respeta_el_tope_de_aceleracion():
    desde = [0.0, 94.249, 63.557, -67.806]          # agarre a r = 250
    hasta = [47.0, 94.249, 63.557, -67.806]         # el mismo punto, girado
    t = perfil.duracion_minima(desde, hasta)
    v, a = perfil.picos(desde, hasta, t)
    assert a <= perfil.A_TOPE*1.001, f'{a} m/s2 contra el tope {perfil.A_TOPE}'
    assert t > 1.0, 'un traslado de 200 mm no puede durar menos de un segundo'


def test_duracion_minima_respeta_la_velocidad_de_cada_eje():
    desde = [0.0, 50.0, 0.0, 40.0]
    hasta = [0.0, 110.0, 120.0, -108.0]
    t = perfil.duracion_minima(desde, hasta)
    for nombre, a, b in zip(cin.EJES, desde, hasta):
        w = perfil.K_V*math.radians(abs(b - a))/t
        assert w <= cin.VEL_MAX[nombre]*1.001, f'{nombre} a {w} rad/s'
