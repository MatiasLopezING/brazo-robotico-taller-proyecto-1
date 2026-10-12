# ADR-002: Alimentar el conjunto desde el riel de +5 V de una fuente ATX, sin convertidor

- **Estado**: Aceptada
- **Fecha**: 2026-09-28
- **Autores**: Matias Lopez (02670/0), Ariana Ariza (02879/6)

## Contexto

Los cinco MG996R admiten de 4,8 a 7,2 V y su par crece con la tensión: 9,4 kg·cm a 4,8 V y
11,0 kg·cm a 6,0 V según la hoja de datos de TowerPro. El consumo estimado es de **4,71 A en
régimen** y **6,22 A de pico** con arranque escalonado (`Alimentacion_brazo.ipynb`, secciones 3 y 4).

El requerimiento 3.1.5 pide que los actuadores se alimenten desde un bus de potencia con cableado
independiente del de la lógica, con el que solo comparte la masa. El 3.3.4 pide que el sistema no
opere con tensiones que impliquen riesgo eléctrico.

[ADR-001](ADR-001-transmision-por-engranajes) bajó el par que debe entregar el servomotor del hombro
de 11,96 a 3,99 kg·cm, lo que cambia por completo el planteo de este ADR: con acople directo, ninguna
tensión admisible alcanzaba.

## Problema

¿A qué tensión se alimentan los servomotores, y con qué fuente, de modo que el hombro verifique con
el factor de seguridad adoptado?

## Opciones Consideradas

### Opción A — Riel de +5 V de una fuente ATX, directo

- **Descripción**: se usa una fuente de computadora en desuso y únicamente su riel de +5 V. Los
  servomotores y la placa cuelgan de la misma tensión, con pares de cables separados.
- **Ventajas**: sin componentes intermedios; la fuente trae protección y filtrado de red, gabinete
  cerrado y ficha de red; el riel de +5 V entrega más de 20 A, cuatro veces lo necesario; su masa ya
  está unida al chasis y a la tierra del enchufe, de modo que la tierra común queda resuelta por
  construcción.
- **Desventajas**: es la tensión más baja admisible, con lo que el par disponible es el mínimo. Su
  capacidad de cortocircuito —más de 20 A— alimentaría un error de cableado hasta quemar algo.
- **Evidencia**: descontando la caída de 0,11 V en el cable de 1,5 mm², al servomotor llegan
  **4,89 V** y el par disponible es de **9,52 kg·cm**, contra los 7,97 kg·cm que el hombro exige con
  FS 2. Margen: **19 %**.
- **Costo**: una fuente en desuso, sin costo.

### Opción B — Convertidor reductor de +12 V a 6 V

- **Descripción**: se toma el riel de +12 V de la misma fuente y se baja a 6 V con un convertidor
  conmutado para los servomotores.
- **Ventajas**: 11,0 kg·cm de par disponible, un 16 % más que a 4,89 V. Permitiría una reducción de
  2,5:1 en el hombro y conservar 72° de barrido en vez de 60°.
- **Desventajas**: agrega un componente, su disipador y unos 5 W de disipación. Y agrega un modo de
  falla nuevo y severo: **si el preajuste del convertidor se mueve, la salida puede subir a 12 V y
  quemar los cinco servomotores de una vez.**
- **Evidencia**: a 6 V el par es de 11,00 kg·cm; con reducción 2,5:1 el hombro exige 9,57 kg·cm, que
  a 4,89 V no verifica (9,52 disponibles) y a 6 V sí.
- **Costo**: el del convertidor más el disipador, y el tiempo de montaje y verificación.

### Opción C — Fuente conmutada de laboratorio de 6 V

- **Descripción**: una fuente dedicada de 6 V y al menos 7 A.
- **Ventajas**: tensión exacta, limitación de corriente propia que protege ante un error de
  cableado.
- **Desventajas**: costo muy superior al de una ATX en desuso de potencia equivalente. Con 5 o 7 A
  nominales, el pico de arranque la pondría al límite y su tensión se hundiría justo cuando el brazo
  más par necesita.
- **Costo**: alto, contra presupuesto de materia.

## Comparativa Resumida

