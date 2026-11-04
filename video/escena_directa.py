"""E2 - Cinematica directa: de los cuatro angulos a donde queda el vaso.

Pensada como fondo de una presentacion hablada: casi no hay texto, hay
matematica. Cada estado clave queda quieto varios segundos para que haya tiempo
de explicarlo en vivo.

Sigue el orden del cuaderno `Cinematica_brazo.ipynb`: primero la convencion de
angulos, que la documentacion tenia contradictoria; despues la suma de los
eslabones como vectores; despues los casos de control; y al final el espacio de
trabajo con los recorridos que dejo la transmision.

El escenario, la paleta, los dos estilos de dibujo y las piezas sueltas salen de
`escena_base.py`; las cotas y los angulos, de `brazo_anim.py`. La pose de
ejemplo es la misma con la que cierra E4, asi que los dos videos terminan en el
mismo brazo y en los mismos cuatro numeros.

    manim -ql escena_directa.py Directa                  # 480p15 alambre
    manim -qh --fps 30 escena_directa.py Directa         # 1080p30 solido
    manim -qk --fps 60 escena_directa.py Directa         # 2160p60 solido

El README del directorio tiene los tiempos de render y las variables de entorno.
"""
import math

import numpy as np
from manim import *

import brazo_anim as K
from escena_base import *   # noqa: F401,F403

POSE = K.directa(*Q)   # Q es la pose de ejemplo compartida, de escena_base

# Los dos casos de control del cuaderno. Ninguno es una pose alcanzable (el
# hombro arranca en 50 grados); son la verificacion de que la formula da lo que
# tiene que dar en los dos extremos donde se sabe la respuesta de memoria.
VERTICAL = K.directa(Q[0], 0.0, 0.0, 0.0)
HORIZONTAL = K.directa(Q[0], 90.0, 0.0, 0.0)

PASO_Z = 0.003        # alto de cada franja del espacio de trabajo
PASO_BARRIDO = 1.0    # grados con que se recorren las ventanas
Z_REGLA = 0.295       # la regla del radio, arriba de todo
R_REGLA = -0.052      # la regla de la altura, a la izquierda de la base


def dz_texto(dz):
    """El aporte en altura, en mm y con signo, sin el cero negativo."""
    v = dz*1000
    return "0" if abs(v) < 0.5 else f"{v:+.0f}"


def corridas(puntos, paso=PASO_Z, paso_r=0.0015, cierre=6):
    """Parte una nube de puntos (r, z) en franjas horizontales llenas.

    Dibujar el espacio de trabajo punto por punto son cientos de miles de
    objetos. Agrupado por fila queda en unas pocas centenas de rectangulos, se
    ve como una region maciza y ademas el hueco que abre la guarda de la caja
    aparece solo, como una fila partida en dos.

    `cierre` tapa los huecos de hasta esa cantidad de celdas: el barrido de
    angulos deja agujeros de uno o dos milimetros que son del muestreo y no de
    la geometria. El hueco real, el de la guarda, mide mas de cien milimetros,
    asi que no corre riesgo de taparse.
    """
    filas = {}
    for r, z in puntos:
        filas.setdefault(int(round(z/paso)), set()).add(int(round(r/paso_r)))
    tramos = []
    for iz, cols in sorted(filas.items()):
        cs = sorted(cols)
        ini = prev = cs[0]
        for c in cs[1:]:
            if c > prev + cierre:
                tramos.append((iz*paso, ini*paso_r, prev*paso_r))
                ini = c
            prev = c
        tramos.append((iz*paso, ini*paso_r, prev*paso_r))
    return tramos


