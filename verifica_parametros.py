#!/usr/bin/env python3
"""Comprueba que todas las copias de los parametros sigan de acuerdo.

El proyecto escribe las mismas cotas en varios lugares por razones legitimas:
los cuadernos las derivan y las explican, el URDF las necesita en su formato, el
nodo de ROS 2 corre instalado y sin acceso al repositorio, y la pagina HTML es
un archivo solo que tiene que funcionar sin conexion. Lo que no puede pasar es
que se desincronicen sin que nadie se entere: si manana ADR-010 cambia una
ventana, este script dice exactamente que archivo quedo atrasado.

    python3 verifica_parametros.py     ->  0 si todo coincide, 1 si hay deriva
"""
import math
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
import brazo_parametros as P   # noqa: E402

PAQUETE = RAIZ / 'ros2_ws' / 'src' / 'brazo_description'
URDF = PAQUETE / 'urdf' / 'brazo.urdf'
NODO = PAQUETE / 'scripts' / 'tarea.py'
CONTROL = (RAIZ / 'ros2_ws' / 'src' / 'brazo_control' / 'brazo_control'
           / 'cinematica.py')
PAGINAS = [p for p in (RAIZ / 'Wiki' / 'dh-brazo.html',
                       RAIZ / 'Wiki' / 'inversa-brazo.html') if p.exists()]
CUADERNOS = [RAIZ / 'Cinematica_brazo.ipynb', RAIZ / 'Jacobiano_brazo.ipynb',
             RAIZ / 'Cinematica_inversa_brazo.ipynb']

fallas, revisados = [], 0


def texto(ruta, una_linea=False):
    if ruta is None or not ruta.exists():
        return None
    t = ruta.read_text(encoding='utf-8')
    return re.sub(r'\s+', ' ', t) if una_linea else t


def revisar(archivo, etiqueta, patron, esperados, fuente, escala=1.0):
    """Busca uno o mas numeros con una expresion regular y los compara."""
    global revisados
    if fuente is None:
        print(f"  {etiqueta:<30} archivo ausente")
        return
    if not isinstance(esperados, (list, tuple)):
        esperados = (esperados,)
    m = re.search(patron, fuente)
    if not m or len(m.groups()) != len(esperados):
        fallas.append(f"{archivo}: no encuentro {etiqueta}")
        print(f"  {etiqueta:<30} NO ENCONTRADO")
        return
    revisados += len(esperados)
    hallados = [float(g)*escala for g in m.groups()]
    # el URDF imprime con tres decimales, asi que la tolerancia la fija ese redondeo
    ok = all(abs(h - e) < max(6e-4, abs(e)*5e-4) for h, e in zip(hallados, esperados))
    h = ', '.join(f'{v:g}' for v in hallados)
    e = ', '.join(f'{v:g}' for v in esperados)
    print(f"  {etiqueta:<30}{h:>18} {'=' if ok else '!='} {e}"
          f"{'' if ok else '   <-- DESINCRONIZADO'}")
    if not ok:
        fallas.append(f"{archivo}: {etiqueta} vale ({h}) y deberia ser ({e})")