| Criterio | A: +5 V directo | B: convertidor a 6 V | C: fuente de 6 V |
|---|---|---|---|
| Par disponible | 9,52 kg·cm | 11,00 kg·cm | 11,00 kg·cm |
| Margen en el hombro con FS 2 | 19 % | 38 % | 38 % |
| Componentes agregados | ninguno | convertidor + disipador | ninguno |
| Comportamiento en el pico de 6,22 A | la tensión no se hunde | igual | se hunde |
| Modo de falla agregado | cortocircuito sin límite | **sobretensión a 12 V** | ninguno |
| Costo | nulo | medio | alto |

## Decisión

Se adopta la **opción A**: riel de +5 V de una fuente ATX, sin ningún convertidor, con fusible
obligatorio de 8 A retardado junto a la fuente.

| Ítem | Valor |
|---|---|
| Corriente en régimen | 4,71 A |
| Pico de arranque, escalonado 150 ms | 6,22 A |
| Cable de potencia | 1,5 mm² (AWG 16), caída de 0,11 V (2,2 %) |
| Capacitor de bus | 2200 µF / 16 V |
| Fusible | 8 A retardado |
| Rama de lógica | 5 V / 0,35 A, del mismo riel con cables propios |

## Rationale

La diferencia de par entre A y B es real pero no es necesaria: con la transmisión de
[ADR-001](ADR-001-transmision-por-engranajes), 9,52 kg·cm bastan con 19 % de margen. Pagar un
componente, un disipador y 5 W de disipación para ganar un margen que no hace falta no se justifica,
y menos cuando ese componente introduce un modo de falla que destruye los cinco actuadores a la vez.

Dicho de otro modo: **se gasta un engranaje más grande en vez de un componente electrónico**. El
engranaje cuesta dos horas de impresora.

La opción C se descarta por costo y, sobre todo, por comportamiento dinámico: el pico de arranque
de 6,22 A pondría al límite a una fuente dedicada, mientras que con la ATX la tensión no se hunde.
Incluso en el caso extremo de los cinco servomotores arrancando juntos (10,19 A), la caída es de
0,24 V y el par disponible queda en 9,35 kg·cm, todavía por encima de los 7,97 que el hombro
necesita.

Se acepta explícitamente el peor criterio en «modo de falla agregado»: la ATX no limita corriente.
Por eso el fusible deja de ser una buena práctica y pasa a ser obligatorio.

## Implicaciones

- **Positivas**: arquitectura eléctrica sin componentes activos intermedios; la tierra común queda
  resuelta por construcción; la fuente habilita [ADR-006](ADR-006-fuente-como-lastre-de-la-base).
- **Negativas**: el margen del hombro queda en 19 %, el más ajustado del diseño, y cualquier
  desviación del servomotor real respecto de la hoja de datos lo consume.
- **Riesgos**:
  - *Cortocircuito alimentado por más de 20 A*. **Mitigación**: fusible de 8 A retardado lo más cerca
    posible de la fuente, por encima del pico de 6,22 A y por debajo de lo que tolera el cable de
    1,5 mm².
  - *Inversión de polaridad*, que quemaría los cinco servomotores. **Mitigación**: conector
    polarizado en la entrada del bus.
  - *Clones del MG996R que entreguen menos par que la hoja de datos*, típicamente entre 10 y 20 %
    menos. **Mitigación**: es el ensayo n.º 2 de la lista; si da menos de 9,5 kg·cm, se baja la carga
    o se pasa a la opción B.
- **Acciones**:
  - Medir el par de bloqueo real alimentando a 5 V (Matias).
  - Verificar la caída en bornes del servomotor más lejano en la pose de mayor esfuerzo (Matias).
  - Incorporar fusible, capacitor y conector polarizado al circuito impreso (Ariana).

## Consecuencias Observadas

Pendiente de implementación. La fuente todavía no se puso en marcha.

## Alternativas Futuras

Si el par de bloqueo real medido a 5 V quedara por debajo de 9,5 kg·cm, o si el ensayo mostrara que
60° de barrido en el hombro no alcanzan, el camino de vuelta es la opción B: convertidor desde el
riel de +12 V a 6 V y reducción 2,5:1. El resto del diseño eléctrico —bus, capacitor, cable,
fusible— no cambia.

## Referencias

- `Alimentacion_brazo.ipynb`, secciones 2 a 8.
- TowerPro, MG996R Digital Servo, hoja de datos del fabricante.
- Informe de Avance 1, sección 4.6.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-09-28 | Creación | Matias Lopez |
| 2026-10-03 | Se corrige el riel indicado en el esquemático de +6 V a +5 V | Ariana Ariza |
