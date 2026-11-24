# Correcciones del 2.º informe de avance — devolución de Malena

Grupo N.º 3 — brazo robótico teleoperado. Archivo corregido: `brazo.kicad_pcb`
(con las reglas nuevas en `brazo.kicad_pro`).

Versiones anteriores, por si hace falta volver:

| archivo | qué es |
|---|---|
| `brazo_antes_de_la_correccion.kicad_pcb` | lo que se entregó |
| `brazo_v2_aislamiento_0.2.kicad_pcb` | primera corrección: capas invertidas y cortos sacados, pero con 0,2 mm de aislamiento |
| `brazo_v2_reglas_viejas.kicad_pro` | las reglas viejas del proyecto (aislamiento 0,0, pista 0,2) |

## La norma

No teníamos las restricciones de diseño de la cátedra, así que se tomaron las del
proyecto aprobado que se usó de referencia (`kicad-v2`), que es de la misma
materia y usa el mismo proceso de fabricación:

| | antes | ahora (= proyecto aprobado) |
|---|---|---|
| aislamiento mínimo | 0,0 mm (el DRC no controlaba nada) | **0,7 mm** |
| pista de señal | 0,7 mm | **1,0 mm** |
| pista de potencia (+5 V y entrada al fusible) | 0,7 mm | **1,7 mm** |
| cobre al borde | 0,5 mm | 0,5 mm |
| vía | 1,5 / 0,7 mm | 1,5 / 0,7 mm |

Las reglas quedaron cargadas en el proyecto: clase `Default` con 1,0 / 0,7, y
clase `Potencia` con 1,7 mm para `+5V` y para la entrada al fusible.

## Las tres observaciones

### 1. «Las conexiones sobre la capa top deberían estar en la bottom y viceversa»

Todo el ruteo está en **B.Cu** (cara de abajo, la que se ataca). En **F.Cu** sólo
hay puentes de alambre: tramos rectos que van de un agujero a otro.

### 2. «Algunas pistas están muy juntas — pueden sacar pines que no usen»

La causa era concreta: el ruteo se había hecho con pistas de 0,2 mm y después se
las ensanchó a 0,7 mm. Los tramos paralelos habían quedado separados 0,40 y
0,65 mm y con el ensanche se pisaban: **20 cortocircuitos entre pistas** y 38
islas invadidas.

Se sacaron las 65 islas de P1 y P2 que el diseño no usa, y la placa se **ruteó
de nuevo entera** con la norma de arriba. Todas las parejas de cobre de redes
distintas quedan a 0,7 mm o más, incluidas las islas vecinas de una misma tira.

### 3. «Los pads de los pines de la placa deberían ser ovalados»

Las islas de P1 eran de 2,0 × 1,7 mm (proporción 1,18: en KiCad se ven casi
redondas) y las de P2 de 2,2 × 1,7. Ahora son todas de **2,6 × 1,7 mm**, y se
alargan hacia el lado donde se quitaron los pines: el cobre está corrido 0,3 mm
respecto del agujero (el `offset` del pad en KiCad). Así quedan bien ovaladas,
tienen más cobre para soldar y no le roban lugar al ruteo. P1-1 y P1-2, que están
una al lado de la otra, se alargan en vertical.

De paso, **F1** (portafusible) tiene perforación de **1,0 mm**: con islas de
1,7 mm de ancho el anillo de cobre quedaba en 0,35 mm, demasiado fino. Ahora es
de 2,6 × 1,8 mm, con un anillo de 0,40 mm.

## Puentes de alambre

| red | largo | por qué |
|---|---|---|
| PWM_HOMBRO | 61,2 mm | Los tres PWM que van de los servos a P1 llegan en orden cruzado, así que uno tiene que cruzar. Es el único cruce de señal que obliga la ubicación de los componentes. |
| GND | 4,0 mm | une pedazos del plano de masa |
| GND | 4,8 mm | ídem |
| GND | 4,0 mm | ídem |
| GND | 4,0 mm | ídem |

Los cuatro de masa existen porque en una placa de una cara cada pista es una
pared para el relleno: con 0,7 mm de aislamiento, una pista de 1,0 mm se lleva
una franja de 2,4 mm, y las que corren junto al borde lo cierran. El relleno queda
partido, y cada puente corto une un pedazo con el resto por encima de una pista.

Para comparar: el archivo entregado tenía **5 puentes, de 19 a 60 mm**.

## Otras cosas que estaban mal y se corrigieron

- El relleno de cobre estaba en la red **+3,3 V** en vez de GND. Se había dado
  vuelta al fusionar GND y +3,3 V en el esquemático.
- La masa llegaba al pad de entrada de +5 V de la bornera, y faltaban la entrada
  de +5 V y la derivación de +3,3 V a la bornera nueva. Todo venía del cambio de
  bornera de 2 a 3 vías.
- PWM_MUÑECA no llegaba a P2-31, y JOY_B_Y terminaba 25,4 mm antes de P1-15.
  Ya venían cortadas del archivo original.
- Serigrafía: las referencias de H1 y H2 caían sobre el borde, y la de C1 se
  pisaba con J1.

## Verificación

Se hizo con geometría exacta, con las islas como cápsulas y el desplazamiento
del cobre aplicado:

- aislamiento ≥ 0,7 mm entre todo par de cobres de redes distintas, por capa
- cobre al borde ≥ 0,51 mm
- anillo de cobre ≥ 0,40 mm en todas las islas y vías
- agujero contra agujero ≥ 1,00 mm
- las 14 redes completas
- simulación del relleno: un solo grupo de masa, y cada pad de masa con al
  menos 2 radios térmicos (`min_resolved_spokes = 2`)

## Al abrir en KiCad

1. Abrir `brazo.kicad_pcb`.
2. **B** para rellenar las zonas.
3. Inspeccionar → Control de reglas de diseño → Ejecutar DRC.

**Esperable:** 0 errores, y advertencias `lib_footprint_mismatch` en las huellas
modificadas. Esas advertencias **tienen que quedar**, porque son la prueba de
que las huellas se tocaron a propósito. Si KiCad ofrece "actualizar huellas desde
la biblioteca", **no**: devolvería las 65 islas quitadas y las islas casi
redondas.

## Para el aula virtual con Malena

1. ¿Las restricciones del apunte son las mismas que las del proyecto aprobado
   (0,7 / 1,0 / 1,7)?
2. Al sacar pines de P1 y P2 también se sacaron sus agujeros. ¿El conector de
   2×20 se recorta, o prefiere que los agujeros queden sin cobre (NPTH) para que
   el conector entre entero?
3. ¿Los cuatro puentes cortos de masa están bien, o prefiere otra solución para
   el plano (por ejemplo, un anillo de masa en el perímetro)?