class Directa(BrazoEscena):

    def construct(self):
        self.correr((
            ("escenario", self.escenario),
            ("ejes", self.beat_1_ejes),
            ("convencion", self.beat_2_convencion),
            ("suma", self.beat_3_suma),
            ("control", self.beat_4_control),
            ("alfa", self.beat_5_alfa),
            ("base", self.beat_6_base),
            ("juntas", self.beat_7_juntas),
            ("espacio", self.beat_8_espacio),
            ("cierre", self.beat_9_cierre)))

    # ------------------------------------------------------- utilidades
    def normal(self, q1=None):
        """La normal del plano del brazo: la direccion de los tres ejes."""
        a = math.radians(Q[0] if q1 is None else q1)
        return np.array([-math.sin(a), math.cos(a), 0.0])

    def franjas(self, puntos, color, opac=0.30):
        """El espacio de trabajo dibujado como franjas en el plano del brazo."""
        g = VGroup()
        for z, r0, r1 in corridas(puntos):
            ancho = max(r1 - r0, 0.0012)
            rect = Rectangle(width=ancho*SC, height=PASO_Z*SC,
                             stroke_width=0, fill_opacity=opac, fill_color=color)
            self.de_pie(rect, Q[0] - 90)
            g.add(rect.move_to(Pp((r0 + r1)/2, z, Q[0])))
        return g

    def lectura(self, lineas, punto, escala=0.45):
        """Un bloque de texto monoespaciado, de pie en el plano del brazo.

        Va parado en el espacio y no fijo al cuadro: un objeto fijo al cuadro se
        registra por su familia de glifos al agregarlo, asi que no se puede
        redibujar cuadro a cuadro sin perder glifos.
        """
        g = VGroup(*[Text(l, font="DejaVu Sans Mono", font_size=24,
                          color=C_BRAZO) for l in lineas])
        g.arrange(DOWN, aligned_edge=LEFT, buff=0.18).scale(escala)
        return self.de_pie(g, Q[0] - 90).move_to(punto)

    def arco_en_plano(self, centro, desde, hasta, radio, color, ancho=4):
        """Un arco entre dos angulos absolutos, dentro del plano del brazo.

        Los angulos se miden desde la vertical, que es la convencion del brazo,
        y el arco se dibuja sobre el plano que giro la base.
        """
        q1 = math.radians(Q[0])
        er = np.array([math.cos(q1), math.sin(q1), 0.0])   # el eje r del plano
        return ParametricFunction(
            lambda t: centro + radio*SC*(math.sin(t)*er + math.cos(t)*OUT),
            t_range=[math.radians(desde), math.radians(hasta)],
            color=color, stroke_width=ancho)

    # ------------------------------------------- 1. los ejes de las juntas
    def beat_1_ejes(self):
        """Tres ejes paralelos y uno perpendicular: de ahi sale todo lo demas."""
        pts = [Pp(r, z, Q[0]) for r, z in POSE['pts']]
        self.brazo = self.brazo_de(POSE, C_BRAZO)
        self.play(Create(self.brazo), run_time=1.6)
        self.mostrar((r"\text{cuatro ejes: base, hombro, codo, mu\~{n}eca}",
                      "cuatro ejes: base, hombro, codo, muñeca"))
        self.wait(3)

        n = self.normal()
        largo = 0.105
        eje_base = DashedLine(P(0, 0, 0.02), P(0, 0, 0.40), color=C_E1,
                              stroke_width=6, dash_length=0.14)
        ejes_par = VGroup(*[
            DashedLine(p - largo*SC*n, p + largo*SC*n, color=C_E2,
                       stroke_width=6, dash_length=0.12)
            for p in pts[:3]])
        self.play(Create(eje_base), run_time=1.0)
        self.play(Create(ejes_par), run_time=1.4)
        self.mostrar(
            (r"\text{tres ejes \emph{paralelos}: hombro, codo, mu\~{n}eca}",
             "tres ejes paralelos: hombro, codo, muñeca"),
            (r"\text{un eje \emph{perpendicular}: la base}",
             "un eje perpendicular: la base"))
        self.wait(5)

        self.plano = Polygon(
            Pp(-0.03, 0, Q[0]), Pp(0.33, 0, Q[0]),
            Pp(0.33, 0.45, Q[0]), Pp(-0.03, 0.45, Q[0]),
            fill_opacity=0.08, fill_color=C_PLANO, stroke_color=C_PLANO,
            stroke_width=2)
        self.play(FadeIn(self.plano), run_time=1.1)
        self.mostrar(
            (r"\text{los tres eslabones se mueven en un mismo plano}",
             "los tres eslabones se mueven en un mismo plano"),
            (r"\text{la cadena se parte: brazo plano} + \text{rotacion}",
             "la cadena se parte: brazo plano + rotación"))
        self.wait(5)
        self.play(FadeOut(eje_base), FadeOut(ejes_par),
                  FadeOut(self.ejes), run_time=0.9)

    # --------------------------------------------- 2. la convencion
    def beat_2_convencion(self):
        """Cual angulo se mide desde donde. El cuaderno lo tenia contradictorio."""
        pts = [Pp(r, z, Q[0]) for r, z in POSE['pts']]
        self.move_camera(phi=88*DEGREES, theta=(Q[0] - 90)*DEGREES, zoom=2.1,
                         frame_center=self.encuadre_plano(Q[0], POSE['pts']),
                         run_time=2.4)
        self.mostrar(
            (r"q_2 \text{ desde la vertical}", "q₂ desde la vertical"),
            (r"q_3 \text{ y } q_4 \text{ desde el eslabon anterior}",
             "q₃ y q₄ desde el eslabón anterior"))
        self.wait(3)

        # cada referencia es la prolongacion del eslabon anterior; la del hombro
        # es la vertical, que es el eslabon cero
        refs, arcos, rots = VGroup(), VGroup(), VGroup()
        previo = 0.0
        for i, (paso, color, nombre) in enumerate(zip(
                POSE['pasos'], (C_E1, C_E2, C_E3), ("q_2", "q_3", "q_4"))):
            origen = pts[i]
            d = unit(np.array([math.sin(math.radians(previo))*math.cos(
                math.radians(Q[0])),
                math.sin(math.radians(previo))*math.sin(math.radians(Q[0])),
                math.cos(math.radians(previo))]))
            refs.add(DashedLine(origen, origen + 0.11*SC*d, color=C_GRIS,
                                stroke_width=3, dash_length=0.08))
            arcos.add(self.arco_en_plano(origen, previo, paso['ang'], 0.052,
                                         color))
            medio = (previo + paso['ang'])/2
            pm = origen + 0.075*SC*np.array(
                [math.sin(math.radians(medio))*math.cos(math.radians(Q[0])),
                 math.sin(math.radians(medio))*math.sin(math.radians(Q[0])),
                 math.cos(math.radians(medio))])
            rots.add(self.rotulo(rf"{nombre}={POSE['q'][i+1]:.1f}^\circ", pm,
                                 color, 0.44,
                                 plano=f"q{i+2} = {POSE['q'][i+1]:.1f}°"))
            previo = paso['ang']
        for k in range(3):
            self.play(Create(refs[k]), run_time=0.5)
            self.play(Create(arcos[k]), FadeIn(rots[k]), run_time=0.9)
            self.wait(1.6)
        self.mostrar(
            (r"\text{si los tres fueran absolutos, } q_4=90^\circ"
             r"\text{ bastaria para enderezar}",
             "si los tres fueran absolutos, q₄ = 90° bastaría para enderezar"),
            (r"\text{la mu\~{n}eca tiene } 270^\circ"
             r"\text{ porque compensa } 60^\circ+120^\circ",
             "la muñeca tiene 270° porque compensa 60° + 120°"))
        self.wait(5)
        self.refs, self.arcos, self.rots = refs, arcos, rots

    # -------------------------------------- 3. la suma de los eslabones
    def beat_3_suma(self):
        """r y z salen de sumar los tres eslabones como vectores."""
        self.play(FadeOut(self.refs), FadeOut(self.arcos), FadeOut(self.rots),
                  FadeOut(self.brazo), run_time=0.8)
        self.mostrar(
            (r"\alpha_2=q_2 \qquad \alpha_{23}=q_2+q_3 \qquad"
             r"\alpha_{234}=q_2+q_3+q_4",
             "α₂ = q₂     α₂₃ = q₂+q₃     α₂₃₄ = q₂+q₃+q₄"),
            (rf"{POSE['angs'][0]:.1f}^\circ \qquad {POSE['angs'][1]:.1f}^\circ"
             rf" \qquad {POSE['angs'][2]:.1f}^\circ",
             f"{POSE['angs'][0]:.1f}°        {POSE['angs'][1]:.1f}°"
             f"        {POSE['angs'][2]:.1f}°"))
        self.wait(4)

        # Dos reglas, una por coordenada. Cada eslabon proyecta sus dos puntas
        # sobre las dos, y como el radio y la altura se acumulan, las tres
        # proyecciones quedan pegadas una atras de la otra y llenan el total
        # exacto: eso es la suma de vectores, dibujada.
        er = unit(Pp(1, 0, Q[0]) - Pp(0, 0, Q[0]))      # el eje r en el mundo
        regla_r = Line(Pp(0, Z_REGLA, Q[0]), Pp(POSE['r'], Z_REGLA, Q[0]),
                       color=C_GRIS, stroke_width=2, stroke_opacity=0.45)
        regla_z = Line(Pp(R_REGLA, K.H_HOMBRO, Q[0]),
                       Pp(R_REGLA, POSE['z'], Q[0]),
                       color=C_GRIS, stroke_width=2, stroke_opacity=0.45)
        self.play(Create(regla_r), Create(regla_z), run_time=0.9)

        colores = (C_E1, C_E2, C_E3)
        tramos, proy, piezas, etiq = (VGroup() for _ in range(4))
        for paso, color in zip(POSE['pasos'], colores):
            (r0, z0), (r1, z1) = paso['desde'], paso['hasta']
            a, b = Pp(r0, z0, Q[0]), Pp(r1, z1, Q[0])
            tramos.add(self.tubo(a, b, color))
            sub = VGroup()
            for r, z in ((r0, z0), (r1, z1)):
                sub.add(DashedLine(Pp(r, z, Q[0]), Pp(r, Z_REGLA, Q[0]),
                                   color=color, stroke_width=2, dash_length=0.08,
                                   stroke_opacity=0.5))
                sub.add(DashedLine(Pp(r, z, Q[0]), Pp(R_REGLA, z, Q[0]),
                                   color=color, stroke_width=2, dash_length=0.08,
                                   stroke_opacity=0.5))
            proy.add(sub)
            piezas.add(VGroup(
                Line(Pp(r0, Z_REGLA, Q[0]), Pp(r1, Z_REGLA, Q[0]),
                     color=color, stroke_width=9),
                # el tercer eslabon tiene cos(90) = 0: su altura es un tic, no
                # un tramo, y asi se ve que no aporta nada a z
                Line(Pp(R_REGLA, z0, Q[0]), Pp(R_REGLA, z1, Q[0]),
                     color=color, stroke_width=9)
                if abs(z1 - z0) > 0.002 else
                Line(Pp(R_REGLA - 0.012, z0, Q[0]), Pp(R_REGLA + 0.012, z0, Q[0]),
                     color=color, stroke_width=5)))
            etiq.add(VGroup(
                self.rotulo(rf"{paso['dr']*1000:.0f}",
                            Pp((r0 + r1)/2, Z_REGLA + 0.022, Q[0]), color, 0.44,
                            plano=f"{paso['dr']*1000:.0f}"),
                self.rotulo(dz_texto(paso['dz']),
                            Pp(R_REGLA - 0.028, (z0 + z1)/2, Q[0]), color, 0.44,
                            plano=dz_texto(paso['dz']))))

        formulas = (
            (r"r=L_1\,\mathrm{sen}\,\alpha_2", "r = L₁·sen α₂"),
            (r"r=L_1\,\mathrm{sen}\,\alpha_2+L_2\,\mathrm{sen}\,\alpha_{23}",
             "r = L₁·sen α₂ + L₂·sen α₂₃"),
            (r"r=L_1\,\mathrm{sen}\,\alpha_2+L_2\,\mathrm{sen}\,\alpha_{23}"
             r"+L_3\,\mathrm{sen}\,\alpha_{234}",
             "r = L₁·sen α₂ + L₂·sen α₂₃ + L₃·sen α₂₃₄"))
        for k in range(3):
            self.play(Create(tramos[k]), run_time=0.9)
            self.play(Create(proy[k]), run_time=0.7)
            self.play(Create(piezas[k]), FadeIn(etiq[k]), run_time=0.8)
            self.mostrar(formulas[k])
            self.wait(2.2)
            self.play(FadeOut(proy[k]), run_time=0.4)
        totales = VGroup(
            self.rotulo(rf"r={POSE['r']*1000:.0f}",
                        Pp(POSE['r'] + 0.045, Z_REGLA, Q[0]), C_BRAZO, 0.5,
                        plano=f"r = {POSE['r']*1000:.0f}"),
            self.rotulo(rf"z={POSE['z']*1000:.0f}",
                        Pp(R_REGLA, POSE['z'] - 0.035, Q[0]), C_BRAZO, 0.5,
                        plano=f"z = {POSE['z']*1000:.0f}"))
        self.play(FadeIn(totales), run_time=0.8)
        self.wait(1.5)
        self.mostrar(
            (r"r=L_1\,\mathrm{sen}\,\alpha_2+L_2\,\mathrm{sen}\,\alpha_{23}"
             r"+L_3\,\mathrm{sen}\,\alpha_{234}"
             rf"={POSE['r']*1000:.0f}\ \mathrm{{mm}}",
             f"r = L₁·sen α₂ + L₂·sen α₂₃ + L₃·sen α₂₃₄ = {POSE['r']*1000:.0f} mm"),
            (r"z=h_{hombro}+L_1\cos\alpha_2+L_2\cos\alpha_{23}"
             r"+L_3\cos\alpha_{234}"
             rf"={POSE['z']*1000:.0f}\ \mathrm{{mm}}",
             f"z = h + L₁·cos α₂ + L₂·cos α₂₃ + L₃·cos α₂₃₄ "
             f"= {POSE['z']*1000:.0f} mm"),
            (r"\text{no es una aproximacion: es la suma exacta}",
             "no es una aproximación: es la suma exacta"))
        self.wait(5)
        self.play(FadeOut(piezas), FadeOut(etiq), FadeOut(totales),
                  FadeOut(regla_r), FadeOut(regla_z), run_time=0.8)
        self.tramos = tramos

    # ------------------------------------------ 4. los casos de control
    def beat_4_control(self):
        """Los dos extremos donde la respuesta se sabe de memoria."""
        self.play(FadeOut(self.tramos), run_time=0.5)
        self.move_camera(phi=88*DEGREES, theta=(Q[0] - 90)*DEGREES, zoom=1.45,
                         frame_center=Pp(0.12, 0.26, Q[0]), run_time=2.0)
        vert = self.brazo_de(VERTICAL, C_OK)
        cota = DashedLine(P(0, 0, 0), Pp(0, VERTICAL['z'], Q[0]), color=C_OK,
                          stroke_width=2.5, dash_length=0.1)
        tv = self.rotulo(rf"{VERTICAL['z']*1000:.0f}\ \mathrm{{mm}}",
                         Pp(-0.055, VERTICAL['z']/2, Q[0]), C_OK, 0.5,
                         plano=f"{VERTICAL['z']*1000:.0f} mm")
        self.play(Create(vert), run_time=1.2)
        self.play(Create(cota), FadeIn(tv), run_time=0.9)
        self.mostrar(
            (r"q_2=q_3=q_4=0 \;\Rightarrow\; \text{brazo vertical}",
             "q₂ = q₃ = q₄ = 0  ⇒  brazo vertical"),
            (rf"z=h_{{hombro}}+L_1+L_2+L_3={VERTICAL['z']*1000:.0f}"
             rf"\ \mathrm{{mm}}",
             f"z = h + L₁ + L₂ + L₃ = {VERTICAL['z']*1000:.0f} mm"))
        self.wait(4.5)

        hor = self.brazo_de(HORIZONTAL, C_MUN)
        cota2 = DashedLine(Pp(0, HORIZONTAL['z'], Q[0]),
                           Pp(HORIZONTAL['r'], HORIZONTAL['z'], Q[0]),
                           color=C_MUN, stroke_width=2.5, dash_length=0.1)
        th = self.rotulo(rf"{HORIZONTAL['r']*1000:.0f}\ \mathrm{{mm}}",
                         Pp(HORIZONTAL['r']/2, HORIZONTAL['z'] + 0.03, Q[0]),
                         C_MUN, 0.5, plano=f"{HORIZONTAL['r']*1000:.0f} mm")
        self.play(FadeOut(vert), FadeOut(cota), FadeOut(tv), run_time=0.6)
        self.play(Create(hor), run_time=1.2)
        self.play(Create(cota2), FadeIn(th), run_time=0.9)
        self.mostrar(
            (r"q_2=90^\circ,\; q_3=q_4=0 \;\Rightarrow\;"
             r"\text{brazo estirado horizontal}",
             "q₂ = 90°, q₃ = q₄ = 0  ⇒  brazo estirado horizontal"),
            (rf"r=L_1+L_2+L_3={HORIZONTAL['r']*1000:.0f}\ \mathrm{{mm}}"
             rf"\text{{ a la altura del hombro}}",
             f"r = L₁ + L₂ + L₃ = {HORIZONTAL['r']*1000:.0f} mm "
             f"a la altura del hombro"))
        self.wait(4)
        self.mostrar(
            (r"\text{ninguna de las dos es alcanzable: el hombro arranca en }"
             r"50^\circ",
             "ninguna de las dos es alcanzable: el hombro arranca en 50°"),
            (r"\text{son el control de que la formula da lo que tiene que dar}",
             "son el control de que la fórmula da lo que tiene que dar"))
        self.wait(4)
        self.play(FadeOut(hor), FadeOut(cota2), FadeOut(th), run_time=0.8)

    # --------------------------------------------------- 5. alfa
    def beat_5_alfa(self):
        """La suma de los tres angulos es la inclinacion de la garra."""
        self.move_camera(phi=88*DEGREES, theta=(Q[0] - 90)*DEGREES, zoom=2.0,
                         frame_center=self.encuadre_plano(Q[0], POSE['pts']),
                         run_time=2.0)
        t = ValueTracker(Q[1])

        def pose_de():
            q2 = t.get_value()
            q3 = Q[2] + (q2 - Q[1])*-0.8      # el codo acompaña al hombro
            return K.directa(Q[0], q2, q3, ALFA - q2 - q3)

        def dibujo():
            p = pose_de()
            g = self.brazo_de(p, C_OK, liviano=True)
            for pt in p['pts'][1:]:
                g.add(Sphere(center=Pp(*pt, Q[0]), radius=0.012*SC,
                             resolution=(6, 6), fill_opacity=1.0,
                             fill_color=C_BRAZO, checkerboard_colors=False,
                             stroke_width=0))
            # el vaso colgado de la punta, siempre derecho
            punta = Pp(p['r'], p['z'], Q[0])
            g.add(circulo(punta, RIGHT, UP, K.VASO_D/2*SC, C_E1, 3))
            g.add(Line(punta - K.VASO_D/2*SC*RIGHT,
                       punta - K.VASO_D/2*SC*RIGHT - K.VASO_H*SC*OUT,
                       color=C_E1, stroke_width=3))
            g.add(Line(punta + K.VASO_D/2*SC*RIGHT,
                       punta + K.VASO_D/2*SC*RIGHT - K.VASO_H*SC*OUT,
                       color=C_E1, stroke_width=3))
            g.add(circulo(punta - K.VASO_H*SC*OUT, RIGHT, UP,
                          K.VASO_D/2*SC, C_E1, 3))
            return g

        def texto():
            p = pose_de()
            return self.lectura(
                [f"q2 = {p['q'][1]:6.1f}°",
                 f"q3 = {p['q'][2]:6.1f}°",
                 f"q4 = {p['q'][3]:6.1f}°",
                 f"alfa = {p['alfa']:6.1f}°"], Pp(0.43, 0.30, Q[0]))

        brazo = always_redraw(dibujo)
        lect = always_redraw(texto)
        self.play(FadeIn(brazo), FadeIn(lect), run_time=1.2)
        self.mostrar(
            (r"\alpha=q_2+q_3+q_4 \text{ es la inclinacion de la garra}",
             "α = q₂ + q₃ + q₄ es la inclinación de la garra"),
            (r"q_4=90^\circ-q_2-q_3 \;\Rightarrow\; \alpha=90^\circ"
             r"\text{: el vaso queda derecho}",
             "q₄ = 90° − q₂ − q₃  ⇒  α = 90°: el vaso queda derecho"))
        self.wait(2.5)
        self.play(t.animate.set_value(K.VENTANAS['hombro'][1]), run_time=3.0)
        self.play(t.animate.set_value(K.VENTANAS['hombro'][0]), run_time=3.5)
        self.play(t.animate.set_value(Q[1]), run_time=2.5)
        self.wait(2)
        brazo.clear_updaters()
        lect.clear_updaters()
        self.play(FadeOut(brazo), FadeOut(lect), run_time=0.8)

    # ------------------------------------------------------- 6. la base
    def beat_6_base(self):
        """Lo que queda es rotar el plano: (r, z) -> (x, y, z)."""
        self.brazo = self.brazo_de(POSE, C_BRAZO)
        self.play(FadeIn(self.brazo), run_time=0.8)
        self.move_camera(phi=10*DEGREES, theta=-90*DEGREES, zoom=1.7,
                         frame_center=P(0.12, 0.09, 0), run_time=2.4)
        self.play(FadeIn(self.ejes[:3]), FadeIn(self.ejes[3:5]), run_time=0.8)
        radio = Line(P(0, 0, 0), P(POSE['x'], POSE['y'], 0), color=C_MUN,
                     stroke_width=5)
        proy = DashedLine(Pp(POSE['r'], POSE['z'], Q[0]),
                          P(POSE['x'], POSE['y'], 0), color=C_OBJ,
                          stroke_width=2.5, dash_length=0.1)
        arco = circulo(P(0, 0, 0), RIGHT, UP, 0.95, C_MUN, 4, 0,
                       math.radians(Q[0]))
        rot = self.rotulo(rf"q_1={Q[0]:.1f}^\circ",
                          P(0, 0, 0) + 1.3*np.array(
                              [math.cos(math.radians(Q[0]/2)),
                               math.sin(math.radians(Q[0]/2)), 0]), C_MUN, 0.5,
                          plano=f"q₁ = {Q[0]:.1f}°")
        self.play(Create(radio), Create(proy), run_time=1.0)
        self.play(Create(arco), FadeIn(rot), run_time=1.0)
        self.mostrar(
            (rf"x=r\cos q_1={POSE['x']*1000:.0f}\ \mathrm{{mm}}",
             f"x = r·cos q₁ = {POSE['x']*1000:.0f} mm"),
            (rf"y=r\,\mathrm{{sen}}\,q_1={POSE['y']*1000:.0f}\ \mathrm{{mm}}",
             f"y = r·sen q₁ = {POSE['y']*1000:.0f} mm"))
        self.wait(4.5)
        self.play(FadeOut(radio), FadeOut(proy), FadeOut(arco), FadeOut(rot),
                  FadeOut(self.ejes), run_time=0.8)

    # ------------------------------------------ 7. que mueve cada servo
    def beat_7_juntas(self):
        """Un eje por vez, dentro de su ventana, y la punta dibujando su arco."""
        self.play(FadeOut(self.brazo), run_time=0.5)
        self.move_camera(phi=88*DEGREES, theta=(Q[0] - 90)*DEGREES, zoom=1.7,
                         frame_center=Pp(0.13, 0.22, Q[0]), run_time=2.2)
        for k, (eje, nombre, color) in enumerate(
                zip(('hombro', 'codo', 'muneca'),
                    ('el hombro', 'el codo', 'la mu\\~{n}eca'),
                    (C_E1, C_E2, C_E3))):
            lo, hi = K.VENTANAS[eje]
            t = ValueTracker(Q[k + 1])

            def pose_de(k=k, t=t):
                q = list(Q)
                q[k + 1] = t.get_value()
                return K.directa(*q)

            def dibujo(k=k, t=t, color=color):
                p = pose_de(k, t)
                g = self.brazo_de(p, color, liviano=True)
                for pt in p['pts'][1:]:
                    g.add(Sphere(center=Pp(*pt, Q[0]), radius=0.012*SC,
                                 resolution=(6, 6), fill_opacity=1.0,
                                 fill_color=C_BRAZO,
                                 checkerboard_colors=False, stroke_width=0))
                return g

            def texto(k=k, t=t):
                p = pose_de(k, t)
                return self.lectura(
                    [f"q{k+2} = {p['q'][k+1]:6.1f}°",
                     f"r  = {p['r']*1000:5.0f} mm",
                     f"z  = {p['z']*1000:5.0f} mm"], Pp(0.40, 0.33, Q[0]))

            # el rastro es el lugar geometrico de la punta con ese eje solo
            rastro = ParametricFunction(
                lambda s, k=k: Pp(*K.directa(*[Q[0]] + [
                    (lo + s*(hi - lo)) if j == k else Q[j + 1]
                    for j in range(3)])['pts'][3], Q[0]),
                t_range=[0, 1, 0.02], color=color, stroke_width=3,
                stroke_opacity=0.55)
            brazo = always_redraw(dibujo)
            lect = always_redraw(texto)
            self.play(FadeIn(brazo), FadeIn(lect), Create(rastro), run_time=1.0)
            self.mostrar(
                (rf"\text{{solo {nombre}}}:\;{lo:.0f}^\circ\le q_{{{k+2}}}"
                 rf"\le {hi:.0f}^\circ",
                 f"solo {nombre.replace(chr(92) + '~{n}', 'ñ')}:  "
                 f"{lo:.0f}° ≤ q{k+2} ≤ {hi:.0f}°"))
            self.play(t.animate.set_value(hi), run_time=1.8)
            self.play(t.animate.set_value(lo), run_time=2.6)
            self.play(t.animate.set_value(Q[k + 1]), run_time=1.6)
            brazo.clear_updaters()
            lect.clear_updaters()
            self.play(FadeOut(brazo), FadeOut(lect), FadeOut(rastro),
                      run_time=0.6)

    # ------------------------------------------- 8. el espacio de trabajo
    def beat_8_espacio(self):
        """Hasta donde llega la punta con los recorridos que hay, y que cuesta la caja."""
        libres, vetados = K.espacio(PASO_BARRIDO)
        todo = self.franjas(libres + vetados, C_GRIS, 0.22)
        solo = self.franjas(libres, C_PLANO, 0.32)
        self.play(FadeIn(todo), run_time=1.6)
        self.mostrar(
            (r"\text{todas las poses con los tres ejes dentro de su ventana}",
             "todas las poses con los tres ejes dentro de su ventana"),
            (rf"\text{{hombro }}50^\circ\!-\!110^\circ,\;"
             rf"\text{{codo }}0^\circ\!-\!120^\circ,\;"
             rf"\text{{mu\~{{n}}eca}}\;{-108}^\circ\!-\!{40}^\circ",
             "hombro 50°–110°, codo 0°–120°, muñeca −108°–40°"))
        self.wait(4)

        cja = caja(K.CAJA_W, K.CAJA_D, K.CAJA_H, C_MAL)
        self.play(FadeIn(cja), run_time=0.9)
        self.play(FadeOut(todo), FadeIn(solo), run_time=1.6)
        self.mostrar(
            (r"\text{la guarda saca las poses que meten el brazo en la caja}",
             "la guarda saca las poses que meten el brazo en la caja"),
            (rf"\text{{ningun punto con }} z<{K.CAJA_H*1000:.0f}"
             rf"\ \mathrm{{mm}}\text{{ puede tener }} r<{K.R_GUARDA*1000:.0f}"
             rf"\ \mathrm{{mm}}",
             f"ningún punto con z < {K.CAJA_H*1000:.0f} mm puede tener "
             f"r < {K.R_GUARDA*1000:.0f} mm"))
        self.wait(5)
        self.play(FadeOut(cja), run_time=0.6)

        self.move_camera(phi=68*DEGREES, theta=-58*DEGREES, zoom=1.15,
                         frame_center=P(0.05, 0.03, 0.20), run_time=2.4)
        # el plano sale antes de girar: con la figura barriendo los 360 grados,
        # el plano de una sola pose ya no dice nada y tapa media vuelta
        self.play(FadeOut(self.plano), run_time=0.6)
        self.mostrar(
            (r"\text{y la base barre esa figura alrededor de la vertical}",
             "y la base barre esa figura alrededor de la vertical"))
        self.play(Rotating(solo, axis=OUT, about_point=P(0, 0, 0),
                           angle=TAU, run_time=7.0, rate_func=linear))
        self.wait(1.5)
        self.play(FadeOut(solo), run_time=1.0)

    # ------------------------------------------------------- 9. el cierre
    def beat_9_cierre(self):
        """La misma pose con la que cierra E4."""
        self.move_camera(phi=72*DEGREES, theta=-58*DEGREES, zoom=1.4,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.0)
        brazo = self.brazo_de(POSE, C_OK)
        vaso = self.copa(OBJ)
        punta = self.marca(Pp(POSE['r'], POSE['z'], Q[0]), C_OBJ, 0.015)
        self.play(FadeIn(vaso), Create(brazo), FadeIn(punta), run_time=1.6)
        self.mostrar(
            (rf"q_1={Q[0]:.1f}^\circ\quad q_2={Q[1]:.1f}^\circ\quad "
             rf"q_3={Q[2]:.1f}^\circ\quad q_4={Q[3]:.1f}^\circ",
             f"q₁ = {Q[0]:.1f}°   q₂ = {Q[1]:.1f}°   "
             f"q₃ = {Q[2]:.1f}°   q₄ = {Q[3]:.1f}°"),
            (rf"\longrightarrow\;({POSE['x']*1000:.0f},\;"
             rf"{POSE['y']*1000:.0f},\;{POSE['z']*1000:.0f})\ \mathrm{{mm}}"
             rf"\quad \alpha={POSE['alfa']:.0f}^\circ",
             f"→  ({POSE['x']*1000:.0f}, {POSE['y']*1000:.0f}, "
             f"{POSE['z']*1000:.0f}) mm    α = {POSE['alfa']:.0f}°"))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait(2)
