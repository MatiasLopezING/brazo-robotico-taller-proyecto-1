#!/usr/bin/env python3
"""Genera brazo.urdf a partir de brazo_parametros.py.

El URDF no es una fuente nueva de numeros: toma los parametros adoptados del
proyecto y los escribe en el formato que entienden ROS 2, MoveIt, MATLAB
(importrobot) y cualquier otro visor. Si una cota cambia, se cambia en
brazo_parametros.py y se vuelve a correr esto.
"""
import math
import pathlib
import sys


def _parametros():
    """brazo_parametros.py vive en la raiz del repositorio, unos niveles arriba."""
    aqui = pathlib.Path(__file__).resolve()
    for padre in aqui.parents:
        if (padre / 'brazo_parametros.py').exists():
            sys.path.insert(0, str(padre))
            import brazo_parametros
            return brazo_parametros
    raise SystemExit('no encuentro brazo_parametros.py: correr desde el repositorio')


P = _parametros()
M = 0.001                                 # los parametros estan en mm, el URDF en metros

SECCION = (0.030, 0.040)                  # seccion de dibujo de los eslabones
PALMA = (0.045, 0.040)                    # ancho y alto del cuerpo de la pinza
DEDO = (0.012, 0.015, 0.022)              # dedo: ancho, alto, largo


def rad(x):
    return f"{math.radians(x):.6f}"


def n(x):
    return f"{x:.6g}"


def cuerpo(dim, centro, material):
    d = f'{n(dim[0])} {n(dim[1])} {n(dim[2])}'
    c = f'{n(centro[0])} {n(centro[1])} {n(centro[2])}'
    return f"""    <visual>
      <origin xyz="{c}" rpy="0 0 0"/>
      <geometry><box size="{d}"/></geometry>
      <material name="{material}"/>
    </visual>
    <collision>
      <origin xyz="{c}" rpy="0 0 0"/>
      <geometry><box size="{d}"/></geometry>
    </collision>"""


def junta(nombre, padre, hijo, xyz, eje, clave, extra=""):
    lo, hi = P.VENTANAS[clave]
    return f"""  <joint name="{nombre}" type="revolute">
    <parent link="{padre}"/>
    <child link="{hijo}"/>
    <origin xyz="{xyz}" rpy="0 0 0"/>
    <axis xyz="{eje}"/>
    <limit lower="{rad(lo)}" upper="{rad(hi)}" velocity="{P.vel_junta(clave):.3f}" effort="{P.par_junta(clave):.3f}"/>
{extra}  </joint>
"""


L1, L2, L3 = P.L1*M, P.L2*M, P.L3*M
CAJA = (P.CAJA_W*M, P.CAJA_D*M, P.CAJA_H*M)
PED = (0.044, 0.044, P.PEDESTAL*M)

U = [f"""<?xml version="1.0"?>
<!-- Brazo robotico teleoperado - Taller de Proyecto I (E0306), Grupo N 3, UNLP
     GENERADO por genera_urdf.py a partir de brazo_parametros.py, que es la
     unica fuente de cotas del proyecto. No editar a mano: editar los parametros
     y volver a generar. verifica_parametros.py avisa si alguna copia quedo
     atrasada, y verifica_urdf.py comprueba que este archivo describe la misma
     cinematica que los cuadernos.

     Convencion de ejes: z hacia arriba, x hacia adelante (el radio del brazo).
     Cada junta de giro tiene su eje en y, salvo la base, que gira en z, de modo
     que el angulo de cada junta ES el angulo del cuaderno:
       base    q1, desde una direccion de referencia
       hombro  q2, desde la vertical
       codo    q3, desde el eslabon anterior
       muneca  q4, desde el eslabon anterior
     Equivale a la tabla de Denavit-Hartenberg documentada en la wiki, donde
     theta2 = q2 - 90 por el corrimiento que impone el metodo.

     Sin bloques <inertial>: las piezas todavia no estan modeladas en 3D, asi
     que no hay masas ni tensores medidos y no se inventan. El modelo sirve para
     visualizar, verificar cinematica y planificar; para simular dinamica en
     Gazebo hay que agregarlos. -->
<robot name="brazo_grupo3">

  <material name="gris"><color rgba="0.82 0.83 0.80 1.0"/></material>
  <material name="grafito"><color rgba="0.23 0.25 0.28 1.0"/></material>
  <material name="acento"><color rgba="0.60 0.36 0.08 1.0"/></material>

  <!-- caja base: aloja la fuente ATX y la chapa de lastre (ADR-009) -->
  <link name="base_link">
{cuerpo(CAJA, (0, 0, CAJA[2]/2), 'gris')}
  </link>
""",
     junta('base', 'base_link', 'columna', f'0 0 {n(CAJA[2])}', '0 0 1', 'base'),
     f"""  <!-- pedestal sobre la tapa: levanta el hombro a {P.H_HOMBRO:.0f} mm de la mesa -->
  <link name="columna">
{cuerpo(PED, (0, 0, PED[2]/2), 'grafito')}
  </link>
""",
     junta('hombro', 'columna', 'brazo', f'0 0 {n(PED[2])}', '0 1 0', 'hombro'),
     f"""  <link name="brazo">
{cuerpo((SECCION[0], SECCION[1], L1), (0, 0, L1/2), 'acento')}
  </link>
""",
     junta('codo', 'brazo', 'antebrazo', f'0 0 {n(L1)}', '0 1 0', 'codo'),
     f"""  <link name="antebrazo">
{cuerpo((SECCION[0], SECCION[1], L2), (0, 0, L2/2), 'acento')}
  </link>
""",
     junta('muneca', 'antebrazo', 'palma', f'0 0 {n(L2)}', '0 1 0', 'muneca'),
     f"""  <!-- palma: del eje de la muneca a la punta de los dedos hay L3 = {P.L3:.0f} mm -->
  <link name="palma">
{cuerpo((PALMA[0], PALMA[1], L3 - DEDO[2]), (0, 0, (L3 - DEDO[2])/2), 'grafito')}
  </link>
"""]

for lado, signo in (('izq', 1), ('der', -1)):
    extra = ('    <mimic joint="dedo_izq" multiplier="1.0" offset="0.0"/>\n'
             if lado == 'der' else '')
    U.append(junta(f'dedo_{lado}', 'palma', f'dedo_{lado}_link',
                   f'{n(signo*P.PINZA_PIVOTES*M/2)} 0 {n(L3 - DEDO[2])}',
                   f'0 {signo} 0', 'dedo', extra))
    U.append(f"""  <link name="dedo_{lado}_link">
{cuerpo(DEDO, (-signo*DEDO[0]/2, 0, DEDO[2]/2), 'acento')}
  </link>
""")

U.append(f"""  <!-- punta: el punto que calculan los cuadernos, entre las dos mordazas -->
  <joint name="punta_fija" type="fixed">
    <parent link="palma"/>
    <child link="punta"/>
    <origin xyz="0 0 {n(L3)}" rpy="0 0 0"/>
  </joint>
  <link name="punta"/>

  <!-- la mesa, como referencia de altura cero -->
  <joint name="mesa_fija" type="fixed">
    <parent link="base_link"/>
    <child link="mesa"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>
  <link name="mesa"/>

</robot>
""")

salida = pathlib.Path(__file__).resolve().parent.parent / 'urdf' / 'brazo.urdf'
if not salida.parent.exists():
    salida = pathlib.Path(__file__).with_name('brazo.urdf')
salida.write_text("".join(U), encoding='utf-8')
print('escrito:', salida, f'({salida.stat().st_size} bytes)')
