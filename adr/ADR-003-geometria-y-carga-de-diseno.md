# ADR-003: Eslabones de 12 cm, alcance de 32,5 cm y carga de diseño de 145 g

- **Estado**: Aceptada
- **Fecha**: 2026-10-02
- **Autores**: Matias Lopez (02670/0)

## Contexto

El requerimiento 3.1.4 exige que el brazo tome el recipiente en una posición y lo deposite en otra
**sin desplazar la base**, y el 3.1.2 que manipule un recipiente cilíndrico con líquido.

Con el servomotor y la transmisión ya fijados ([ADR-001](ADR-001-transmision-por-engranajes)), el
alcance y la carga **dejan de ser independientes**: son las dos caras del mismo límite de par. Un
brazo más largo admite menos carga, porque el momento es peso por distancia.

El informe inicial dejaba ambos valores como «a determinar en la fase de diseño».

## Problema

¿Qué combinación de longitud de eslabón y carga máxima adoptar, sabiendo que aumentar una obliga a
reducir la otra?

## Opciones Consideradas

El cuaderno recorre el cálculo completo para varios tamaños y busca, en cada uno, la carga máxima que
las tres juntas admiten con sus transmisiones y el factor de seguridad de 2.

| `L1 = L2` | Alcance | Carga máxima | Quién limita |
|---|---|---|---|
| 8 cm | 24,5 cm | 309 g | codo |
| 10 cm | 28,5 cm | 252 g | codo |
| **12 cm** | **32,5 cm** | **205 g** | codo |
| 14 cm | 36,5 cm | 156 g | hombro |
| 16 cm | 40,5 cm | 106 g | hombro |

### Opción A — Eslabones de 10 cm, alcance 28,5 cm

- **Ventajas**: 252 g de carga máxima, un margen cómodo sobre los 145 g del recipiente.
- **Desventajas**: con 28,5 cm de alcance, la distancia entre el punto de toma y el de depósito se
  reduce a unos 16 cm, lo que vuelve poco demostrativa la tarea.
- **Evidencia**: tabla anterior, sección 8 del cuaderno.
- **Costo**: igual que las demás; cambia solo el largo del perfil.

### Opción B — Eslabones de 12 cm, alcance 32,5 cm

- **Ventajas**: el brazo toma el recipiente en un punto y lo deposita a unos 20 cm sin mover la base.
  205 g de carga máxima contra 145 g de carga de diseño, lo que deja 19 % de margen en el hombro
  sobre el factor de seguridad.
- **Desventajas**: hombro y codo quedan prácticamente empatados como articulación crítica, sin
  holgura para crecer.
- **Evidencia**: el par en el hombro es de 11,96 kg·cm y el del codo de 5,92; tras la transmisión
  exigen 7,97 y 7,89 kg·cm respectivamente, de 9,52 disponibles.
- **Costo**: igual.

### Opción C — Eslabones de 14 cm, alcance 36,5 cm

- **Ventajas**: 4 cm más de alcance.
- **Desventajas**: la carga máxima cae a 156 g, apenas 11 g por encima de la carga de diseño. Cualquier
  desviación del servomotor real respecto de la hoja de datos deja el brazo sin margen.
- **Evidencia**: tabla anterior.
- **Costo**: igual.

### Sobre la carga: por qué 145 g

El valor no se elige, se mide sobre un recipiente real: un vaso plástico de 55 mm de diámetro
interior con 44 mm de agua. El agua ocupa un cilindro de 105 cm³, que a 1 g/cm³ son 105 g, y el vaso
vacío pesa unos 40 g. Bajar de ahí sería usar un recipiente de juguete y la demostración perdería
sentido; subir obligaría a acortar el brazo.

## Comparativa Resumida

