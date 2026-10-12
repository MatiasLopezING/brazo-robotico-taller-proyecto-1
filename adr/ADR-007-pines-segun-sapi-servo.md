# ADR-007: Asignar los pines de los servomotores al mapa nativo de `sapi_servo`

- **Estado**: Aceptada
- **Fecha**: 2026-10-03
- **Autores**: Ariana Ariza (02879/6), Lautaro Lopes (02978/9)

## Contexto

El requerimiento 3.3.2 obliga a desarrollar el firmware en C sobre el proyecto Firmware v3 con la
biblioteca sAPI por encima de LPCOpen. El 3.1.6 pide un circuito impreso propio que integre
conectores, protección y desacople, de modo que el mapa de pines que se adopte ahora **condiciona el
rutado** de esa placa.

El módulo `sapi_servo` implementa la generación de señales para hasta nueve canales preasignados,
mediante temporizadores e interrupciones del LPC4337, sobre líneas específicas de los conectores P1 y
P2:

| Servo lógico | Salida física | Conector y pin |
|---|---|---|
| `SERVO0` | `T_FIL1` | P1 36 |
| `SERVO1` | `T_COL0` | P1 39 |
| `SERVO2` | `T_FIL2` | P1 37 |
| `SERVO3` | `T_FIL3` | P1 35 |
| `SERVO4` | `GPIO8` | P2 40 |
| `SERVO5` a `SERVO8` | `LCD1`, `LCD2`, `LCD3`, `GPIO2` | — |

Una primera versión del esquemático agrupaba las salidas de modulación en la tira P2, sin
correspondencia con ese mapa.

## Problema

¿Se adopta el mapa de pines nativo de la biblioteca, o se elige un reparto propio y se remapea en el
firmware?

## Opciones Consideradas

### Opción A — Reparto propio, con remapeo en la capa de abstracción

- **Descripción**: se eligen los pines por conveniencia de rutado del circuito impreso y se
  reconfigura el mapa interno del driver.
- **Ventajas**: libertad total para agrupar las señales donde convenga al trazado de la placa, lo que
  puede acortar pistas y simplificar el rutado.
- **Desventajas**: obliga a modificar la capa de abstracción de la biblioteca de la cátedra, con lo
  que el firmware deja de ser portable a otro equipo y cualquier actualización de sAPI hay que
  volver a parchearla. El remapeo no es solo una tabla: cada salida está atada a un temporizador y a
  una función de multiplexado concretos del LPC4337, de modo que no cualquier pin sirve.
- **Evidencia**: `sapi_servo.h` documenta que la implementación usa los Timer 1, 2 y 3; las salidas
  disponibles son las nueve de la tabla y no un conjunto arbitrario.
- **Costo**: tiempo de firmware y riesgo de depuración en la etapa de integración.

### Opción B — Adoptar el mapa nativo

- **Descripción**: se asignan `SERVO0` a `SERVO3` sobre la tira P1 y `SERVO4` sobre P2, respetando
  estrictamente el mapa de la biblioteca.
- **Ventajas**: `servoConfig()` y `servoWrite()` funcionan sin tocar nada; el plano y el firmware
  quedan en correspondencia directa; cualquier integrante puede probar un eje sin conocer el
  remapeo; no hay deuda con futuras versiones de sAPI.
- **Desventajas**: el rutado del circuito impreso tiene que acomodarse a pines ya fijados, repartidos
  entre las dos tiras.
- **Evidencia**: los cuatro ejes del brazo caen en P1 (35, 36, 37 y 39) y la pinza en P2 (40).
- **Costo**: nulo en firmware; alguna restricción de trazado.

### Opción C — Generar el PWM por cuenta propia, sin `sapi_servo`

- **Descripción**: configurar directamente el `SCTimer` del LPC4337 para las cinco salidas.
- **Ventajas**: libertad total de pines y control fino sobre la resolución del pulso.
- **Desventajas**: es trabajo de bajo nivel que la biblioteca ya resuelve, y que no aporta al
  objetivo del proyecto. Aumenta el riesgo en la ruta crítica del cronograma.
- **Costo**: alto en tiempo de desarrollo y depuración.

## Comparativa Resumida

| Criterio | A: reparto propio | B: mapa nativo | C: PWM propio |
|---|---|---|---|
| Esfuerzo de firmware | medio | **nulo** | alto |
| Libertad de rutado | alta | baja | alta |
| Portabilidad y mantenimiento | baja | alta | media |
| Riesgo en la integración | medio | bajo | alto |
| Correspondencia plano ↔ firmware | hay que documentarla | directa | hay que documentarla |

