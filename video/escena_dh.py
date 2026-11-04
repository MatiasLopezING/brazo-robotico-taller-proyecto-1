"""E3 - Denavit-Hartenberg: los cinco sistemas y el producto de matrices.

Pensada como fondo de una presentacion hablada: casi no hay texto, hay
matematica. Cada estado clave queda quieto varios segundos para que haya tiempo
de explicarlo en vivo.

Sigue la seccion 3 del cuaderno `Cinematica_brazo.ipynb`. El papel de este video
no es derivar la cinematica —eso lo hace E2 por la via geometrica— sino mostrar
el metodo sistematico y usarlo como verificacion independiente: otra convencion
de ejes, otros angulos, otro producto de matrices, el mismo resultado.

El escenario, la paleta, los dos estilos de dibujo y las piezas sueltas salen de
`escena_base.py`; las cotas, los angulos y la tabla, de `brazo_anim.py`.

    manim -ql escena_dh.py DH                  # 480p15 alambre
    manim -qh --fps 30 escena_dh.py DH         # 1080p30 solido
    manim -qk --fps 60 escena_dh.py DH         # 2160p60 solido

El README del directorio tiene los tiempos de render y las variables de entorno.
"""
import math

import numpy as np
from manim import *

import brazo_anim as K
from escena_base import *   # noqa: F401,F403

POSE = K.directa(*Q)
TABLA = K.tabla_dh(*Q)
MARCOS = K.cadena_dh(*Q)

LARGO_EJE = 0.068      # largo de las flechas de cada triada, en metros
C_X, C_Y, C_Z = C_MAL, C_OK, C_E1


def malla_poses(n=3):
    """Unas pocas poses repartidas por las ventanas, siempre las mismas.

    La verificacion final recorre esta grilla en vez de sortear angulos: asi el
    numero que sale en pantalla es reproducible y el video se puede rehacer
    igual el mes que viene.
    """
    def tramo(eje):
        lo, hi = K.VENTANAS[eje]
        return [lo + i*(hi - lo)/(n - 1) for i in range(n)]

    poses = []
    for q1 in (-90.0, 0.0, 90.0):
        for q2 in tramo('hombro'):
            for q3 in tramo('codo'):
                for q4 in tramo('muneca'):
                    poses.append((q1, q2, q3, q4))
    return poses


