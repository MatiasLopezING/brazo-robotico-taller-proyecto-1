# Animaciones de la cinemática

Animaciones hechas con [Manim Community](https://www.manim.community/) para
proyectar atrás mientras se expone. No llevan voz ni texto explicativo: cada
estado clave queda quieto varios segundos para dar tiempo a explicarlo en vivo.

| archivo | qué es |
| --- | --- |
| `brazo_anim.py` | la cinemática del brazo, copia fiel de `brazo_control/cinematica.py` |
| `escena_base.py` | el escenario, la paleta, los dos estilos y las piezas sueltas |
| `escena_directa.py` | E2, la cinemática directa, en nueve tramos |
| `escena_dh.py` | E3, Denavit-Hartenberg, en seis tramos |
| `escena_inversa.py` | E4, la cinemática inversa, en diez tramos |

Los tres videos usan la misma pose de ejemplo —la que resuelve la inversa para
el punto donde la tarea toma el vaso, definida en `escena_base.py`— así que
cierran en el mismo brazo y en los mismos cuatro ángulos. El orden para verlos
es E2, E3, E4: la vía geométrica, su verificación por matrices, y el problema
inverso.

Los videos no están en el repositorio: se generan, pesan decenas de megabytes y
quedan bajo `media/`, que está ignorada.

## Qué muestra E2

| tramo | arranca en | qué se ve |
| --- | --- | --- |
| escenario | 0:00 | la caja, el pedestal, el hombro y los ejes de la base |
| ejes | 0:06 | los cuatro ejes: tres paralelos y uno perpendicular, de donde sale que la cadena es plana |
| convención | 0:27 | `q₂` desde la vertical, `q₃` y `q₄` desde el eslabón anterior, y por qué la muñeca necesita 270° |
| suma | 0:48 | los tres eslabones proyectados sobre dos reglas: las proyecciones se apilan y llenan `r` y `z` |
| control | 1:21 | todo a cero da 515 mm de altura; estirado horizontal da 325 mm de radio |
| alfa | 1:44 | `α = q₂+q₃+q₄` es la inclinación de la garra, y `q₄ = 90° − q₂ − q₃` mantiene el vaso derecho |
| base | 2:02 | la rotación que faltaba: `x = r·cos q₁`, `y = r·sen q₁` |
| juntas | 2:14 | un eje por vez dentro de su ventana, con la punta dibujando su arco |
| espacio | 2:42 | todo lo que alcanza la punta, lo que le saca la guarda de la caja, y el barrido de la base |
| cierre | 3:10 | la pose resuelta, la misma con la que cierra E4 |

Duración total 3:22.

## Qué muestra E3

Este video no deriva la cinemática: eso lo hace E2 por la vía geométrica. Acá el
papel de Denavit-Hartenberg es el que le da la sección 3 del cuaderno —método
sistemático y verificación independiente—, así que cierra comparándose con E2.

| tramo | arranca en | qué se ve |
| --- | --- | --- |
| escenario | 0:00 | la caja, el pedestal, el hombro y los ejes de la base |
| reglas | 0:06 | las dos reglas que eligen los ejes, los cinco sistemas puestos uno por uno, y que `z₁, z₂, z₃` son los tres ejes paralelos de E2 |
| parámetros | 0:49 | el paso del sistema 0 al 1 hecho en sus cuatro movimientos: gira `θ₁`, sube `d₁`, no se corre (`a₁ = 0`), y tuerce `α₁ = −90°` |
| tabla | 1:25 | las cuatro filas una por una, el offset `θ₂ = q₂ − 90°`, y que las tres filas con `d = 0` y `α = 0` son el brazo plano |
| producto | 1:54 | `T = A₁A₂A₃A₄` con los dieciséis números moviéndose junto con el brazo |
| coincide | 2:20 | por qué el acuerdo con E2 no es casualidad, y el peor desvío sobre 81 poses en los cinco sistemas |
| cierre | 2:40 | la misma pose con la que cierran E2 y E4 |

Duración total 2:51.

## Qué muestra E4

| tramo | arranca en | qué se ve |
| --- | --- | --- |
| escenario | 0:00 | la caja, el pedestal, el hombro y los ejes de la base |
| planteo | 0:06 | el vaso, el punto objetivo y el problema: de `(x, y, z, α)` a los cuatro ángulos |
| base | 0:13 | `q₁ = atan2(y, x)`, el radio `r` y el plano donde vive el brazo |
| muñeca | 0:31 | el desacople: restar `L₃` para pasar de la punta a la muñeca |
| esferas | 0:41 | las dos restricciones de distancia como esferas y su circunferencia de intersección |
| plano | 1:05 | el plano del brazo corta esa circunferencia en dos puntos: las dos ramas |
| triángulo | 1:14 | el triángulo isósceles, `semi`, `medio` y las fórmulas de `q₂`, `q₃`, `q₄` |
| ramas | 1:31 | las dos ramas dibujadas y la ventana del codo descartando la de codo arriba |
| barrido | 1:49 | el objetivo recorre la banda útil y los cuatro ángulos salen solos: la inversa es una función |
| rechazo | 2:10 | un punto fuera de alcance: las esferas no se cortan, el hueco de 26 mm sobre la recta, la orden se rechaza |
| cierre | 2:29 | la pose resuelta, con los cuatro ángulos |

Duración total 2:41. Los tiempos los imprime el propio render con
`BRAZO_TIEMPOS=1`, así que no se desactualizan si se cambia un tramo.

## Cómo renderizar

Hace falta Python 3.9 o más, `pip install manim` y
[ffmpeg](https://www.gyan.dev/ffmpeg/builds/) en el `PATH`. LaTeX es opcional:
si no está instalado, las fórmulas se dibujan con texto unicode en vez de
MathTex, que queda algo menos prolijo pero corre igual.

    manim -ql escena_inversa.py Inversa             # 480p15, para revisar
    manim -qh --fps 30 escena_inversa.py Inversa    # 1080p30
    manim -qk --fps 60 escena_inversa.py Inversa    # 2160p60

    manim -qh --fps 30 escena_directa.py Directa    # lo mismo para E2
    manim -qh --fps 30 escena_dh.py DH              # y para E3

El resultado queda en `media/videos/<archivo>/<resolucion>/<Escena>.mp4`.

### Los dos estilos de dibujo

Hay un solo guion y dos maneras de dibujarlo:

- **alambre**: líneas, circunferencias y polígonos ubicados en el espacio. Se
  lee como un diagrama y renderiza dos órdenes de magnitud más rápido.
- **sólido**: esferas, cilindros y prismas de verdad, con las dos esferas de la
  intersección translúcidas.

El estilo lo elige la calidad del render: `-ql` usa alambre, `-qh` y `-qk` usan
sólido. Se puede forzar con `BRAZO_ESTILO`.

### Cuánto tarda

El render es por CPU y de un solo hilo, así que depende casi solo del
procesador. Las dos primeras filas están medidas en una máquina de referencia y
las otras dos son la extrapolación por cantidad de píxeles y de cuadros:

| calidad | estilo | E2 | E3 | E4 |
| --- | --- | --- | --- | --- |
| 480p15 | alambre | 2 min (medido) | 1,5 min (medido) | 1,5 min (medido) |
| 480p15 | sólido | 4,5 min (medido) | 2,5 min (medido) | 6,5 min (medido) |
| 1080p30 | sólido | 10 min (medido) | 6,5 min (medido) | 17 min (medido) |
| 1080p60 | sólido | ~20 min | ~13 min | ~35 min |
| 2160p60 | sólido | ~1,5 h | ~1 h | ~3 h |

Una máquina de escritorio común tarda entre una y tres veces más que esa
referencia, así que 2160p60 es un render de una noche y 1080p60 entra en una
pausa para almorzar.

### Rendear los tres de una

Cada render de manim usa un solo núcleo, así que en una máquina de cuatro o más
conviene lanzarlos en paralelo: los tres juntos tardan lo que el más largo —E4—
en vez de la suma. Cada uno necesita **su propio `--media_dir`**, porque la
caché de LaTeX es compartida y si no los procesos se pisan:

    manim -qk --fps 60 --media_dir media/E2 escena_directa.py Directa
    manim -qk --fps 60 --media_dir media/E3 escena_dh.py DH
    manim -qk --fps 60 --media_dir media/E4 escena_inversa.py Inversa

Antes de lanzarlos conviene **compilar una fórmula cualquiera una sola vez**. Si
hay LaTeX instalado las escenas lo usan, y MiKTeX instala al vuelo los paquetes
que le faltan con un instalador que admite una sola instancia: tres renders
arrancando juntos se pisan y dos mueren en la primera fórmula. Alcanza con
correr una escena corta en `-ql` antes, o directamente evitarlo con
`BRAZO_LATEX=0`, que dibuja las fórmulas con texto unicode y queda casi igual.

Las tres juntas rinden muy distinto porque lo que cuesta es la malla de las
superficies, no la duración. En E4 las dos esferas translúcidas se llevan más de
la mitad del render; E2 no tiene esferas grandes; y E3 dibuja sus quince ejes de
referencia con línea y punta en vez de malla, que es lo que lo vuelve el más
barato de los tres. `BRAZO_MALLA` baja la malla de las esferas sin tocar la
resolución del video, y es la perilla que conviene mover si el render se hace
largo:

    BRAZO_MALLA=16 manim -qk --fps 60 escena_inversa.py Inversa

Otras opciones útiles mientras se ajusta una escena:

    BRAZO_TIEMPOS=1 manim -ql escena_inversa.py Inversa   # imprime los tiempos de cada tramo
    manim -ql -n 40,60 escena_inversa.py Inversa          # solo un rango de animaciones
    manim -ql -s escena_inversa.py Inversa                # solo el último cuadro

## De dónde salen los números

Ningún número de los videos está escrito a mano. Las cotas y las ventanas salen
de `brazo_anim.py`, que es copia de `brazo_control/cinematica.py`, que a su vez
sale de `brazo_parametros.py`. Los ángulos de cada pose los calcula la misma
inversa que corre en el nodo de ROS 2; la banda útil, el límite de alcance y el
espacio de trabajo se miden recorriendo los ángulos en vez de declararse; y los
dos casos de control de E2 son los del cuaderno, recalculados en el render.

`verifica_parametros.py` incluye a `brazo_anim.py` entre los archivos que
compara contra `brazo_parametros.py`, así que si mañana cambia una ventana el
script dice que el video quedó atrasado.
