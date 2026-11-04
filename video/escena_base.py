"""Taller comun de las animaciones del brazo.

Acá vive todo lo que comparten los videos: las cotas, la paleta, los dos estilos
de dibujo, el escenario (mesa, caja, pedestal, ejes) y las piezas sueltas
—eslabones, articulaciones, rotulos, el panel de formulas—. Cada escena
importa esto y solo escribe sus propios tramos.

Los numeros no estan escritos a mano: salen de `brazo_anim.py`, que es la misma
cinematica del cuaderno y del nodo de ROS 2. Si cambia una cota, cambia el video.

Dos estilos de dibujo, el mismo guion
-------------------------------------
    alambre  lineas, circunferencias y poligonos ubicados en el espacio. Se lee
             como diagrama y renderiza dos ordenes de magnitud mas rapido.
    solido   esferas, cilindros y prismas de verdad, translucidos. Es mucho mas
             caro y es el que conviene dejar rendereando de noche.

El estilo se elige por la calidad del render: `-ql` usa alambre, `-qh` y `-qk`
usan solido. Se puede forzar con la variable de entorno BRAZO_ESTILO.

Variables de entorno
--------------------
    BRAZO_ESTILO=alambre|solido   fuerza el estilo
    BRAZO_MALLA=16                malla mas gruesa en las esferas
    BRAZO_LATEX=0                 texto unicode aunque haya LaTeX instalado
    BRAZO_TIEMPOS=1               imprime el minuto en que arranca cada tramo
"""
import math
import os
import shutil

import numpy as np
from manim import *

import brazo_anim as K

# ---------------------------------------------------------------- parametros
SC = 6.0                      # unidades de manim por metro
Q1 = 35.0                     # grados de base del punto de ejemplo
Z_OBJ = 0.070                 # el vaso se agarra a la altura de la garra
ALFA = 90.0                   # muñeca horizontal: el vaso no se inclina
OBJ = K.plano(K.R_VASO, Z_OBJ, Q1)   # el radio al que la tarea toma el vaso
# La pose de ejemplo no se elige: es la que resuelve la inversa para ese punto.
# Los tres videos cierran en ella, asi que terminan en el mismo brazo y en los
# mismos cuatro numeros.
Q = K.construir(*OBJ, ALFA)['elegida']['q']

C_BRAZO = "#e3e6df"
C_OBJ = "#ff6b5e"
C_MUN = "#f5b041"
C_E1 = "#5b9bff"
C_E2 = "#c89bff"
C_E3 = "#f5b041"
C_PLANO = "#4fd1a5"
C_OK = "#4fd1a5"
C_MAL = "#ff6b5e"
C_GRIS = "#8d949c"

ESTILO = os.environ.get("BRAZO_ESTILO") or (
    "solido" if config.pixel_height >= 1080 else "alambre")
SOLIDO = ESTILO == "solido"
# La malla crece con la resolucion de salida, no con el estilo: a 480p una
# esfera de 24x24 no se distingue de una de 12x12 y cuesta cuatro veces mas.
# Las esferas translucidas son lo que domina el tiempo de render, asi que
# BRAZO_MALLA baja la malla sin tocar la resolucion del video.
RES = int(os.environ.get("BRAZO_MALLA") or (
    12 if config.pixel_height < 1080 else (24 if config.pixel_height <= 1080 else 32)))
# con BRAZO_LATEX=0 se fuerza el texto unicode aunque LaTeX este instalado
HAY_LATEX = (shutil.which("latex") is not None
             and os.environ.get("BRAZO_LATEX", "1") != "0")
# BRAZO_TIEMPOS=1 imprime el minuto en que arranca cada tramo: es el guion para
# hablar arriba del video, y sale del propio render en vez de medirse a mano
TIEMPOS = bool(os.environ.get("BRAZO_TIEMPOS"))


def P(x, y, z):
    return np.array([x*SC, y*SC, z*SC])


def Pp(r, z, q1):
    return P(*K.plano(r, z, q1))


def unit(v):
    n = np.linalg.norm(v)
    return v/n if n > 1e-12 else np.array([1.0, 0.0, 0.0])


def T(latex, plano=None, color=WHITE, escala=0.5):
    """Una formula. Con LaTeX usa MathTex; sin LaTeX, el texto unicode."""
    if HAY_LATEX:
        return MathTex(latex, color=color).scale(escala)
    return Text(plano if plano is not None else latex, font_size=26,
                color=color).scale(escala/0.5*1.0)