class DH(BrazoEscena):

    def construct(self):
        self.correr((
            ("escenario", self.escenario),
            ("reglas", self.beat_1_reglas),
            ("parametros", self.beat_2_parametros),
            ("tabla", self.beat_3_tabla),
            ("producto", self.beat_4_producto),
            ("coincide", self.beat_5_coincide),
            ("cierre", self.beat_6_cierre)))

    # ------------------------------------------------------- utilidades
    def triada(self, T, nombre=None, largo=LARGO_EJE, rotulos=True):
        """Los tres ejes de un sistema, dibujados donde y como los pone DH.

        Las flechas van con linea y punta tambien en el estilo solido. Un eje
        de referencia es una abstraccion, no una pieza: no gana nada con malla,
        y hay quince en pantalla casi todo el video —doce mas por cuadro
        mientras el brazo se mueve—, que con malla a 1080p multiplicaba el
        tiempo de render por diez.
        """
        o = P(*K.origen(T))
        g = VGroup()
        for k, color, letra in ((0, C_X, "x"), (1, C_Y, "y"), (2, C_Z, "z")):
            punta = o + largo*SC*np.array(K.eje(T, k))
            g.add(Line(o, punta, color=color, stroke_width=4).add_tip(
                tip_length=0.14, tip_width=0.10))
            if rotulos and letra != "y" and nombre is not None:
                g.add(self.rotulo(rf"{letra}_{nombre}",
                                  o + largo*1.38*SC*np.array(K.eje(T, k)),
                                  color, 0.40, plano=f"{letra}{nombre}"))
        return g

    def celdas(self, T):
        """La matriz 4x4 como grilla de numeros, con la posicion en milimetros.

        Las tres primeras columnas son la orientacion y no tienen unidad; la
        cuarta es donde esta la punta. Van con el mismo ancho de campo para que
        la grilla quede alineada en monoespacio.
        """
        g = VGroup()
        for i in range(4):
            for j in range(4):
                v = T[i][j]
                txt = f"{v*1000:6.1f}" if j == 3 and i < 3 else f"{v:6.2f}"
                g.add(Text(txt, font="DejaVu Sans Mono", font_size=24,
                           color=C_OBJ if j == 3 and i < 3 else C_BRAZO))
        g.arrange_in_grid(rows=4, cols=4, buff=0.24).scale(0.60)
        return g

    # --------------------------------------- 1. donde van los sistemas
    def beat_1_reglas(self):
        """Las dos reglas que eligen los ejes, y las cinco triadas puestas."""
        self.brazo = self.brazo_de(POSE, C_BRAZO)
        self.play(Create(self.brazo), run_time=1.4)
        # de cerca: las triadas son el contenido del video y a la distancia del
        # escenario no se leen
        self.play(FadeOut(self.ejes), run_time=0.6)
        self.move_camera(phi=70*DEGREES, theta=-50*DEGREES, zoom=2.1,
                         frame_center=P(0.09, 0.06, 0.14), run_time=2.0)
        self.mostrar(
            (r"z_i \text{ sobre el eje de giro de la articulacion siguiente}",
             "z_i sobre el eje de giro de la articulación siguiente"),
            (r"x_i \text{ sobre la normal comun entre } z_{i-1} \text{ y } z_i",
             "x_i sobre la normal común entre z_{i−1} y z_i"))
        self.wait(5)

        self.marcos = VGroup(*[self.triada(T, str(i))
                               for i, T in enumerate(MARCOS)])
        nombres = ("en la base, sobre la mesa", "en el hombro", "en el codo",
                   "en la mu\\~{n}eca", "en la punta de los dedos")
        for i, (m, nom) in enumerate(zip(self.marcos, nombres)):
            self.play(FadeIn(m, scale=1.3), run_time=0.7)
            self.mostrar(
                (rf"\text{{sistema }}{i}\text{{: {nom}}}",
                 f"sistema {i}: {nom.replace(chr(92) + '~{n}', 'ñ')}"))
            self.wait(2.6)
        # los tres ejes paralelos de E2 tienen nombre aca: son z1, z2 y z3
        n = np.array(K.eje(MARCOS[1], 2))
        paralelos = VGroup(*[
            DashedLine(P(*K.origen(T)) - 0.1*SC*n, P(*K.origen(T)) + 0.1*SC*n,
                       color=C_E2, stroke_width=4, dash_length=0.1,
                       stroke_opacity=0.7)
            for T in MARCOS[1:4]])
        self.play(Create(paralelos), run_time=1.3)
        self.mostrar(
            (r"z_1,\,z_2,\,z_3\text{ son los tres ejes paralelos de E2}",
             "z₁, z₂, z₃ son los tres ejes paralelos de E2"),
            (r"z_0\text{ es el perpendicular: el de la base}",
             "z₀ es el perpendicular: el de la base"))
        self.wait(5)
        self.play(FadeOut(paralelos), run_time=0.7)
        self.mostrar(
            (r"\text{cinco sistemas, cuatro pasos entre ellos}",
             "cinco sistemas, cuatro pasos entre ellos"),
            (r"\text{cada paso se describe con cuatro numeros}",
             "cada paso se describe con cuatro números"))
        self.wait(5)

    # ------------------------------------- 2. los cuatro parametros
    def beat_2_parametros(self):
        """El paso del sistema 0 al 1, hecho en sus cuatro movimientos.

        Se anima la primera fila porque es la unica con los cuatro parametros
        interesantes: gira, sube, no se corre, y tuerce noventa grados.
        """
        self.play(FadeOut(self.marcos[1:]), run_time=0.6)
        self.move_camera(phi=74*DEGREES, theta=-38*DEGREES, zoom=2.9,
                         frame_center=P(0.01, 0.01, 0.105), run_time=2.2)
        self.mostrar(
            (r"A_i=\mathrm{Rot}_z(\theta_i)\;T_z(d_i)\;T_x(a_i)\;"
             r"\mathrm{Rot}_x(\alpha_i)",
             "A_i = Rot_z(θ_i) · T_z(d_i) · T_x(a_i) · Rot_x(α_i)"))
        self.wait(4)

        movil = self.triada(MARCOS[0], None, rotulos=False)
        self.play(FadeIn(movil, scale=1.2), run_time=0.7)
        _, theta, d, a, alfa = TABLA[0]

        arco = circulo(P(0, 0, 0), RIGHT, UP, 0.62, C_MUN, 4, 0,
                       math.radians(theta))
        self.mostrar(
            (rf"\theta_1=q_1={theta:.1f}^\circ \quad"
             rf"\text{{giro sobre }} z_0",
             f"θ₁ = q₁ = {theta:.1f}°    giro sobre z₀"))
        self.play(Create(arco),
                  Rotate(movil, angle=math.radians(theta), axis=OUT,
                         about_point=P(0, 0, 0)), run_time=1.8)
        self.wait(3.6)

        cota = DashedLine(P(0, 0, 0), P(0, 0, d), color=C_MUN,
                          stroke_width=3, dash_length=0.1)
        tcota = self.rotulo(rf"d_1={d*1000:.0f}", P(0.045, 0.045, d/2), C_MUN,
                            0.46, plano=f"d₁ = {d*1000:.0f}")
        self.mostrar(
            (rf"d_1={d*1000:.0f}\ \mathrm{{mm}} \quad"
             rf"\text{{traslacion sobre }} z_0",
             f"d₁ = {d*1000:.0f} mm    traslación sobre z₀"))
        self.play(Create(cota), FadeIn(tcota),
                  movil.animate.shift(P(0, 0, d)), run_time=1.8)
        self.wait(3.6)

        self.mostrar(
            (rf"a_1={a*1000:.0f} \quad"
             r"\text{los ejes de base y hombro se cortan: no hay corrimiento}",
             f"a₁ = {a*1000:.0f}    los ejes de base y hombro se cortan: "
             f"no hay corrimiento"))
        self.wait(4.5)

        ex = np.array(K.eje(MARCOS[1], 0))
        self.mostrar(
            (rf"\alpha_1={alfa:.0f}^\circ \quad"
             r"\text{giro sobre } x_1\text{: la unica torsion del brazo}",
             f"α₁ = {alfa:.0f}°    giro sobre x₁: la única torsión del brazo"),
            (r"\text{es lo que vuelve horizontal al eje del hombro}",
             "es lo que vuelve horizontal al eje del hombro"))
        self.play(Rotate(movil, angle=math.radians(alfa), axis=ex,
                         about_point=P(0, 0, d)), run_time=2.2)
        self.wait(5.0)
        self.play(FadeIn(self.marcos[1]), FadeOut(movil), FadeOut(arco),
                  FadeOut(cota), FadeOut(tcota), run_time=1.0)
        self.play(FadeIn(self.marcos[2:]), run_time=0.8)

    # ---------------------------------------------------- 3. la tabla
    def beat_3_tabla(self):
        """Las cuatro filas, y lo que queda de cada una."""
        self.move_camera(phi=68*DEGREES, theta=-46*DEGREES, zoom=1.5,
                         frame_center=P(0.17, 0.13, 0.16), run_time=2.0)
        # la tabla es informacion, no geometria: va pegada al cuadro, donde se
        # lee derecha, y no parada en el espacio
        cab = ("i", "junta", "θ", "d", "a", "α")
        filas = [[str(i + 1), nom, f"{t:.1f}", f"{d*1000:.0f}",
                  f"{a*1000:.0f}", f"{al:.0f}"]
                 for i, (nom, t, d, a, al) in enumerate(TABLA)]
        celdas = VGroup()
        for c in cab:
            celdas.add(Text(c, font="DejaVu Sans Mono", font_size=26,
                            color=C_GRIS))
        colores = (C_MUN, C_E1, C_E2, C_E3)
        for f, color in zip(filas, colores):
            for c in f:
                celdas.add(Text(c, font="DejaVu Sans Mono", font_size=26,
                                color=color))
        celdas.arrange_in_grid(rows=5, cols=6, buff=0.28).scale(0.64)
        self.fijo_al_cuadro(celdas, buff=0.8)
        self.play(FadeIn(celdas[:6]), run_time=0.7)
        for k in range(4):
            self.play(FadeIn(celdas[6*(k + 1):6*(k + 2)]), run_time=0.6)
            self.wait(1.6)
        self.mostrar(
            (r"\text{un parametro por fila es la variable: siempre }\theta"
             r"\text{, porque las cuatro juntas son de giro}",
             "un parámetro por fila es la variable: siempre θ, "
             "porque las cuatro juntas son de giro"),
            (r"\text{los otros tres se miden sobre la pieza y no cambian}",
             "los otros tres se miden sobre la pieza y no cambian"))
        self.wait(5)
        self.mostrar(
            (rf"\theta_2=q_2-90^\circ={TABLA[1][1]:.1f}^\circ",
             f"θ₂ = q₂ − 90° = {TABLA[1][1]:.1f}°"),
            (r"\text{el cero de DH no es el cero mecanico: }x_1"
             r"\text{ quedo sobre la normal comun,}",
             "el cero de DH no es el cero mecánico: x₁ quedó sobre "
             "la normal común,"),
            (r"\text{noventa grados corrido de la vertical desde la que se "
             r"mide } q_2",
             "noventa grados corrido de la vertical desde la que se mide q₂"))
        self.wait(6)
        self.mostrar(
            (r"\text{las tres ultimas filas tienen } d=0 \text{ y } \alpha=0",
             "las tres últimas filas tienen d = 0 y α = 0"),
            (r"\text{lo unico que queda de cada una es el largo del eslabon}",
             "lo único que queda de cada una es el largo del eslabón"),
            (r"\Rightarrow\ \text{esas tres filas \emph{son} el brazo plano}",
             "⇒ esas tres filas son el brazo plano"))
        self.wait(5)
        self.tabla = celdas

    # ------------------------------------------- 4. el producto
    def beat_4_producto(self):
        """T = A1 A2 A3 A4, con los numeros moviendose junto con el brazo."""
        self.play(FadeOut(self.tabla), FadeOut(self.marcos), run_time=0.8)
        self.mostrar(
            (r"T=A_1A_2A_3A_4",
             "T = A₁ · A₂ · A₃ · A₄"),
            (r"\text{ultima columna: donde esta la punta}",
             "última columna: dónde está la punta"),
            (r"3\times 3\text{ de arriba: como esta orientada la pinza}",
             "3×3 de arriba: cómo está orientada la pinza"))

        t = ValueTracker(Q[1])

        def pose_de():
            q2 = t.get_value()
            q3 = Q[2] + (q2 - Q[1])*-0.8
            return [Q[0], q2, q3, ALFA - q2 - q3]

        def dibujo():
            q = pose_de()
            g = self.brazo_de(K.directa(*q), C_OK, liviano=True)
            for T in K.cadena_dh(*q)[1:]:
                g.add(self.triada(T, None, 0.042, rotulos=False))
            return g

        def numeros():
            m = self.celdas(K.cadena_dh(*pose_de())[4])
            return self.de_pie(m, Q[0] - 62).move_to(Pp(0.44, 0.30, Q[0]))

        brazo = always_redraw(dibujo)
        tabla = always_redraw(numeros)
        # el brazo nuevo y la matriz entran durante el viaje de camara: si no,
        # quedan dos segundos de pantalla vacia entre un tramo y el otro
        self.move_camera(phi=84*DEGREES, theta=(Q[0] - 62)*DEGREES, zoom=1.75,
                         frame_center=Pp(0.17, 0.19, Q[0]), run_time=2.2,
                         added_anims=[FadeOut(self.brazo), FadeIn(brazo),
                                      FadeIn(tabla)])
        self.wait(4.5)
        self.play(t.animate.set_value(K.VENTANAS['hombro'][1]), run_time=3.0)
        self.wait(2.0)
        self.play(t.animate.set_value(K.VENTANAS['hombro'][0]), run_time=3.8)
        self.wait(2.0)
        self.play(t.animate.set_value(Q[1]), run_time=2.6)
        self.wait(3.5)
        brazo.clear_updaters()
        tabla.clear_updaters()
        self.play(FadeOut(brazo), FadeOut(tabla), run_time=0.8)

    # ------------------------------------------- 5. por que coincide
    def beat_5_coincide(self):
        """El acuerdo con E2 no es casualidad: es la misma cuenta simplificada."""
        self.brazo = self.brazo_de(POSE, C_BRAZO)
        self.marcos = VGroup(*[self.triada(T, str(i))
                               for i, T in enumerate(MARCOS)])
        # el brazo entra durante el viaje de camara: si no, quedan dos segundos
        # de pantalla vacia entre un tramo y el otro
        self.play(FadeIn(self.brazo), FadeIn(self.marcos), run_time=1.2)
        self.move_camera(phi=70*DEGREES, theta=-48*DEGREES, zoom=1.9,
                         frame_center=P(0.10, 0.07, 0.14), run_time=2.2)
        self.mostrar(
            (r"A_2A_3A_4:\ \text{giros sobre el mismo eje} \Rightarrow"
             r"\text{ los angulos se suman}",
             "A₂A₃A₄: giros sobre el mismo eje ⇒ los ángulos se suman"),
            (r"a_2\,u(\theta_2)+a_3\,u(\theta_2{+}\theta_3)"
             r"+a_4\,u(\theta_2{+}\theta_3{+}\theta_4)",
             "a₂·u(θ₂) + a₃·u(θ₂+θ₃) + a₄·u(θ₂+θ₃+θ₄)"),
            (r"\text{palabra por palabra, la formula geometrica de E2}",
             "palabra por palabra, la fórmula geométrica de E2"))
        self.wait(8)

        poses = malla_poses()
        peor = max(max(K.desvio_dh(*q)) for q in poses)
        exp = math.floor(math.log10(peor*1000))
        man = peor*1000/10**exp
        self.mostrar(
            (rf"\text{{peor desvio sobre {len(poses)} poses, en los cinco "
             rf"sistemas: }}{man:.0f}\cdot 10^{{{exp}}}\ \mathrm{{mm}}",
             f"peor desvío sobre {len(poses)} poses, en los cinco sistemas: "
             f"{man:.0f}·10^{exp} mm"),
            (r"\text{no solo la punta: tambien el codo y la mu\~{n}eca}",
             "no solo la punta: también el codo y la muñeca"),
            (r"\text{que son los que mira la guarda contra la caja}",
             "que son los que mira la guarda contra la caja"))
        self.wait(7)

    # ------------------------------------------------------- 6. cierre
    def beat_6_cierre(self):
        """La misma pose con la que cierran E2 y E4."""
        self.move_camera(phi=72*DEGREES, theta=-58*DEGREES, zoom=1.4,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.0)
        vaso = self.copa(OBJ)
        self.play(FadeIn(vaso), run_time=0.9)
        self.mostrar(
            (r"\text{el mismo brazo, por otro camino}",
             "el mismo brazo, por otro camino"),
            (rf"({POSE['x']*1000:.0f},\;{POSE['y']*1000:.0f},\;"
             rf"{POSE['z']*1000:.0f})\ \mathrm{{mm}}\quad"
             rf"\alpha={POSE['alfa']:.0f}^\circ",
             f"({POSE['x']*1000:.0f}, {POSE['y']*1000:.0f}, "
             f"{POSE['z']*1000:.0f}) mm    α = {POSE['alfa']:.0f}°"))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait(2)
