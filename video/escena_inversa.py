"""E4 - Cinematica inversa: de un punto del espacio a los cuatro angulos.

Pensada como fondo de una presentacion hablada: casi no hay texto, hay
matematica. Cada estado clave queda quieto varios segundos para que haya tiempo
de explicarlo en vivo.

El escenario, la paleta, los dos estilos de dibujo y las piezas sueltas salen de
`escena_base.py`; las cotas y los angulos, de `brazo_anim.py`. Aca solo estan
los diez tramos de este video.

    manim -ql escena_inversa.py Inversa                  # 480p15 alambre
    manim -qh --fps 30 escena_inversa.py Inversa         # 1080p30 solido
    manim -qk --fps 60 escena_inversa.py Inversa         # 2160p60 solido

El README del directorio tiene los tiempos de render y las variables de entorno.
"""
import math

import numpy as np
from manim import *

import brazo_anim as K
from escena_base import *   # noqa: F401,F403

# la banda util y el limite de alcance se miden, no se escriben: salen de la
# misma cinematica, asi que el video no puede contradecir al cuaderno
R_DESDE, R_HASTA = K.banda(Z_OBJ, ALFA)
MARGEN_LEJOS = 0.030                 # cuanto mas afuera del brazo estirado se
                                     # pide el punto imposible: con 30 mm el
                                     # hueco entre las dos esferas ya se ve
R_LEJOS = K.limite_alcance(Z_OBJ, ALFA) + MARGEN_LEJOS