def circulo(centro, u, v, radio, color, ancho=2.0, desde=0.0, hasta=TAU, opac=1.0):
    """Circunferencia o arco en el plano que generan u y v."""
    return ParametricFunction(
        lambda t: centro + radio*(math.cos(t)*u + math.sin(t)*v),
        t_range=[desde, hasta], color=color, stroke_width=ancho,
        stroke_opacity=opac)


def aristas(ancho, fondo, alto, color, grosor=2.0, opac=0.9):
    """Las doce aristas de un prisma apoyado en z=0 y centrado en el origen."""
    a, f = ancho/2, fondo/2
    base = [P(-a, -f, 0), P(a, -f, 0), P(a, f, 0), P(-a, f, 0)]
    tapa = [p + P(0, 0, alto) for p in base]
    g = VGroup()
    for i in range(4):
        g.add(Line(base[i], base[(i + 1) % 4], color=color, stroke_width=grosor))
        g.add(Line(tapa[i], tapa[(i + 1) % 4], color=color, stroke_width=grosor))
        g.add(Line(base[i], tapa[i], color=color, stroke_width=grosor))
    return g.set_stroke(opacity=opac)


def caja(ancho, fondo, alto, color, opac=0.9):
    """Un prisma: macizo translucido en solido, solo aristas en alambre.

    Las aristas se dibujan en los dos casos. En cairo el orden de dibujo entre
    superficies translucidas no siempre sale bien, y las aristas son lo que deja
    leer la forma cuando el relleno se superpone mal.
    """
    g = VGroup()
    if SOLIDO:
        g.add(Prism(dimensions=[ancho*SC, fondo*SC, alto*SC],
                    fill_opacity=0.22, fill_color=color, stroke_width=0.6,
                    stroke_color=color, stroke_opacity=0.35)
              .move_to(P(0, 0, alto/2)))
    else:
        a, f = ancho/2, fondo/2
        g.add(Polygon(P(-a, -f, alto), P(a, -f, alto), P(a, f, alto),
                      P(-a, f, alto), color=color, stroke_width=0,
                      fill_opacity=0.10, fill_color=color))
    g.add(aristas(ancho, fondo, alto, color, 2.0, opac))
    return g


def cilindro(centro, radio, alto, color, opac=0.18, res=None):
    r = res or min(18, max(10, RES))
    return Cylinder(radius=radio*SC, height=alto*SC, direction=Z_AXIS,
                    resolution=(2, r), fill_opacity=opac, fill_color=color,
                    checkerboard_colors=False, stroke_width=0.6,
                    stroke_color=color, stroke_opacity=0.3).move_to(centro)


def bola(centro, radio, color, opac=0.16):
    """La esfera de una restriccion de distancia.

    En solido es una esfera translucida con su malla visible; en alambre, unos
    meridianos y paralelos. En los dos casos se le agregan tres circunferencias
    maximas, que son las que hacen que el ojo lea una esfera y no una mancha.
    """
    g = VGroup()
    if SOLIDO:
        g.add(Sphere(center=centro, radius=radio*SC, resolution=(RES, RES),
                     fill_opacity=opac, fill_color=color,
                     checkerboard_colors=False, stroke_width=0.5,
                     stroke_color=color, stroke_opacity=0.45))
        for u, v in ((RIGHT, UP), (RIGHT, OUT), (UP, OUT)):
            g.add(circulo(centro, u, v, radio*SC, color, 1.8, opac=0.55))
    else:
        for k in range(6):
            a = k*PI/6
            g.add(circulo(centro, np.array([math.cos(a), math.sin(a), 0.0]),
                          OUT, radio*SC, color, 1.6, opac=0.5))
        for k in range(1, 4):
            h = radio*SC*math.cos(k*PI/4)
            rr = math.sqrt(max(0.0, (radio*SC)**2 - h**2))
            g.add(circulo(centro + np.array([0, 0, h]), RIGHT, UP, rr, color,
                          1.6, opac=0.5))
    return g