## Decisión

Se adopta la **opción B**. Los cinco servomotores se conectan a los pines nativos de `sapi_servo`:

| Servo lógico | Articulación | Salida física | Pin | Red del plano |
|---|---|---|---|---|
| `SERVO0` | Base | `T_FIL1` | P1 36 | `PWM_BASE` |
| `SERVO1` | Hombro | `T_COL0` | P1 39 | `PWM_HOMBRO` |
| `SERVO2` | Codo | `T_FIL2` | P1 37 | `PWM_CODO` |
| `SERVO3` | Muñeca | `T_FIL3` | P1 35 | `PWM_MUÑECA` |
| `SERVO4` | Pinza | `GPIO8` | P2 40 | `PWM_PINZA` |

Las entradas analógicas acompañan la misma lógica y se ubican sobre los canales que la placa expone
en P1: `CH3` en el pin 9, `CH2` en el 11, `CH1` en el 13 y `CH0` multiplexado en el 15.

## Rationale

El proyecto tiene su dificultad en el control coordinado y en la mecánica, no en la generación de
pulsos. Gastar tiempo de firmware y riesgo de integración para ganar libertad de trazado en una placa
de una sola hoja es un mal intercambio, sobre todo cuando el rutado todavía no mostró que los pines
nativos sean un problema.

Se acepta a sabiendas el peor criterio en libertad de rutado: si el trazado resultara forzado, el
costo recae sobre Ariana en la etapa de circuito impreso, y es un costo acotado y conocido, a
diferencia del de depurar un remapeo de temporizadores.

La opción C se descarta por la misma razón, agravada: reimplementa algo que ya funciona, en la ruta
crítica del cronograma.

## Implicaciones

- **Positivas**: `servoInit()` y `servoWrite()` se usan tal como vienen; el plano y el firmware se
  verifican uno contra el otro sin tabla intermedia.
- **Negativas**: las señales quedan repartidas entre las dos tiras, con la pinza sola en P2, lo que
  obliga a llevar masa a los dos conectores.
- **Riesgos**:
  - *Los Timer 1, 2 y 3 quedan tomados* por la biblioteca y no están disponibles para otras
    funciones que entren en conflicto. **Mitigación**: usar el `SysTick` como base de tiempo del
    superbucle, que es además lo que pide el requerimiento 3.3.9.
  - *Los números de pin del plano no coinciden con la documentación de la placa*. Ocurrió: la primera
    versión ubicaba las entradas analógicas en los pines 3, 5 y 7, que en la EDU-CIAA-NXP son
    `RESET`, `ISP` y `GNDA`. **Mitigación**: se verificó cada pin contra el documento oficial de la
    placa y se corrigieron las entradas analógicas; **quedan tres puntos abiertos**, detallados en
    [Esquemático y pines](Esquematico-y-pines), §6.
- **Acciones**:
  - Cerrar los tres pines pendientes antes de generar la netlist del circuito impreso (Ariana).
  - Alinear las etiquetas de canal del cuaderno de bajo nivel con las del plano (Lautaro).

## Consecuencias Observadas

La decisión ya se aplicó sobre el plano: las cinco salidas de modulación se movieron de la tira P2 a
los pines nativos, y las entradas analógicas se corrigieron a los canales reales. El informe de
avance 1 se entregó con esa asignación. Quedan los tres puntos de masa y pulsador por cerrar.

## Alternativas Futuras

Si el rutado del circuito impreso resultara impracticable con estos pines, la opción A sigue
disponible y su costo es acotado: `sapi_servo` permite redefinir el mapa, siempre dentro de las nueve
salidas que la biblioteca soporta. La señal que indicaría esto es que el trazado exija más de dos
capas o puentes.

## Referencias

- `Firmware_Control_bajo_nivel.ipynb`, secciones 5 y 6 — mapa de salidas y restricción de
  temporizadores.
- `diseño_esquemático.ipynb` — criterio de compatibilidad con sAPI.
- Proyecto CIAA, *EDU-CIAA-NXP v1.1 Board*, rev. 5r0, 3-1-2019 — numeración de P1 y P2.
- Informe de Avance 1, sección 4.5 y Anexo A.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-10-03 | Creación; las salidas PWM se mueven de P2 a los pines nativos de P1 | Ariana Ariza |
| 2026-10-05 | Se corrigen las entradas analógicas a los pines 9, 11, 13 y 15 | Ariana Ariza |