| Criterio | A: 10 cm | B: 12 cm | C: 14 cm |
|---|---|---|---|
| Alcance | 28,5 cm | 32,5 cm | 36,5 cm |
| Carga máxima | 252 g | 205 g | 156 g |
| Margen sobre la carga de diseño de 145 g | 74 % | **41 %** | 8 % |
| Margen del hombro sobre FS 2 | holgado | 19 % | nulo en la práctica |
| Demostración de la tarea | pobre | adecuada | adecuada |
| Riesgo ante un servomotor más flojo que la hoja de datos | bajo | medio | **alto** |

## Decisión

Se adoptan **eslabones de 12 cm** (`L1 = L2 = 12 cm`), muñeca de 8,5 cm y altura del hombro de 9 cm,
lo que da un **alcance de 32,5 cm**. La carga de diseño es de **145 g** y la carga máxima admisible
calculada, de **205 g**.

## Rationale

La opción C se descarta porque sus 11 g de margen sobre la carga de diseño no absorben ninguna de
las incertidumbres que el factor de seguridad está pensado para cubrir, en particular que los clones
del MG996R suelen entregar entre 10 y 20 % menos que la hoja de datos.

La opción A es la más segura pero no cumple bien el propósito: con 28,5 cm el traslado es tan corto
que no demuestra la tarea del requerimiento 3.1.4.

La opción B es el punto donde las dos curvas se cruzan de manera aceptable: alcance suficiente para
una demostración real y 41 % de margen de carga. Se acepta explícitamente que es peor que A en
riesgo, y que el hombro queda con el margen más ajustado del proyecto, 19 %.

Vale registrar un efecto que apareció al hacer el barrido: **quién limita cambia con el tamaño**. De
14 cm en adelante manda el hombro, que carga todo el brazo; por debajo manda el codo, porque su par
crece más rápido con la carga —la soporta a 20,5 cm de su eje contra 32,5 del hombro, pero su
transmisión solo multiplica 1,5 veces contra 3— y a 12 cm los dos quedan empatados. El tamaño
adoptado es, casualmente, el punto de equilibrio entre las dos articulaciones.

## Implicaciones

- **Positivas**: fija los valores que el informe inicial dejaba abiertos y permite cerrar el
  dimensionamiento, la alimentación y la lista de materiales.
- **Negativas**: el hombro queda como la articulación que define el diseño, con 19 % de margen, y el
  codo inmediatamente detrás con 21 %.
- **Riesgos**:
  - *El servomotor real entrega menos que la hoja de datos*. **Mitigación**: la tabla de tamaños
    indica cuánto bajar la carga; es el ensayo n.º 2 de la lista.
  - *El recipiente definitivo pesa más de 145 g*. **Mitigación**: se lo pesa en balanza **antes** de
    comprar el resto de los materiales. Es un límite, no un valor nominal.
- **Acciones**:
  - Pesar el recipiente definitivo y confirmar que no supera los 145 g (Matias).
  - Ensayar primero el hombro cuando lleguen los componentes (Matias).
  - Los puntos de toma y de depósito se ubican a la altura de la tapa de la caja-base, no sobre la
    mesa, porque el hombro solo dispone de 60° de barrido.

## Consecuencias Observadas

Pendiente de implementación. La estructura todavía no se fabricó.

## Alternativas Futuras

Si el par de bloqueo real quedara por debajo de lo previsto, la tabla de tamaños indica directamente
la carga máxima admisible para cada largo de eslabón, de modo que la corrección es recalcular, no
rediseñar. Si hiciera falta más alcance, el camino es la opción B de
[ADR-002](ADR-002-riel-de-5v-sin-convertidor): alimentar a 6 V, lo que recupera 1,5 kg·cm.

## Referencias

- `Dimensionamiento_brazo.ipynb`, secciones 1, 2, 5 y 8.
- Informe de Avance 1, requerimientos 3.1.2 y 3.1.4; sección 4.7 y Anexo C.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-10-02 | Creación, tras descartar la variante de brazo corto con resorte | Matias Lopez |