class Inversa(BrazoEscena):

    def construct(self):
        self.c = K.construir(*OBJ, ALFA)
        self.correr((
            ("escenario", self.escenario),
            ("planteo", self.beat_1_planteo),
            ("base", self.beat_2_base),
            ("muñeca", self.beat_3_muneca),
            ("esferas", self.beat_4_esferas),
            ("plano", self.beat_5_plano),
            ("triangulo", self.beat_6_triangulo),
            ("ramas", self.beat_7_ramas),
            ("barrido", self.beat_8_barrido),
            ("rechazo", self.beat_9_rechazo),
            ("cierre", self.beat_10_cierre)))

    # ------------------------------------------------------- 1. el planteo
    def beat_1_planteo(self):
        vaso = self.copa(OBJ)
        self.objetivo = self.marca(P(*OBJ), C_OBJ, 0.015)
        self.play(FadeIn(vaso), run_time=1.1)
        self.play(FadeIn(self.objetivo, scale=1.8), run_time=0.8)
        self.mostrar(
            (r"(x,\,y,\,z,\,\alpha)\ \longrightarrow\ (q_1,\,q_2,\,q_3,\,q_4)",
             "(x, y, z, α)  →  (q₁, q₂, q₃, q₄)"),
            (rf"({OBJ[0]*1000:.0f},\ {OBJ[1]*1000:.0f},\ {OBJ[2]*1000:.0f})"
             rf"\ \mathrm{{mm}}\qquad \alpha={ALFA:.0f}^\circ",
             f"({OBJ[0]*1000:.0f}, {OBJ[1]*1000:.0f}, {OBJ[2]*1000:.0f}) mm"
             f"    α = {ALFA:.0f}°"))
        self.wait(4)
        self.vaso = vaso

    # ---------------------------------------------------------- 2. la base
    def beat_2_base(self):
        c = self.c
        self.move_camera(phi=6*DEGREES, theta=-90*DEGREES, zoom=1.7,
                         frame_center=P(0.12, 0.09, 0), run_time=2.2)
        radio = Line(P(0, 0, 0), P(OBJ[0], OBJ[1], 0), color=C_MUN, stroke_width=5)
        proy = DashedLine(P(*OBJ), P(OBJ[0], OBJ[1], 0), color=C_OBJ,
                          stroke_width=2.5, dash_length=0.1)
        arco = circulo(P(0, 0, 0), RIGHT, UP, 0.95, C_MUN, 4, 0, math.radians(c['q1']))
        rot = self.rotulo(rf"q_1={c['q1']:.1f}^\circ",
                          P(0, 0, 0) + 1.3*np.array(
                              [math.cos(math.radians(c['q1']/2)),
                               math.sin(math.radians(c['q1']/2)), 0]), C_MUN, 0.5,
                          plano=f"q₁ = {c['q1']:.1f}°")
        self.play(Create(proy), Create(radio), run_time=1.1)
        self.play(Create(arco), FadeIn(rot), run_time=1.1)
        self.mostrar(
            (r"q_1=\operatorname{atan2}(y,\,x)", "q₁ = atan2(y, x)"),
            (rf"r=\sqrt{{x^2+y^2}}={c['r']*1000:.0f}\ \mathrm{{mm}}",
             f"r = √(x² + y²) = {c['r']*1000:.0f} mm"))
        self.wait(4)

        # el plano llega justo hasta donde el brazo puede llegar; mas grande se
        # convierte en una pared verde que tapa el resto de la escena
        self.plano_brazo = Polygon(
            Pp(-0.03, 0, c['q1']), Pp(0.31, 0, c['q1']),
            Pp(0.31, 0.33, c['q1']), Pp(-0.03, 0.33, c['q1']),
            fill_opacity=0.08, fill_color=C_PLANO, stroke_color=C_PLANO,
            stroke_width=2)
        self.play(FadeIn(self.plano_brazo), run_time=1.1)
        self.move_camera(phi=72*DEGREES, theta=-58*DEGREES, zoom=1.45,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.2)
        self.mostrar(
            (r"\text{el brazo vive en un plano}", "el brazo vive en un plano"),
            (r"\text{tres ejes paralelos, dos coordenadas: } (r,\,z)",
             "tres ejes paralelos, dos coordenadas: (r, z)"))
        self.wait(4)
        # los ejes ya cumplieron: de aca en mas la referencia es la caja y el
        # plano, y las tres flechas solo tapaban
        self.play(FadeOut(arco), FadeOut(rot), FadeOut(proy), FadeOut(radio),
                  FadeOut(self.ejes), run_time=0.8)

    # ------------------------------------------- 3. desacople de la muñeca
    def beat_3_muneca(self):
        c = self.c
        pm = Pp(c['rm'], c['zm'], c['q1'])
        self.move_camera(phi=88*DEGREES, theta=(c['q1'] - 90)*DEGREES, zoom=2.4,
                         frame_center=self.encuadre_plano(
                             c['q1'], [(c['r'], c['z']), (c['rm'], c['zm'])]),
                         run_time=2.4)
        vec = self.flecha(P(*OBJ), pm, C_MUN, 5)
        self.muneca = self.marca(pm, C_MUN, 0.013)
        # el rotulo va perpendicular al eslabon y hacia afuera del plano verde,
        # que es de donde antes se superponia
        n = unit(np.cross(P(*OBJ) - pm, OUT))
        etiq = self.rotulo(r"L_3=85", (P(*OBJ) + pm)/2 + 0.42*n + 0.12*OUT,
                           C_MUN, 0.5, plano="L₃ = 85")
        self.play(Create(vec), run_time=1.0)
        self.play(FadeIn(self.muneca, scale=1.7), FadeIn(etiq), run_time=0.8)
        self.mostrar(
            (r"r_m=r-L_3\operatorname{sen}\alpha", "rm = r − L₃·sen α"),
            (r"z_m=z-L_3\cos\alpha", "zm = z − L₃·cos α"),
            (rf"r_m={c['rm']*1000:.0f}\ \mathrm{{mm}}\qquad "
             rf"z_m={c['zm']*1000:.0f}\ \mathrm{{mm}}",
             f"rm = {c['rm']*1000:.0f} mm    zm = {c['zm']*1000:.0f} mm"))
        self.wait(5)
        self.vec_l3, self.etiq_l3 = vec, etiq

    # ------------------------------------------------------ 4. las esferas
    def beat_4_esferas(self):
        c = self.c
        ph, pm = P(0, 0, K.H_HOMBRO), Pp(c['rm'], c['zm'], c['q1'])
        self.move_camera(phi=64*DEGREES, theta=-58*DEGREES, zoom=1.35,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.2)
        e1 = bola(ph, K.L1, C_E1)
        e2 = bola(pm, K.L2, C_E2)
        self.play(FadeIn(e1) if SOLIDO else Create(e1), run_time=1.4)
        self.mostrar((r"\|\,\mathrm{codo}-\mathrm{hombro}\,\|=L_1",
                      "‖codo − hombro‖ = L₁ = 120 mm"))
        self.wait(3)
        self.play(FadeIn(e2) if SOLIDO else Create(e2), run_time=1.4)
        self.mostrar((r"\|\,\mathrm{codo}-\mathrm{hombro}\,\|=L_1",
                      "‖codo − hombro‖ = L₁ = 120 mm"),
                     (r"\|\,\mathrm{codo}-\mathrm{mu\tilde{n}eca}\,\|=L_2",
                      "‖codo − muñeca‖ = L₂ = 120 mm"))
        self.wait(3)

        self.circulo_codos = self.interseccion(ph, pm, K.L1, K.L2)
        self.play(Create(self.circulo_codos), run_time=1.8)
        self.mostrar(
            (r"\text{dos esferas se cortan en una circunferencia}",
             "dos esferas se cortan en una circunferencia"),
            (r"\text{todas las posiciones posibles del codo}",
             "todas las posiciones posibles del codo"))
        self.wait(3)
        self.play(FadeOut(e1), FadeOut(e2), run_time=1.0)
        self.begin_ambient_camera_rotation(rate=0.16)
        self.wait(5)
        self.stop_ambient_camera_rotation()

    def interseccion(self, ph, pm, l1, l2, ancho=7):
        """La circunferencia donde se cortan las dos esferas. None si no se cortan."""
        d = np.linalg.norm(pm - ph)
        if d > (l1 + l2)*SC or d < 1e-9:
            return None
        eje = (pm - ph)/d
        a = (d**2 + (l1*SC)**2 - (l2*SC)**2)/(2*d)
        rad2 = (l1*SC)**2 - a**2
        if rad2 <= 0:
            return None
        u = unit(np.cross(eje, OUT))
        return circulo(ph + a*eje, u, np.cross(eje, u), math.sqrt(rad2),
                       C_OBJ, ancho)

    # ------------------------------ 5. el plano corta la circunferencia
    def beat_5_plano(self):
        c = self.c
        self.play(self.plano_brazo.animate.set_fill(opacity=0.22), run_time=1.0)
        self.codos = VGroup(*[
            self.marca(Pp(*b['pts'][1], c['q1']),
                       C_OK if b['sirve'] else C_MAL, 0.014)
            for b in c['ramas']])
        self.play(*[FadeIn(p, scale=1.8) for p in self.codos], run_time=1.2)
        self.mostrar(
            (r"\text{el plano del brazo corta la circunferencia}",
             "el plano del brazo corta la circunferencia"),
            (r"\text{en \emph{dos} puntos: las dos soluciones}",
             "en dos puntos: las dos soluciones"))
        self.move_camera(phi=80*DEGREES, theta=-22*DEGREES, zoom=1.5,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.6)
        self.wait(4)

    # ----------------------------------------------------- 6. el triangulo
    def beat_6_triangulo(self):
        c = self.c
        self.play(FadeOut(self.circulo_codos), run_time=0.8)
        ph, pm = P(0, 0, K.H_HOMBRO), Pp(c['rm'], c['zm'], c['q1'])
        self.move_camera(phi=88*DEGREES, theta=(c['q1'] - 90)*DEGREES, zoom=2.4,
                         frame_center=self.encuadre_plano(
                             c['q1'], c['elegida']['pts'] + [(c['rm'], c['zm'])]),
                         run_time=2.4)
        lado = Line(ph, pm, color=C_MUN, stroke_width=4)
        hacia = np.array([math.cos(math.radians(c['q1'])),
                          math.sin(math.radians(c['q1'])), 0.0])
        dtex = self.rotulo(rf"d={c['d']*1000:.0f}",
                           (ph + pm)/2 + 0.5*OUT - 0.3*hacia, C_MUN, 0.5,
                           plano=f"d = {c['d']*1000:.0f}")
        self.play(Create(lado), FadeIn(dtex), run_time=1.0)
        self.mostrar(
            (r"d=\sqrt{r_m^{2}+(z_m-Z_0)^{2}}", "d = √(rm² + (zm − Z₀)²)"),
            (rf"\mathrm{{semi}}=\arccos\frac{{d}}{{L_1+L_2}}"
             rf"={math.degrees(c['semi']):.1f}^\circ",
             f"semi = arccos(d / (L₁+L₂)) = {math.degrees(c['semi']):.1f}°"),
            (rf"\mathrm{{medio}}=\operatorname{{atan2}}(r_m,\,z_m-Z_0)"
             rf"={math.degrees(c['medio']):.1f}^\circ",
             f"medio = atan2(rm, zm − Z₀) = {math.degrees(c['medio']):.1f}°"))
        self.wait(5)
        elegida = c['elegida']
        pc = Pp(*elegida['pts'][1], c['q1'])
        self.triangulo = VGroup(Line(ph, pc, color=C_OK, stroke_width=6),
                                Line(pc, pm, color=C_OK, stroke_width=6))
        self.play(Create(self.triangulo), run_time=1.2)
        self.mostrar(
            (r"q_2=\mathrm{medio}\mp\mathrm{semi}", "q₂ = medio ∓ semi"),
            (r"q_3=\pm\,2\,\mathrm{semi}", "q₃ = ± 2·semi"),
            (r"q_4=\alpha-q_2-q_3", "q₄ = α − q₂ − q₃"))
        self.wait(5)
        self.lado_d, self.dtex = lado, dtex

    # --------------------------------------- 7. las dos ramas y el filtro
    def beat_7_ramas(self):
        c = self.c
        self.play(FadeOut(self.triangulo), run_time=0.6)
        self.move_camera(phi=80*DEGREES, theta=-50*DEGREES, zoom=1.5,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.2)
        abajo, arriba = c['ramas'][0], c['ramas'][1]
        g_ab = self.brazo_de(abajo, C_OK)
        g_ar = self.brazo_de(arriba, C_MAL, opac=0.8, liviano=True)
        self.play(Create(g_ab), Create(g_ar), run_time=1.6)
        self.mostrar(
            (rf"\text{{codo abajo}}:\ q_2={abajo['q'][1]:.1f}^\circ,\ "
             rf"q_3={abajo['q'][2]:.1f}^\circ,\ q_4={abajo['q'][3]:.1f}^\circ",
             f"codo abajo:  q₂ = {abajo['q'][1]:.1f}°   "
             f"q₃ = {abajo['q'][2]:.1f}°   q₄ = {abajo['q'][3]:.1f}°"),
            (rf"\text{{codo arriba}}:\ q_2={arriba['q'][1]:.1f}^\circ,\ "
             rf"q_3={arriba['q'][2]:.1f}^\circ,\ q_4={arriba['q'][3]:.1f}^\circ",
             f"codo arriba: q₂ = {arriba['q'][1]:.1f}°   "
             f"q₃ = {arriba['q'][2]:.1f}°   q₄ = {arriba['q'][3]:.1f}°"))
        self.wait(5)
        self.mostrar(
            (r"50^\circ\le q_2\le 110^\circ\qquad 0^\circ\le q_3\le 120^\circ",
             "50° ≤ q₂ ≤ 110°     0° ≤ q₃ ≤ 120°"),
            (rf"q_2={arriba['q'][1]:.1f}^\circ>110^\circ\ \Rightarrow\ "
             rf"\text{{la rama de codo arriba no existe}}",
             f"q₂ = {arriba['q'][1]:.1f}° > 110°  ⇒  "
             f"la rama de codo arriba no existe"))
        self.wait(4)
        self.play(FadeOut(g_ar), FadeOut(self.codos[1]),
                  FadeOut(self.lado_d), FadeOut(self.dtex), run_time=1.2)
        self.wait(1.5)
        self.brazo_final = g_ab

    # -------------------------------- 8. la inversa como funcion: barrido
    def beat_8_barrido(self):
        """Mover el objetivo y ver los cuatro angulos salir solos.

        Es el beat que justifica el trabajo: una sola rama sobrevive a las
        ventanas, asi que la inversa es una funcion y el firmware no tiene que
        elegir nada. Los numeros en vivo se dibujan con Text y no con MathTex:
        MathTex compila LaTeX por cada cadena distinta, y aca cambian sesenta
        veces por segundo.
        """
        c = self.c
        self.play(FadeOut(self.brazo_final), FadeOut(self.objetivo),
                  FadeOut(self.muneca), FadeOut(self.codos[0]),
                  FadeOut(self.vec_l3), FadeOut(self.etiq_l3),
                  FadeOut(self.vaso), run_time=1.0)
        self.move_camera(phi=86*DEGREES, theta=(c['q1'] - 90)*DEGREES, zoom=2.0,
                         frame_center=Pp(0.145, 0.175, c['q1']), run_time=2.2)
        self.mostrar(
            (r"\text{una sola rama sobrevive a las ventanas}",
             "una sola rama sobrevive a las ventanas"),
            (r"\Rightarrow\ \text{la inversa es una \emph{funcion}}",
             "⇒ la inversa es una función"))

        t = ValueTracker(R_DESDE)

        def estado():
            return K.construir(*K.plano(t.get_value(), Z_OBJ, Q1), ALFA)

        def dibujo():
            e = estado()['elegida']
            g = self.brazo_de(e, C_OK, liviano=True)
            # esferas chicas y de malla gruesa en vez de Dot: un Dot es un disco
            # en el plano xy y con la camara dentro del plano del brazo se veria
            # de canto. Una esfera se ve igual desde cualquier angulo y a
            # resolucion 6x6 cuesta poco aunque se redibuje en cada cuadro.
            for p, col, rad in [(e['pts'][1], C_BRAZO, 0.012),
                                (e['pts'][2], C_BRAZO, 0.012),
                                (e['pts'][3], C_OBJ, 0.014)]:
                g.add(Sphere(center=Pp(*p, Q1), radius=rad*SC, resolution=(6, 6),
                             fill_opacity=1.0, fill_color=col,
                             checkerboard_colors=False, stroke_width=0))
            return g

        # La lectura va parada en el espacio, no fija al cuadro. Un objeto fijo
        # al cuadro se registra por su familia de glifos en el momento de
        # agregarlo, asi que no se puede redibujar: ni `become` (que empareja
        # submobjetos y pierde un glifo cuando cambia la cantidad de digitos) ni
        # volver a registrarlo en cada cuadro sirven. Puesta en el mundo y
        # orientada a mano hacia la camara, `always_redraw` funciona sin trucos.
        pos = Pp(0.47, 0.27, Q1)

        def lectura():
            s = estado()
            e = s['elegida']
            g = VGroup(*[Text(l, font="DejaVu Sans Mono", font_size=24,
                              color=C_BRAZO)
                         for l in (f"r  = {s['r']*1000:5.0f} mm",
                                   f"q2 = {e['q'][1]:6.1f}°",
                                   f"q3 = {e['q'][2]:6.1f}°",
                                   f"q4 = {e['q'][3]:6.1f}°")])
            g.arrange(DOWN, aligned_edge=LEFT, buff=0.18).scale(0.45)
            return self.de_pie(g, Q1 - 90).move_to(pos)

        lect = always_redraw(lectura)
        brazo = always_redraw(dibujo)
        rastro = Line(Pp(R_DESDE, Z_OBJ, Q1), Pp(R_HASTA, Z_OBJ, Q1),
                      color=C_OBJ, stroke_width=2, stroke_opacity=0.45)
        self.play(FadeIn(brazo), FadeIn(lect), Create(rastro), run_time=1.2)
        self.wait(1.5)
        self.play(t.animate.set_value(R_HASTA), run_time=4.0, rate_func=smooth)
        self.wait(0.8)
        self.play(t.animate.set_value(R_DESDE), run_time=4.0, rate_func=smooth)
        self.wait(1.5)
        self.mostrar(
            (rf"{R_DESDE*1000:.0f}\ \mathrm{{mm}}\le r\le "
             rf"{R_HASTA*1000:.0f}\ \mathrm{{mm}}"
             rf"\quad\text{{(ancho }}{(R_HASTA-R_DESDE)*1000:.0f}"
             rf"\ \mathrm{{mm}})",
             f"{R_DESDE*1000:.0f} mm ≤ r ≤ {R_HASTA*1000:.0f} mm"
             f"   (ancho {(R_HASTA-R_DESDE)*1000:.0f} mm)"),
            (rf"\text{{afuera lo frenan las ventanas; adentro, la guarda de la caja}}",
             "afuera lo frenan las ventanas; adentro, la guarda de la caja"))
        self.wait(3)
        lect.clear_updaters()
        brazo.clear_updaters()
        self.play(FadeOut(brazo), FadeOut(lect), FadeOut(rastro), run_time=0.9)

    # ------------------------------------ 9. un punto fuera de alcance
    def beat_9_rechazo(self):
        """El limite del alcance se ve: las esferas dejan de tocarse."""
        c = self.c
        ph = P(0, 0, K.H_HOMBRO)
        lejos = K.plano(R_LEJOS, Z_OBJ, Q1)
        s = K.construir(*lejos, ALFA)
        pm = Pp(s['rm'], s['zm'], Q1)
        self.move_camera(phi=70*DEGREES, theta=-52*DEGREES, zoom=1.2,
                         frame_center=P(0.12, 0.08, 0.16), run_time=2.0)
        obj = self.marca(P(*lejos), C_MAL, 0.015)
        mun = self.marca(pm, C_MUN, 0.013)
        lado = DashedLine(ph, pm, color=C_MAL, stroke_width=3, dash_length=0.12)
        e1 = bola(ph, K.L1, C_E1, 0.13)
        e2 = bola(pm, K.L2, C_E2, 0.13)
        self.play(FadeIn(obj, scale=1.6), FadeIn(mun), Create(lado), run_time=1.1)
        self.play(FadeIn(e1) if SOLIDO else Create(e1),
                  FadeIn(e2) if SOLIDO else Create(e2), run_time=1.5)
        self.mostrar(
            (rf"d={s['d']*1000:.0f}\ \mathrm{{mm}}>L_1+L_2="
             rf"{(K.L1+K.L2)*1000:.0f}\ \mathrm{{mm}}",
             f"d = {s['d']*1000:.0f} mm > L₁ + L₂ = {(K.L1+K.L2)*1000:.0f} mm"),
            (r"\text{las esferas no se cortan: no hay codo posible}",
             "las esferas no se cortan: no hay codo posible"))
        self.wait(2)
        # proyectadas sobre el cuadro las dos esferas se pisan igual, asi que el
        # hueco se muestra sobre la recta: L1 desde el hombro, L2 desde la
        # muñeca, y lo que sobra en el medio es lo que falta de brazo
        eje = unit(pm - ph)
        hueco = s['d'] - K.L1 - K.L2
        tramo1 = Line(ph, ph + K.L1*SC*eje, color=C_E1, stroke_width=7)
        tramo2 = Line(pm, pm - K.L2*SC*eje, color=C_E2, stroke_width=7)
        falta = Line(ph + K.L1*SC*eje, pm - K.L2*SC*eje, color=C_MAL,
                     stroke_width=9)
        htex = self.rotulo(rf"{hueco*1000:.0f}\ \mathrm{{mm}}",
                           (ph + pm)/2 + 0.55*OUT, C_MAL, 0.5,
                           plano=f"{hueco*1000:.0f} mm")
        self.play(Create(tramo1), Create(tramo2), run_time=0.9)
        self.play(Create(falta), FadeIn(htex), run_time=0.8)
        self.wait(3.5)
        self.mostrar(
            (r"\text{sin solucion} \Rightarrow \text{se rechaza la orden}",
             "sin solución ⇒ se rechaza la orden"),
            (r"\text{el firmware no extrapola ni se acerca lo que puede}",
             "el firmware no extrapola ni se acerca lo que puede"))
        self.wait(4)
        self.play(FadeOut(VGroup(tramo1, tramo2, falta, htex)),
                  FadeOut(e1), FadeOut(e2), FadeOut(lado), FadeOut(obj),
                  FadeOut(mun), run_time=1.0)

    # ------------------------------------------------------- 10. el cierre
    def beat_10_cierre(self):
        c = self.c
        q = c['elegida']['q']
        self.move_camera(phi=72*DEGREES, theta=-58*DEGREES, zoom=1.4,
                         frame_center=P(0.10, 0.07, 0.17), run_time=2.0)
        brazo = self.brazo_de(c['elegida'], C_OK)
        obj = self.marca(P(*OBJ), C_OBJ, 0.015)
        self.play(FadeOut(self.plano_brazo), FadeIn(self.vaso),
                  Create(brazo), FadeIn(obj), run_time=1.6)
        self.mostrar(
            (rf"q_1={q[0]:.1f}^\circ\qquad q_2={q[1]:.1f}^\circ",
             f"q₁ = {q[0]:.1f}°     q₂ = {q[1]:.1f}°"),
            (rf"q_3={q[2]:.1f}^\circ\qquad q_4={q[3]:.1f}^\circ",
             f"q₃ = {q[2]:.1f}°     q₄ = {q[3]:.1f}°"))
        self.begin_ambient_camera_rotation(rate=0.12)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        self.wait(2)