class BrazoEscena(ThreeDScene):
    """La escena con el escenario y las piezas; cada video pone sus tramos."""

    def correr(self, beats):
        """Corre los tramos en orden e imprime el guion si se lo piden."""
        self.camera.background_color = "#0b0e11"
        self.panel = VGroup()
        for nombre, beat in beats:
            if TIEMPOS:
                t = self.renderer.time
                print(f"  {int(t)//60}:{t % 60:04.1f}   {nombre}", flush=True)
            beat()

    # ------------------------------------------------ utilidades de escena
    def orientado(self, m):
        """Registra un objeto como siempre de frente, sin agregarlo todavia.

        `add_fixed_orientation_mobjects` agrega a la escena ademas de registrar,
        asi que un rotulo construido al principio de un tramo aparecia en
        pantalla antes de que lo tocara ninguna animacion. El registro queda
        hecho igual; lo unico que se saca es la aparicion anticipada, y la
        animacion que corresponda lo vuelve a agregar.
        """
        self.add_fixed_orientation_mobjects(m)
        self.remove(m)
        return m

    def fijo_al_cuadro(self, m, esquina=DR, buff=0.5):
        """Pega un objeto a una esquina de la pantalla, sin agregarlo todavia.

        Sirve para lo que es informacion y no geometria —una tabla, una
        referencia— que se lee mejor alineada al cuadro que parada en el
        espacio. Solo para objetos que no se redibujan: el registro toma la
        familia de glifos del momento, asi que uno que cambia de contenido tiene
        que ir en el mundo (`de_pie`) y no aca.
        """
        self.add_fixed_in_frame_mobjects(m)
        # el frame_center de la camara tambien corre a los objetos fijos al
        # cuadro, asi que hay que descontarlo
        m.to_corner(esquina, buff=buff).shift(self.camera.frame_center)
        self.remove(m)
        return m

    def nodo(self, p, color, radio=0.012):
        """Una articulacion.

        Las articulaciones son chicas en pantalla, asi que van a la mitad de la
        resolucion de malla: 12x12 ya se ve redonda y cuesta la cuarta parte que
        24x24. La malla fina se reserva para las esferas grandes, que son lo que
        hay que mirar.
        """
        if SOLIDO:
            r = max(8, RES//2)
            return Sphere(center=p, radius=radio*SC, resolution=(r, r),
                          fill_opacity=1.0, fill_color=color,
                          checkerboard_colors=False, stroke_width=0)
        return self.orientado(Dot(radius=radio*SC*0.9, color=color).move_to(p))

    def marca(self, p, color, radio=0.013):
        """Un punto de interes: el objetivo, la muñeca, un codo.

        El halo es un anillo plano y no una esfera envolvente: estas marcas
        quedan en escena casi todo el video y una esfera de malla fina por cada
        una era el gasto mas grande del render sin aportar nada que el anillo no
        diga.
        """
        if SOLIDO:
            g = VGroup(self.nodo(p, color, radio))
            for u, v in ((RIGHT, UP), (RIGHT, OUT), (UP, OUT)):
                g.add(circulo(p, u, v, radio*2.1*SC, color, 1.6, opac=0.5))
            return g
        return self.orientado(Dot(radius=radio*SC*0.9, color=color).move_to(p))

    def tubo(self, a, b, color, radio=0.011, res=None):
        """Un eslabon."""
        if SOLIDO:
            return Line3D(a, b, thickness=radio*SC, color=color,
                          resolution=(2, res or max(10, RES//2)))
        return Line(a, b, color=color, stroke_width=7)

    def de_pie(self, m, theta_grados):
        """Pone de pie un objeto plano, mirando a la camara de ese acimut."""
        m.rotate(PI/2, axis=RIGHT)
        m.rotate(math.radians(theta_grados) + PI/2, axis=OUT)
        return m

    def rotulo(self, texto, p, color, escala=0.46, plano=None):
        return self.orientado(T(texto, plano, color, escala).move_to(p))

    def flecha(self, a, b, color, ancho=4, radio=0.006):
        if SOLIDO:
            return Arrow3D(a, b, color=color, thickness=radio*SC,
                           base_radius=radio*SC*2.6, height=0.22,
                           resolution=(2, max(8, RES//2)))
        return Line(a, b, color=color, stroke_width=ancho).add_tip(
            tip_length=0.18, tip_width=0.12)

    def mostrar(self, *lineas):
        """El panel de arriba a la izquierda. Cada linea es (latex, plano)."""
        partes = []
        for l in lineas:
            latex, plano = l if isinstance(l, tuple) else (l, None)
            partes.append(T(latex, plano, WHITE, 0.5))
        nuevo = VGroup(*partes).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
        # primero se fija al cuadro y recien despues se ubica: al reves, la
        # esquina se calcula en coordenadas de escena y el panel se corta
        self.add_fixed_in_frame_mobjects(nuevo)
        # el frame_center de la camara tambien corre a los objetos fijos al
        # cuadro, asi que hay que descontarlo o el panel se sale por la izquierda
        nuevo.to_corner(UL, buff=0.5).shift(self.camera.frame_center)
        if len(self.panel):
            self.play(FadeOut(self.panel, shift=0.15*UP),
                      FadeIn(nuevo, shift=0.15*UP), run_time=0.7)
        else:
            self.play(FadeIn(nuevo), run_time=0.7)
        self.panel = nuevo

    def brazo_de(self, pose, color, q1=Q1, opac=1.0, liviano=False):
        """El brazo de una pose, con eslabones y articulaciones.

        `pose` es cualquier diccionario con 'pts': las cuatro articulaciones en
        coordenadas del plano, que es lo que devuelven tanto la directa como
        cada rama de la inversa.
        """
        pts = [Pp(r, z, q1) for r, z in pose['pts']]
        g = VGroup()
        for a, b in zip(pts, pts[1:]):
            if liviano:
                g.add(Line(a, b, color=color, stroke_width=7,
                           stroke_opacity=opac))
            else:
                g.add(self.tubo(a, b, color))
        if not liviano:
            for p in pts[1:-1]:
                g.add(self.nodo(p, color, 0.014))
        return g.set_opacity(opac) if opac < 1.0 and not SOLIDO else g

    def encuadre_plano(self, q1, pts):
        """Centro de camara para una vista dentro del plano del brazo.

        Se centra en el medio de la geometria que hay que mirar, y no en un
        punto fijo, que es lo que dejaba el brazo abajo a la izquierda.
        """
        rs = [r for r, _ in pts] + [0.0]
        zs = [z for _, z in pts] + [K.H_HOMBRO]
        return Pp((min(rs) + max(rs))/2, (min(zs) + max(zs))/2, q1)

    def copa(self, punto):
        """El vaso, apoyado en la mesa bajo ese punto."""
        rv, hv = K.VASO_D/2, K.VASO_H
        cx, cy = punto[0], punto[1]
        if SOLIDO:
            return VGroup(
                cilindro(P(cx, cy, hv/2), rv, hv, C_E1, 0.14),
                cilindro(P(cx, cy, hv*0.33), rv*0.93, hv*0.66, C_E1, 0.30),
                circulo(P(cx, cy, hv), RIGHT, UP, rv*SC, C_E1, 2.4))
        return VGroup(
            circulo(P(cx, cy, 0), RIGHT, UP, rv*SC, C_E1, 2),
            circulo(P(cx, cy, hv), RIGHT, UP, rv*SC, C_E1, 2),
            *[Line(P(cx + rv*math.cos(a), cy + rv*math.sin(a), 0),
                   P(cx + rv*math.cos(a), cy + rv*math.sin(a), hv),
                   color=C_E1, stroke_width=2)
              for a in np.arange(0, TAU, PI/3)])

    # --------------------------------------------------------- el escenario
    def escenario(self):
        self.set_camera_orientation(phi=66*DEGREES, theta=-58*DEGREES, zoom=1.45,
                                    frame_center=P(0.10, 0.07, 0.17))
        mesa = VGroup(
            Square(side_length=0.62*SC, stroke_color=C_GRIS, stroke_width=1.5,
                   fill_opacity=0.05, fill_color=C_GRIS).move_to(P(0.09, 0.05, 0)),
            *[Line(P(-0.13, y + 0.05, 0), P(0.49, y + 0.05, 0),
                   stroke_color=C_GRIS, stroke_width=0.7, stroke_opacity=0.3)
              for y in np.arange(-0.31, 0.32, 0.1)],
            *[Line(P(x + 0.09, -0.26, 0), P(x + 0.09, 0.36, 0),
                   stroke_color=C_GRIS, stroke_width=0.7, stroke_opacity=0.3)
              for x in np.arange(-0.31, 0.32, 0.1)])
        cja = caja(K.CAJA_W, K.CAJA_D, K.CAJA_H, C_GRIS)
        ped = caja(0.044, 0.044, K.H_HOMBRO - K.CAJA_H, C_GRIS)
        ped.shift(P(0, 0, K.CAJA_H))
        ejes = VGroup(
            self.flecha(P(0, 0, 0), P(0.30, 0, 0), C_MAL, 3),
            self.flecha(P(0, 0, 0), P(0, 0.30, 0), C_OK, 3),
            self.flecha(P(0, 0, 0), P(0, 0, 0.30), C_E1, 3),
            self.rotulo("x_0", P(0.33, 0, 0), C_MAL, plano="x0"),
            self.rotulo("y_0", P(0, 0.33, 0), C_OK, plano="y0"),
            self.rotulo("z_0", P(0, 0, 0.33), C_E1, plano="z0"))
        self.play(FadeIn(mesa), run_time=1.0)
        self.play(FadeIn(cja), FadeIn(ped), run_time=1.2)
        self.play(Create(ejes), run_time=1.3)
        self.ejes = ejes
        self.hombro = self.marca(P(0, 0, K.H_HOMBRO), C_BRAZO, 0.014)
        self.play(FadeIn(self.hombro, scale=1.6), run_time=0.6)
        self.wait(2)
