#!/usr/bin/env python3
"""Verifica que el URDF describe el mismo brazo que los cuadernos de calculo.

Recorre la cadena del URDF con un lector propio —solo xml y numpy, sin ROS— y
compara la posicion de la punta contra la formula de la cinematica directa en
configuraciones al azar. Si estan instalados, cruza ademas contra yourdfpy y
contra el Robotics Toolbox de Peter Corke, que leen el archivo por su cuenta.

    python3 verifica_urdf.py [ruta al brazo.urdf]
"""
import math
import pathlib
import sys
import xml.etree.ElementTree as ET

import numpy as np

L1, L2, L3, H_HOMBRO = 0.120, 0.120, 0.085, 0.190
EJES = ['base', 'hombro', 'codo', 'muneca']


def directa(q1, q2, q3, q4):
    """La formula que ejecuta el firmware, en metros."""
    a2, a23, a234 = q2, q2 + q3, q2 + q3 + q4
    r = L1*math.sin(a2) + L2*math.sin(a23) + L3*math.sin(a234)
    z = H_HOMBRO + L1*math.cos(a2) + L2*math.cos(a23) + L3*math.cos(a234)
    return np.array([r*math.cos(q1), r*math.sin(q1), z])


def rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = (math.cos(r), math.sin(r), math.cos(p),
                              math.sin(p), math.cos(y), math.sin(y))
    return np.array([[cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr],
                     [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr],
                     [-sp,   cp*sr,            cp*cr]])


def homogenea(R, t):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, t
    return T


def rot_eje(eje, ang):
    k = np.asarray(eje, dtype=float)
    k /= np.linalg.norm(k)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang)*K + (1 - math.cos(ang))*(K @ K)


class Urdf:
    """Lector minimo: lo justo para recorrer una cadena de juntas de giro."""

    def __init__(self, ruta):
        raiz = ET.parse(ruta).getroot()
        self.juntas = {}
        for j in raiz.findall('joint'):
            o = j.find('origin')
            xyz = [float(v) for v in (o.get('xyz', '0 0 0').split() if o is not None
                                      else '0 0 0'.split())]
            r, p, y = [float(v) for v in (o.get('rpy', '0 0 0').split()
                                          if o is not None else '0 0 0'.split())]
            a = j.find('axis')
            eje = [float(v) for v in a.get('xyz').split()] if a is not None else [0, 0, 1]
            lim = j.find('limit')
            self.juntas[j.get('name')] = {
                'tipo': j.get('type'),
                'padre': j.find('parent').get('link'),
                'hijo': j.find('child').get('link'),
                'T': homogenea(rpy(r, p, y), np.array(xyz)),
                'eje': eje,
                'rango': (float(lim.get('lower')), float(lim.get('upper')))
                if lim is not None else None}

    def pose(self, destino, q):
        """Transformada de base_link a 'destino' con los angulos q [rad]."""
        cadena, link = [], destino
        while link != 'base_link':
            for nom, j in self.juntas.items():
                if j['hijo'] == link:
                    cadena.append(nom)
                    link = j['padre']
                    break
            else:
                raise RuntimeError(f'{link} no cuelga de base_link')
        T = np.eye(4)
        for nom in reversed(cadena):
            j = self.juntas[nom]
            T = T @ j['T']
            if j['tipo'] == 'revolute':
                T = T @ homogenea(rot_eje(j['eje'], q.get(nom, 0.0)), np.zeros(3))
        return T


def main():
    ruta = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
        pathlib.Path(__file__).resolve().parent.parent / 'urdf' / 'brazo.urdf'
    print(f'URDF: {ruta}')
    u = Urdf(ruta)

    print('\nventanas declaradas en el URDF:')
    for nom in EJES:
        lo, hi = u.juntas[nom]['rango']
        print(f'  {nom:<8}{math.degrees(lo):>8.1f} a {math.degrees(hi):>7.1f} grados')

    rng = np.random.default_rng(11)
    Q = rng.uniform(-math.pi, math.pi, size=(5000, 4))
    peor = 0.0
    for q in Q:
        T = u.pose('punta', dict(zip(EJES, q)))
        peor = max(peor, float(np.max(np.abs(T[:3, 3] - directa(*q)))))
    print(f'\nlector propio contra la formula del firmware, {len(Q)} poses: '
          f'{peor:.2e} m')
    ok = peor < 1e-9

    try:
        import yourdfpy
        r = yourdfpy.URDF.load(str(ruta))
        peor2 = 0.0
        for q in Q[:1000]:
            r.update_cfg(dict(zip(EJES, q)) | {'dedo_izq': 0.0})
            T = r.get_transform('punta', 'base_link')
            peor2 = max(peor2, float(np.max(np.abs(T[:3, 3] - directa(*q)))))
        print(f'yourdfpy contra la formula del firmware, 1000 poses:       {peor2:.2e} m')
        ok = ok and peor2 < 1e-9
    except ImportError:
        print('yourdfpy no instalado (pip install yourdfpy): cruce omitido')

    try:
        import roboticstoolbox as rtb
        brazo = rtb.DHRobot([
            rtb.RevoluteDH(d=H_HOMBRO, a=0.0, alpha=-math.pi/2),
            rtb.RevoluteDH(a=L1, offset=-math.pi/2),
            rtb.RevoluteDH(a=L2),
            rtb.RevoluteDH(a=L3)])
        peor3 = 0.0
        for q in Q[:1000]:
            T = u.pose('punta', dict(zip(EJES, q)))
            peor3 = max(peor3, float(np.max(np.abs(T[:3, 3] - brazo.fkine(q).t))))
        print(f'URDF contra la tabla Denavit-Hartenberg del toolbox:       {peor3:.2e} m')
        ok = ok and peor3 < 1e-9
    except ImportError:
        print('roboticstoolbox no instalado: cruce omitido')

    print('\n' + ('VERIFICADO: el URDF y los cuadernos describen el mismo brazo.'
                  if ok else 'ATENCION: hay discrepancias, revisar el modelo.'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
