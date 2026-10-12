# ADR-005: Mapear la lectura del joystick a velocidad y no a posición absoluta

- **Estado**: Aceptada
- **Fecha**: 2026-10-02
- **Autores**: Juan David Alvarez (03100/2), Lautaro Lopes (02978/9)

## Contexto

Los módulos KY-023 llevan dos potenciómetros de 10 kΩ **con resorte de retorno al centro**: al
soltar el mando, la palanca vuelve sola a la posición central y la lectura del conversor vuelve a
mitad de escala, unos 512 de 1023 en un ADC de 10 bits.

El requerimiento 3.3.9 pide usar el `SysTick` como base de tiempo sin retardos bloqueantes, de modo
que la lectura del mando y la actualización de los ángulos ocurren cada 10 a 20 ms.

El caso de uso es trasladar un recipiente abierto con líquido, y el dimensionamiento solo es válido
mientras ningún tramo acelere más de 0,98 m/s².

## Problema

¿Qué representa la posición de la palanca del joystick: el ángulo que debe tomar la articulación, o
la velocidad a la que debe moverse?

## Opciones Consideradas

### Opción A — Posición absoluta

- **Descripción**: la lectura del conversor se mapea linealmente al ángulo de la articulación. Palanca
  al centro, articulación a 90°; palanca a fondo, articulación en su tope.
- **Ventajas**: la implementación es una única interpolación lineal, sin estado acumulado. La
  correspondencia entre mando y brazo es inmediata y no se desincroniza.
- **Desventajas**: **al soltar la palanca, el resorte la devuelve al centro y la articulación salta a
  su posición central**, de golpe y con el recipiente cargado. Además, todo el recorrido de la
  articulación queda comprimido en el recorrido de la palanca, de modo que un movimiento fino es
  imposible y la velocidad la impone la mano del operador, sin ningún límite.
- **Evidencia**: el resorte de retorno es una característica física del KY-023, no un parámetro
  configurable. La aceleración resultante de un retorno por resorte supera en órdenes de magnitud
  los 0,98 m/s² admisibles.
- **Costo**: nulo.

### Opción B — Velocidad

- **Descripción**: la lectura se mapea a un incremento angular por ciclo. Palanca al centro,
  incremento cero; palanca desplazada, la articulación se mueve a velocidad proporcional al
  desplazamiento, mientras se la mantenga.
- **Ventajas**: al soltar la palanca la velocidad se anula y **el servomotor conserva su posición**.
  La velocidad máxima queda acotada por el firmware, no por la mano del operador, lo que permite
  respetar el límite de aceleración. El movimiento fino se obtiene con desplazamientos pequeños y
  sostenidos.
- **Desventajas**: requiere mantener el ángulo como estado acumulado y acotarlo contra los límites
  mecánicos de cada articulación. La correspondencia entre la posición de la palanca y la del brazo
  deja de ser directa.
- **Evidencia**: con actualización cada 20 ms e incrementos de 1°, la velocidad resultante es de
  50 °/s, del orden de los 45 °/s que piden los tramos de 2 a 4 segundos.
- **Costo**: nulo.

### Opción C — Posición absoluta con rampa de aproximación

- **Descripción**: mapeo a posición, pero la articulación persigue la consigna con una velocidad
  máxima limitada.
- **Ventajas**: acota la velocidad y conserva la correspondencia directa entre palanca y brazo.
- **Desventajas**: **no resuelve el problema del resorte**: al soltar la palanca la consigna sigue
  siendo el centro, de modo que el brazo vuelve igual, solo que despacio. Para un recipiente cargado,
  que vuelva despacio a una posición no deseada no es mejor que no volver.
- **Costo**: nulo; algo más de firmware que B.

## Comparativa Resumida

