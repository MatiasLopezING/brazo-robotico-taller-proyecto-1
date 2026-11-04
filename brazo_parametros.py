"""Parametros adoptados del brazo: la unica fuente de verdad del proyecto.

Los cuadernos DERIVAN estos valores —de la fuente ATX, del criterio de vuelco,
del barrido de ventanas— y este archivo los REGISTRA ya adoptados, para que todo
lo que los consume salga del mismo lugar:

    genera_urdf.py          los escribe en brazo.urdf
    verifica_parametros.py  comprueba que las demas copias no se desincronicen

Si un calculo cambia un valor, se cambia aca y se corre verifica_parametros.py,
que dice que archivos quedaron atrasados. Las unidades son milimetros y grados,
que es como trabajan los cuadernos; el URDF las pasa a metros y radianes.
"""

# ---- geometria de la cadena (Dimensionamiento_brazo.ipynb, ADR-003) --------
L1 = 120.0          # eje del hombro al eje del codo
L2 = 120.0          # eje del codo al eje de la muneca
L3 = 85.0           # eje de la muneca a la punta de los dedos

# ---- la base (Cinematica_brazo.ipynb seccion 5, ADR-009) ------------------
PSU = (150.0, 86.0, 140.0)      # fuente ATX, formato PS/2: ancho, alto, profundidad
CAJA_W, CAJA_D, CAJA_H = 164.0, 154.0, 100.0
PEDESTAL = 90.0                 # altura del pedestal sobre la tapa
H_HOMBRO = CAJA_H + PEDESTAL    # 190 mm: altura del hombro sobre la mesa
R_VUELCO = min(CAJA_W, CAJA_D)/2        # 77 mm, el peor caso del criterio de vuelco
R_CAJA = (CAJA_W**2 + CAJA_D**2)**0.5/2  # 112,5 mm, el radio de esquina
R_GUARDA = 113.0                # el de esquina redondeado hacia afuera, para el firmware
TAU_HOMBRO, FS_VUELCO = 11.96, 1.5      # kg.cm y factor del criterio de vuelco

# ---- la tarea (Informe de Avance 1, requerimientos 3.1.2 a 3.1.4) ---------
VASO_D, VASO_H, M_VASO = 55.0, 90.0, 0.145      # mm, mm, kg
Z_GARRA = 70.0          # altura de la punta al agarrar: 20 mm bajo el borde
R_VASO = 250.0          # radio al que se toma y se deposita
Z_ALTO = 170.0          # altura de traslado
GIRO_TAREA = 47.0       # giro de base que separa los dos puntos 200 mm a R_VASO

# ---- ventanas de recorrido, en grados (ADR-010) ---------------------------
VENTANAS = {
    'base':   (-180.0, 180.0),
    'hombro': (50.0, 110.0),
    'codo':   (0.0, 120.0),
    'muneca': (-108.0, 40.0),
    'dedo':   (0.0, 62.0),      # cierre de cada mordaza (ADR-008)
}

# ---- la pinza (Pinza_brazo.ipynb, ADR-008) --------------------------------
PINZA_CERRADA, PINZA_ABIERTA = 55.0, 70.0       # apertura entre caras, mm
PINZA_PIVOTES, PINZA_DEDO = 45.0, 22.0          # separacion de pivotes y largo del dedo

# ---- actuadores (Transmision, ADR-001) ------------------------------------
SERVO_PAR = 9.52        # kg.cm del MG996R a 5 V
SERVO_VEL = 5.88        # rad/s sin carga: 0,17 s cada 60 grados
RELACION = {'base': 0.5, 'hombro': 3.0, 'codo': 1.5, 'muneca': 2/3, 'dedo': 1.0}
TOPE_VEL = {'base': 1.74}       # topes de firmware, rad/s

KG_CM_A_NM = 0.0981


def par_junta(eje):
    """Par disponible en la junta [N.m]: el del servo por la relacion."""
    return SERVO_PAR*KG_CM_A_NM*RELACION[eje]/(2 if eje == 'dedo' else 1)


def vel_junta(eje):
    """Velocidad maxima de la junta [rad/s], con el tope de firmware si lo hay."""
    return min(SERVO_VEL/RELACION[eje], TOPE_VEL.get(eje, 1e9))


if __name__ == '__main__':
    print(f"hombro a {H_HOMBRO:.0f} mm de la mesa, eslabones {L1:.0f}/{L2:.0f}/{L3:.0f} mm")
    print(f"caja {CAJA_W:.0f} x {CAJA_D:.0f} x {CAJA_H:.0f} mm, guarda en r = {R_GUARDA:.0f} mm")
    for eje, (lo, hi) in VENTANAS.items():
        print(f"  {eje:<8}{lo:>8.1f} a {hi:>7.1f} grados"
              f"   {par_junta(eje):6.3f} N.m   {vel_junta(eje):6.2f} rad/s")