def main():
    print("fuente de verdad: brazo_parametros.py")

    # ---------------- el URDF ----------------
    t = texto(URDF, una_linea=True)
    print(f"\n{URDF.name} (longitudes en m, angulos en rad)")
    revisar(URDF.name, 'alto de la caja',
            r'name="base" .*?origin xyz="0 0 ([\d.]+)"', P.CAJA_H/1000, t)
    revisar(URDF.name, 'pedestal',
            r'name="hombro" .*?origin xyz="0 0 ([\d.]+)"', P.PEDESTAL/1000, t)
    revisar(URDF.name, 'L1', r'name="codo" .*?origin xyz="0 0 ([\d.]+)"', P.L1/1000, t)
    revisar(URDF.name, 'L2', r'name="muneca" .*?origin xyz="0 0 ([\d.]+)"', P.L2/1000, t)
    revisar(URDF.name, 'L3', r'name="punta_fija" .*?origin xyz="0 0 ([\d.]+)"', P.L3/1000, t)
    for eje in ('base', 'hombro', 'codo', 'muneca', 'dedo'):
        nom = 'dedo_izq' if eje == 'dedo' else eje
        lo, hi = P.VENTANAS[eje]
        revisar(URDF.name, f'ventana {eje}',
                rf'name="{nom}" .*?lower="(-?[\d.]+)" upper="(-?[\d.]+)"',
                (math.radians(lo), math.radians(hi)), t)
        revisar(URDF.name, f'par y velocidad {eje}',
                rf'name="{nom}" .*?velocity="([\d.]+)" effort="([\d.]+)"',
                (P.vel_junta(eje), P.par_junta(eje)), t)

    # ---------------- el nodo de ROS 2 ----------------
    t = texto(NODO)
    print(f"\n{NODO.name} (en m)")
    revisar(NODO.name, 'eslabones', r'L1, L2, L3 = ([\d.]+), ([\d.]+), ([\d.]+)',
            (P.L1/1000, P.L2/1000, P.L3/1000), t)
    revisar(NODO.name, 'altura del hombro', r'H_HOMBRO = ([\d.]+)', P.H_HOMBRO/1000, t)
    revisar(NODO.name, 'caja y guarda', r'CAJA_H, R_GUARDA = ([\d.]+), ([\d.]+)',
            (P.CAJA_H/1000, P.R_GUARDA/1000), t)
    revisar(NODO.name, 'alturas y radio de la tarea',
            r'Z_GARRA, Z_ALTO, R_VASO = ([\d.]+), ([\d.]+), ([\d.]+)',
            (P.Z_GARRA/1000, P.Z_ALTO/1000, P.R_VASO/1000), t)
    revisar(NODO.name, 'giro de la tarea', r'GIRO, Q1_INICIAL = ([\d.]+)', P.GIRO_TAREA, t)
    for eje in ('hombro', 'codo', 'muneca'):
        revisar(NODO.name, f'ventana {eje}',
                rf"'{eje}': \((-?[\d.]+), (-?[\d.]+)\)", P.VENTANAS[eje], t)

    # ---------------- la biblioteca del paquete de control ----------------
    t = texto(CONTROL)
    print(f"\n{CONTROL.name} (en m)")
    revisar(CONTROL.name, 'eslabones', r'L1, L2, L3 = ([\d.]+), ([\d.]+), ([\d.]+)',
            (P.L1/1000, P.L2/1000, P.L3/1000), t)
    revisar(CONTROL.name, 'altura del hombro', r'H_HOMBRO = ([\d.]+)',
            P.H_HOMBRO/1000, t)
    revisar(CONTROL.name, 'caja y guarda', r'CAJA_H, R_GUARDA = ([\d.]+), ([\d.]+)',
            (P.CAJA_H/1000, P.R_GUARDA/1000), t)
    revisar(CONTROL.name, 'altura de agarre', r'Z_GARRA = ([\d.]+)', P.Z_GARRA/1000, t)
    for eje in ('base', 'hombro', 'codo', 'muneca'):
        revisar(CONTROL.name, f'ventana {eje}',
                rf"'{eje}': \((-?[\d.]+), (-?[\d.]+)\)", P.VENTANAS[eje], t)
        revisar(CONTROL.name, f'velocidad {eje}',
                rf"'{eje}': ([\d.]+)(?=[,}}])", P.vel_junta(eje),
                (t or '').split('VEL_MAX')[-1] if t else None)

    # ---------------- las paginas HTML ----------------
    for pagina in PAGINAS:
        t = texto(pagina)
        nom = pagina.name
        print(f"\n{nom} (en mm)")
        revisar(nom, 'eslabones',
                r'const L1 = ([\d.]+), L2 = ([\d.]+), L3 = ([\d.]+)', (P.L1, P.L2, P.L3), t)
        revisar(nom, 'altura del hombro', r'H_HOMBRO = ([\d.]+)', P.H_HOMBRO, t)
        revisar(nom, 'caja', r'CAJA_W = ([\d.]+), CAJA_D = ([\d.]+), CAJA_H = ([\d.]+)',
                (P.CAJA_W, P.CAJA_D, P.CAJA_H), t)
        if t and 'R_GUARDA = Math.ceil' in t:
            # esa pagina la deriva del radio de esquina en vez de escribirla
            print(f"  {'guarda':<30}{'derivada de R_CAJA':>18}")
        else:
            revisar(nom, 'guarda', r'R_GUARDA = ([\d.]+)', P.R_GUARDA, t)
        revisar(nom, 'altura de agarre', r'Z_GARRA = ([\d.]+)', P.Z_GARRA, t)
        for eje in ('hombro', 'codo', 'muneca'):
            clave = {'hombro': 'q2', 'codo': 'q3', 'muneca': 'q4'}[eje]
            revisar(nom, f'ventana {eje}',
                    rf'(?:{clave}|{eje}): \[(-?[\d.]+), (-?[\d.]+)\]', P.VENTANAS[eje], t)

    # ---------------- los cuadernos ----------------
    for cuaderno in CUADERNOS:
        t = texto(cuaderno)
        print(f"\n{cuaderno.name} (en mm)")
        revisar(cuaderno.name, 'eslabones',
                r'L1, L2, L3 = ([\d.]+), ([\d.]+), ([\d.]+)', (P.L1, P.L2, P.L3), t)
        revisar(cuaderno.name, 'altura del hombro', r'H_HOMBRO = ([\d.]+)', P.H_HOMBRO, t)

    print(f"\n{revisados} valores revisados")
    if fallas:
        print(f"{len(fallas)} DESINCRONIZACIONES:")
        for f in fallas:
            print('  -', f)
        return 1
    print('TODO SINCRONIZADO: las copias coinciden con brazo_parametros.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
