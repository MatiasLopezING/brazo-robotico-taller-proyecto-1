# ADR-006: Usar la fuente de computadora como lastre de la base

- **Estado**: Aceptada
- **Fecha**: 2026-09-28
- **Autores**: Matias Lopez (02670/0)

## Contexto

El requerimiento 3.3.8 exige que el prototipo sea transportable y esté montado sobre una base que
impida su vuelco durante la operación.

El par que ve el hombro **también existe como momento de vuelco sobre la mesa**: el brazo estirado
tiende a tumbar el conjunto hacia adelante. La transmisión no interviene, porque multiplica el par
entre el servomotor y la articulación, pero el momento que el brazo ejerce sobre la mesa depende de
los pesos y sus distancias, no de cómo se los sostenga. Ese momento es de **11,96 kg·cm**.

El criterio adoptado es `m_base · R_base ≥ FS · τ_hombro`, con un factor de seguridad de 1,5, más
relajado que el de los servomotores porque el vuelco es una condición estática y las masas
involucradas se conocen mejor.

| Lado de la caja | Radio | Masa mínima |
|---|---|---|
| 14 cm | 7,0 cm | 2,56 kg |
| 20 cm | 10,0 cm | 1,79 kg |
| 25 cm | 12,5 cm | 1,44 kg |
| 30 cm | 15,0 cm | 1,20 kg |

Hacen falta casi **1,8 kg** de lastre en un radio de 10 cm: más que todo el resto del brazo junto,
que ronda los 700 g.

## Problema

¿De dónde sale la masa que impide el vuelco, sin convertir el prototipo en algo intransportable ni
obligarse a amurarlo a la mesa?

## Opciones Consideradas

### Opción A — Amurar el conjunto a la mesa

- **Descripción**: morsas o tornillos pasantes que fijan la base al tablero.
- **Ventajas**: resuelve el vuelco por completo y sin masa adicional.
- **Desventajas**: **incumple el requerimiento 3.3.8**, que pide que el prototipo sea transportable.
  Obliga a disponer de una mesa apta en cada demostración y en la presentación final.
- **Costo**: bajo.

### Opción B — Lastre dedicado

- **Descripción**: una placa de acero o un contenedor con arena dentro de la base.
- **Ventajas**: dimensionable a voluntad; independiente del resto del diseño.
- **Desventajas**: agrega 1,5 a 2 kg de masa muerta que hay que comprar, alojar y transportar, sin
  que cumpla ninguna otra función.
- **Costo**: el del material y el volumen que ocupa.

### Opción C — La fuente ATX dentro de una caja impresa que hace de base

- **Descripción**: se imprime una caja que encierra la fuente de computadora ya adoptada en
  [ADR-002](ADR-002-riel-de-5v-sin-convertidor), y el brazo se monta encima.
- **Ventajas**: **el lastre ya está comprado**. Una fuente ATX pesa entre 1,2 y 2 kg, de modo que con
  una caja de 25 × 25 cm —radio de 12,5 cm— el criterio se cumple con 1,44 kg y el prototipo no
  necesita amurarse. Además acorta el cableado de potencia, lo que reduce la caída de tensión que el
  cálculo eléctrico exige mantener por debajo del 3 %; protege la fuente y la oculta; y el conjunto
  queda transportable de una pieza.
- **Desventajas**: la caja levanta el hombro unos 12,5 cm sobre la mesa; hay que imprimir una pieza
  grande; y la masa real depende de la unidad de fuente que se consiga.
- **Evidencia**: tabla de la sección 10 del cuaderno de dimensionamiento.
- **Costo**: filamento y tiempo de impresora.

## Comparativa Resumida

| Criterio | A: amurar | B: lastre dedicado | C: la fuente como base |
|---|---|---|---|
| Cumple 3.3.8 (transportable) | **no** | sí | sí |
| Masa agregada que hay que comprar | ninguna | 1,5 a 2 kg | **ninguna** |
| Efecto sobre el cableado de potencia | neutro | neutro | lo acorta |
| Funciones que cumple la masa | — | solo lastre | lastre + fuente + gabinete |
| Dependencia de la mesa | alta | ninguna | ninguna |
| Costo | bajo | medio | filamento |

## Decisión

Se adopta la **opción C**: la fuente ATX se aloja dentro de una caja impresa de **25 × 25 cm** que
actúa como base del brazo y como lastre contra el vuelco.

## Rationale

La opción A se descarta por incumplir un requerimiento explícito. La B resuelve el problema pero paga
por masa muerta cuando el proyecto ya tiene 1,2 a 2 kg disponibles que, además, tienen que ir a algún
lado igual.

La C convierte un componente obligatorio en parte de la solución estructural. Es la misma lógica que
[ADR-001](ADR-001-transmision-por-engranajes): aprovechar lo que ya está antes que agregar algo
nuevo.

El lado de 25 cm se elige porque es el primer tamaño en el que el criterio se cumple con el extremo
inferior del rango de masas de una ATX (1,44 kg necesarios contra 1,2 a 2 kg disponibles), de modo
que el diseño no depende de conseguir una fuente pesada.

## Implicaciones

- **Positivas**: el prototipo es transportable de una pieza; el cableado de potencia queda corto; la
  fuente queda protegida y no a la vista.
- **Negativas**: la caja **levanta el hombro unos 12,5 cm sobre la mesa**. Como el hombro solo
  dispone de 60° de barrido, los puntos de toma y de depósito conviene ubicarlos a la altura de la
  tapa de la caja y no sobre la mesa. Esto condiciona el montaje de la demostración.
- **Riesgos**:
  - *La fuente que se consiga pesa menos de 1,44 kg*. **Mitigación**: pesarla antes de imprimir la
    caja; si no alcanza, el lado se lleva a 30 cm, que baja el requisito a 1,20 kg.
  - *La caja no soporta el momento* y se deforma. **Mitigación**: la tapa superior se diseña con
    refuerzo bajo el punto de montaje de la base.
- **Acciones**:
  - Pesar la fuente y confirmar el criterio con el lado elegido (Matias).
  - Modelar la caja con el refuerzo bajo el eje de la base (Matias y Lautaro).
  - Prever el paso de cables desde la fuente hacia el brazo con holgura para los 360° de la base.

## Consecuencias Observadas

Pendiente de implementación. La caja todavía no se modeló.

## Alternativas Futuras

Si la fuente disponible resultara demasiado liviana y una caja de 30 cm fuera inconveniente por
tamaño, el camino es combinar: la fuente más una placa de acero delgada en el perímetro de la base,
que agrega masa justo donde el radio es máximo y por lo tanto rinde más por gramo.

## Referencias

- `Dimensionamiento_brazo.ipynb`, sección 10 — criterio de vuelco y tabla de masas mínimas.
- Informe de Avance 1, requerimiento 3.3.8 y sección 4.7.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-09-28 | Creación | Matias Lopez |
