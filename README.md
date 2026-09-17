# Brazo robótico teleoperado de cinco servomotores

Proyecto grupal de **Taller de Proyecto I (E0306)** — Facultad de Ingeniería, UNLP
Departamento de Electrotecnia — 2.º cuatrimestre 2026

Brazo robótico de cuatro grados de libertad más pinza, accionado por cinco
servomotores y gobernado por la placa **EDU-CIAA-NXP** (microcontrolador NXP
LPC4337, ARM Cortex-M4), para la manipulación remota de recipientes en entornos
con riesgo químico, con monitoreo de gases y parada de emergencia por hardware.

## Integrantes

| Nombre | Legajo |
|---|---|
| Lopez Matias | 02670/0 |
| Juan David Alvarez | 03100/2 |
| Lautaro Lopes | 02978/9 |
|  |  |

Grupo N.º 3 · Docente a cargo: Malena Crespi

## Estado del proyecto

| Entrega | Vencimiento | Estado |
|---|---|---|
| Informe inicial | 10/09/2026 | entregado |
| Informe de avance 1 (diseño alto nivel, esquemáticos) | 05/10/2026 | pendiente |
| Informe de avance 2 (diseño bajo nivel, PCB) | 05/11/2026 | pendiente |
| Informe final | 11/02/2027 | pendiente |
| Presentación | 18 y 22/02/2027 | pendiente |

## Contenido

- `Informe_Inicial_v0.docx` — informe inicial, versión editable
- `Informe_Inicial_v0.pdf` — informe inicial, versión para entregar

A medida que avance el proyecto se sumarán el firmware, los esquemáticos, el
diseño de PCB y los protocolos de ensayo.

## Dimensiones del brazo

El brazo cuenta con **cuatro grados de libertad** (hombro, codo, muñeca y
pinza), accionado por cinco servomotores. Los primeros cálculos de
dimensionamiento —geometría de eslabones, par necesario en cada articulación
y selección de servos— se encuentran en el cuaderno
`Dimensionamiento_brazo.ipynb`.

Los valores obtenidos son preliminares; falta corrección y revisión en detalle.

## Convenciones de trabajo

- Rama `main`: siempre en estado entregable.
- Ramas de trabajo: `feature/<tema>`, `fix/<tema>`, `docs/<tema>`.
- Mensajes de commit: `<tipo>(<área>): <descripción en imperativo>`
  con tipos `feat | fix | docs | hw | test | chore` y áreas
  `firmware | hardware | mecanica | docs | ensayos`.
- Una etiqueta por entrega: `informe-inicial`, `avance-1`, `avance-2`, `final`.
