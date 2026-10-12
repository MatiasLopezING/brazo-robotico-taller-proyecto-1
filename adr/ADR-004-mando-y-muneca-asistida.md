# ADR-004: Dos joysticks de dos ejes, con la muñeca calculada por el firmware

- **Estado**: Aceptada
- **Fecha**: 2026-10-02
- **Autores**: Juan David Alvarez (03100/2), Matias Lopez (02670/0)

## Contexto

El brazo tiene cuatro articulaciones de posición más la pinza (requerimiento 3.1.1). El
requerimiento 3.1.7 pide una interfaz de operador con joysticks analógicos y un pulsador, y el 3.2.3
exige mantener el recipiente en posición vertical con la pinza cerrada.

La EDU-CIAA-NXP expone sobre el conector P1 tres canales analógicos directos a través de `sapi_adc`
—`CH1`, `CH2` y `CH3`— más el pin 15, que por defecto es la salida del convertidor digital-analógico
y puede multiplexarse como `CH0`.

La condición que estructura el problema es física: una aceleración brusca derrama el líquido, y una
inclinación del recipiente también. El criterio adoptado acota la aceleración a 0,98 m/s², pero nada
impide que un operador incline el vaso simplemente moviendo el hombro sin corregir la muñeca.

## Problema

¿Cómo se comandan cuatro articulaciones de posición de modo que el recipiente se mantenga vertical,
y con qué dispositivos de mando?

## Opciones Consideradas

### Opción A — Un joystick de dos ejes multiplexado entre pares de articulaciones

- **Descripción**: un único módulo y un pulsador de modo que conmuta entre «base-hombro» y
  «codo-muñeca».
- **Ventajas**: usa dos canales analógicos en lugar de cuatro; menos componentes y menos cableado.
- **Desventajas**: obliga al operador a cambiar de modo **en medio de un traslado**, que es
  justamente cuando el recipiente está cargado. El cambio de modo introduce una pausa y un riesgo de
  error en el peor momento posible.
- **Evidencia**: la tarea del requerimiento 3.1.4 es un traslado continuo de un punto a otro; no hay
  una pausa natural donde conmutar.
- **Costo**: un módulo KY-023 menos.

### Opción B — Cuatro ejes analógicos, uno por articulación, todos manuales

- **Descripción**: dos joysticks de dos ejes, cada eje a una articulación, incluida la muñeca.
- **Ventajas**: control total y explícito; no requiere trigonometría en el firmware.
- **Desventajas**: el operador debe corregir la muñeca **a mano y de forma continua** mientras mueve
  el hombro y el codo, para compensar `q4 = 90° − q2 − q3`. Es una tarea de coordinación de tres ejes
  simultáneos que, si se hace mal, derrama el contenido. Convierte el objetivo del proyecto en una
  habilidad del operador.
- **Evidencia**: la muñeca debe compensar la suma de los recorridos del hombro y del codo, 180°.
- **Costo**: igual que la opción C.

### Opción C — Tres ejes manuales y la muñeca calculada por el microcontrolador

- **Descripción**: el operador gobierna base, hombro y codo; el firmware calcula de forma continua
  el ángulo de contra-rotación de la muñeca, `q4 = 90° − q2 − q3`, para mantener la pinza
  perpendicular al suelo. El cuarto eje queda cableado como reserva.
- **Ventajas**: el recipiente se mantiene vertical **por construcción** y no por pericia del
  operador. Aprovecha la unidad de punto flotante del Cortex-M4. Deja un eje libre para un ajuste
  fino posterior.
- **Desventajas**: el operador pierde el control directo de la muñeca; un error en la trigonometría o
  en la calibración se traduce en inclinación permanente.
- **Evidencia**: la muñeca dispone de 270° de recorrido gracias al par de engranajes invertido
  ([ADR-001](ADR-001-transmision-por-engranajes)), contra los 180° que debe compensar. El margen es
  de 90°.
- **Costo**: dos módulos KY-023 y un pulsador; la trigonometría es una resta.

## Comparativa Resumida