| Criterio | A: posición | B: velocidad | C: posición con rampa |
|---|---|---|---|
| Comportamiento al soltar el mando | **salta al centro** | conserva posición | vuelve al centro despacio |
| Respeta el límite de 0,98 m/s² | no | sí | sí |
| Permite movimiento fino | no | sí | parcial |
| Estado que hay que mantener | ninguno | el ángulo de cada eje | el ángulo de cada eje |
| Complejidad | mínima | baja | media |

## Decisión

Se adopta la **opción B**: la lectura normalizada del joystick se interpreta como **velocidad
angular**, y la capa de lógica integra esa velocidad para obtener el ángulo de cada articulación.

Se acompaña de una **zona muerta** de ±30 cuentas alrededor del centro, para que el ruido eléctrico y
la vibración de la palanca en reposo no produzcan movimiento:

```c
#define CENTRO_ADC      512
#define ZONA_MUERTA     30

if (valor > CENTRO_ADC - ZONA_MUERTA && valor < CENTRO_ADC + ZONA_MUERTA) {
    comando = 0;
}
```

El valor exacto del centro **se determina experimentalmente**, porque el joystick no entrega
exactamente 512.

## Rationale

La opción A se descarta por una consecuencia que es inaceptable en este proyecto: el retorno por
resorte convierte el gesto más natural del operador —soltar el mando— en el movimiento más violento
que el brazo puede hacer, justo cuando sostiene un recipiente con líquido.

La C se descarta porque atiende el síntoma y no la causa: suaviza el retorno pero el brazo sigue
volviendo a una posición que el operador no pidió.

La B resuelve las dos cosas con la misma decisión: el reposo del mando significa «quedate donde
estás», y la velocidad máxima pasa a ser un parámetro del firmware, lo que permite respetar
directamente el límite de aceleración del que depende la validez de todo el dimensionamiento.

Se acepta el peor criterio en «estado que hay que mantener». Es un costo real —hay que acotar el
ángulo acumulado contra los límites mecánicos de cada articulación— pero es trabajo de firmware, no
un riesgo para el recipiente.

## Implicaciones

- **Positivas**: el límite de aceleración de 0,98 m/s² y el de velocidad angular de la base de
  1,74 rad/s pueden imponerse directamente sobre el incremento; el movimiento fino es posible.
- **Negativas**: el firmware debe acotar el ángulo de cada eje contra sus topes (360° base, 60°
  hombro, 120° codo, 270° muñeca) en cada ciclo, porque un ángulo acumulado sin límite se saldría del
  recorrido físico.
- **Riesgos**:
  - *Deriva*: si la zona muerta queda corta, un offset del centro hace que la articulación se mueva
    sola. **Mitigación**: calibración del centro real en el arranque y zona muerta de ±30 cuentas.
  - *El operador pierde la referencia* de dónde está cada articulación. **Mitigación**: señalización
    de estado por los LED de la placa y, eventualmente, una posición de reposo conocida.
- **Acciones**:
  - Implementar la integración y el acotado por articulación en la capa de lógica (David).
  - Medir el centro real de cada uno de los cuatro potenciómetros y ajustar la zona muerta
    (Lautaro).

## Consecuencias Observadas

Pendiente de implementación.

## Alternativas Futuras

Si el control por velocidad resultara lento para posicionar, una mejora compatible es hacer el
incremento proporcional al cuadrado del desplazamiento de la palanca, lo que da precisión cerca del
centro y rapidez en los extremos sin cambiar la decisión. La señal que indicaría esto es que el
ensayo de traslado tarde notoriamente más que los 4 segundos previstos para el tramo largo.

## Referencias

- `Firmware_Control_bajo_nivel.ipynb`, sección 3 — acondicionamiento de la lectura y zona muerta.
- `Diseño_de_SW.ipynb`, sección 1 — decisión crítica sobre el retorno por resorte.
- `Dimensionamiento_brazo.ipynb`, secciones 3.4 y 6.5 — límites de aceleración y de velocidad
  angular.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-10-02 | Creación | Juan David Alvarez |