| Criterio | A: un joystick multiplexado | B: cuatro ejes manuales | C: tres ejes + muñeca asistida |
|---|---|---|---|
| Canales analógicos usados | 2 | 4 | 3 (+1 de reserva) |
| Verticalidad del recipiente | depende del operador | depende del operador | **por construcción** |
| Carga cognitiva del operador | alta: cambia de modo cargado | alta: coordina tres ejes | baja |
| Complejidad de firmware | baja | baja | media (trigonometría) |
| Cumple 3.2.3 | no de forma verificable | no de forma verificable | sí |
| Componentes | 1 joystick | 2 joysticks | 2 joysticks |

## Decisión

Se adopta la **opción C**. Se emplean dos módulos de joystick KY-023 de dos ejes y un pulsador para
la pinza, que solo necesita dos estados.

| Mando | Articulación |
|---|---|
| Joystick A, eje X | base (`q1`) |
| Joystick A, eje Y | hombro (`q2`) |
| Joystick B, eje X | codo (`q3`) |
| Joystick B, eje Y | reserva, sin asignar |
| Pulsador | pinza (`q5`), alterna entre abierta y cerrada |

La muñeca (`q4`) no se comanda: el firmware calcula su ángulo a partir de los del hombro y el codo.
La bandera de «muñeca asistida» se habilita **automáticamente al cerrar la pinza**, porque con la
pinza cerrada se asume que sostiene una carga.

## Rationale

La opción A se descarta por una razón de uso y no de recursos: ahorra dos canales analógicos a costa
de pedirle al operador que cambie de modo en el instante de mayor riesgo.

Entre B y C, la diferencia es dónde vive la garantía de verticalidad. En B es una habilidad humana
que no puede verificarse ni repetirse; en C es una ecuación que el microcontrolador ejecuta cada
20 ms. El requerimiento 3.2.3 está escrito como una obligación del firmware, no del operador, de
modo que C es la única que lo cumple de forma verificable.

Se acepta el peor criterio en complejidad de firmware. A cambio, el objetivo central del proyecto
—que el líquido no se derrame— deja de depender de quién esté al mando.

El pulsador elegido es un botón arcade de 30 mm: es el pulsador de panel más grande y más económico
del mercado local, entra a presión sin tuerca, y su contacto normal abierto va directo entre la
entrada digital y masa, porque el LPC4337 aporta la resistencia interna de elevación.

## Implicaciones

- **Positivas**: el recipiente se mantiene vertical sin intervención; queda un eje analógico libre
  para un ajuste fino de la muñeca si el ensayo lo pidiera.
- **Negativas**: el firmware debe conocer la geometría y la relación de transmisión de hombro, codo y
  muñeca; un error de calibración se manifiesta como inclinación permanente.
- **Riesgos**:
  - *La muñeca se queda sin recorrido*. **Mitigación**: dispone de 270° contra 180° necesarios, con
    90° de margen que absorben además el riesgo del supuesto de barrido.
  - *La aceleración centrípeta al girar la base inclina el recipiente y la muñeca no puede
    corregirla*, porque está fuera de su plano de giro. **Mitigación**: límite de velocidad angular
    de la base de 1,74 rad/s en el firmware.
  - *El operador no entiende por qué la muñeca se mueve sola*. **Mitigación**: el instructivo de uso
    del requerimiento 3.3.7 debe explicarlo.
- **Acciones**:
  - Implementar `q4 = 90° − q2 − q3` en la capa de lógica, en ángulos de articulación (David).
  - Definir la rutina de calibración del centro de cada joystick (Lautaro).
  - Decidir el uso del cuarto eje tras el primer ensayo de verticalidad (grupo).

## Consecuencias Observadas

Pendiente de implementación. La máquina de estados ya contempla la bandera de «muñeca asistida» y su
habilitación automática al cerrar la pinza.

## Alternativas Futuras

Si el ensayo mostrara un desvío residual en la vertical del recipiente, el cuarto eje analógico
—cableado y sin asignar— pasa a ser un ajuste fino que el operador suma al ángulo calculado. La señal
que indicaría esto es el ensayo de traslado con el recipiente cargado.

## Referencias

- `Diseño_de_SW.ipynb`, sección 1 — estrategia de control.
- `Dimensionamiento_brazo.ipynb`, sección 6.3 — recorrido disponible en la muñeca.
- Informe de Avance 1, requerimientos 3.1.7 y 3.2.3; secciones 4.3 y 5.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-10-02 | Creación | Juan David Alvarez |
