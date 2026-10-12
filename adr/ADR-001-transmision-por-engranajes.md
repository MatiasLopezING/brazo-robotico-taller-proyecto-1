# ADR-001: Interponer un par de engranajes impresos entre cada servomotor y su articulación

- **Estado**: Aceptada
- **Fecha**: 2026-09-28
- **Autores**: Matias Lopez (02670/0), con revisión del grupo

## Contexto

El proyecto exige un brazo capaz de tomar un recipiente con líquido en un punto y depositarlo en
otro sin desplazar la base (requerimiento 3.1.4, alcance de 32,5 cm) manipulando un recipiente de
145 g (requerimiento 3.1.2).

Los cinco servomotores MG996R **ya estaban adquiridos** antes de cerrar el dimensionamiento, de modo
que su par es un dato fijo y no una variable. La hoja de datos de TowerPro declara 9,4 kg·cm a 4,8 V
y 11,0 kg·cm a 6,0 V; a la tensión de trabajo de 4,89 V la interpolación lineal da **9,52 kg·cm**.

El cálculo estático en el peor caso —brazo totalmente estirado en horizontal— da un par en el hombro
de **11,96 kg·cm**, del que el recipiente aporta el 39 % y el conjunto muñeca-pinza otro 42 %
(`Dimensionamiento_brazo.ipynb`, sección 5). Con un factor de seguridad de 2, el hombro exige
23,92 kg·cm y el codo 11,84.

## Problema

El par que exige el hombro supera en 2,5 veces el que entrega el servomotor adquirido. ¿Cómo se hace
viable el brazo de 32,5 cm sin reemplazar los actuadores?

## Opciones Consideradas

### Opción A — Acortar los eslabones

- **Descripción**: reducir `L1` y `L2` hasta que el par entre en lo que el servomotor da con acople
  directo.
- **Ventajas**: no agrega piezas ni modos de falla; el brazo queda más rígido y más liviano.
- **Desventajas**: el alcance cae a unos 19 cm, con lo que el brazo no puede tomar y depositar en
  dos puntos distintos sin mover la base. Incumple el requerimiento 3.1.4.
- **Evidencia**: el barrido de tamaños de la sección 8 del cuaderno muestra que con eslabones de
  8 cm el alcance es de 24,5 cm y sigue sin verificar a acople directo.
- **Costo**: nulo en dinero; reimprimir las piezas.

### Opción B — Aligerar la estructura

- **Descripción**: reemplazar el perfil de aluminio por fibra de carbono o por una estructura
  calada.
- **Ventajas**: no cambia la cinemática ni el control.
- **Desventajas**: **no resuelve el problema**. Los dos eslabones aportan 1,01 kg·cm de los 11,96,
  el 8,4 % del total. Anularlos por completo dejaría el hombro en 10,95 kg·cm, todavía por encima
  de lo disponible aun sin factor de seguridad.
- **Evidencia**: descomposición del par en el hombro, sección 5 del cuaderno.
- **Costo**: alto en material, nulo en resultado.

### Opción C — Comprar servomotores de mayor par

- **Descripción**: reemplazar los cinco MG996R por unidades de 25 a 35 kg·cm.
- **Ventajas**: solución directa, sin piezas intermedias ni juego mecánico.
- **Desventajas**: los cinco MG996R ya están comprados y se perderían. Los servomotores de ese par
  son más pesados, con lo que el par exigido vuelve a subir, y consumen más corriente, lo que
  obligaría a revisar toda la alimentación.
- **Costo**: el de cinco servomotores nuevos más el tiempo de reposición, contra un presupuesto de
  proyecto de materia.

### Opción D — Par de engranajes rectos impresos entre servomotor y articulación

- **Descripción**: una rueda dentada en el eje del servomotor y otra en el de la articulación, con
  relación `r = z_junta / z_servo`. La articulación recibe `r` veces el par del servomotor y gira
  `1/r` de su recorrido.
- **Ventajas**: aprovecha los servomotores existentes; las piezas se imprimen en PETG; permite
  elegir una relación distinta por articulación, incluso **invertida** donde sobra par y falta
  recorrido.
- **Desventajas**: agrega masa (38 a 77 g por articulación), juego entre dientes que el lazo de
  control no corrige, e invierte el sentido de giro.
- **Evidencia**: con 20:60 en el hombro, el par exigido al servomotor baja de 11,96 a
  **3,99 kg·cm**; con FS 2 son 7,97 contra 9,52 disponibles. La verificación de flexión de Lewis,
  `σ = F/(b·m·Y)` con `Y ≈ 0,32`, da **10,8 MPa** en el piñón de 20 dientes contra 15 MPa
  admisibles en PETG impreso.
- **Costo**: unas dos horas de impresora por juego y el filamento.

## Comparativa Resumida

| Criterio | A: acortar | B: aligerar | C: otros servos | D: engranajes |
|---|---|---|---|---|
| Cumple el alcance de 32,5 cm | no | sí | sí | sí |
| Resuelve el par del hombro | sí | **no** | sí | sí |
| Aprovecha lo ya comprado | sí | sí | **no** | sí |
| Modos de falla que agrega | ninguno | ninguno | ninguno | juego, rotura de diente |
| Costo | nulo | alto | el de 5 servomotores | 2 h de impresora |
| Riesgo | incumple 3.1.4 | no funciona | rehacer la alimentación | depende del barrido real |

## Decisión

Se adopta la **opción D**: un par de engranajes rectos impresos en PETG, módulo 1,5 mm y 12 mm de
ancho de diente, entre cada servomotor y su articulación.

| Articulación | Dientes | Par en la junta | Par en el servo | × FS 2 | Margen | Barrido |
|---|---|---|---|---|---|---|
| Base | 60:30 | 0,97 kg·cm | 1,94 | 3,88 | 145 % | 360° |
| Hombro | 20:60 | 11,96 kg·cm | 3,99 | 7,97 | 19 % | 60° |
| Codo | 20:30 | 5,92 kg·cm | 3,95 | 7,89 | 21 % | 120° |
| Muñeca | 30:20 | 1,62 kg·cm | 2,42 | 4,85 | 96 % | 270° |
| Pinza | directa | — | 0,72 | 1,44 | 561 % | 180° |

## Rationale

La opción B se descarta porque la evidencia muestra que no resuelve el problema: los eslabones son
el 8 % del par. La A lo resuelve pero incumpliendo el requerimiento de alcance. La C lo resuelve a
costa de descartar material ya comprado y de rehacer el diseño eléctrico.

La D intercambia **par por recorrido**, y ese intercambio es casi gratuito en este proyecto por una
razón ajena a la mecánica: el límite de aceleración que impone el líquido ya obligaba a mover el
brazo lento. Los tramos tardan entre 2 y 4 segundos, lo que pide unos 45 °/s, y con 3:1 la
articulación todavía da 120 °/s. **El líquido ya había quitado la velocidad antes de que la
transmisión la cobrara.**

La solución además resultó más barata de lo esperado en piezas: como la base y la muñeca montan el
par invertido, las mismas tres ruedas —20, 30 y 60 dientes— resuelven las cuatro transmisiones.

Se acepta a sabiendas el peor criterio en «modos de falla»: la transmisión agrega juego y la
posibilidad de romper un diente, cosa que el acople directo no tiene. A cambio se obtiene un brazo
que cumple el alcance con los actuadores disponibles.

## Implicaciones

- **Positivas**: el hombro pasa a 19 % de margen y el codo a 21 %; la base gana 360° de barrido y la
  muñeca 270°, suficientes para compensar los 180° que suman hombro y codo; habilita
  [ADR-002](ADR-002-riel-de-5v-sin-convertidor), porque con 3:1 el riel de 5 V alcanza.
- **Negativas**: entre 38 y 77 g adicionales por articulación, ya contabilizados en el cálculo de
  pares; el recorrido del hombro cae de 180° a 60°.
- **Riesgos**:
  - *El juego no lo corrige nadie*, porque el servomotor mide su posición antes de la transmisión.
    **Mitigación**: agujeros de montaje ovalados que permiten acercar los ejes hasta eliminarlo.
  - *Rotura de un diente* deja la articulación sin control. **Mitigación**: módulo 1,5 verificado
    contra el servomotor trabado, tope mecánico que limite la caída y un juego de repuesto impreso.
  - *El reparto supone 180° de barrido del MG996R*, dato del proveedor contra los 120° de la hoja de
    datos. **Mitigación**: es el primer ensayo a ejecutar; si da 120°, cambia la cantidad de dientes,
    no la mecánica.
- **Acciones**:
  - Imprimir y pesar un juego de engranajes para confirmar las masas derivadas de la geometría
    (Matias).
  - Medir el barrido real del servomotor antes de fijar los dientes definitivos (Matias y Lautaro).
  - El firmware trabaja en **ángulos de articulación** y aplica la relación y el cambio de signo en
    la capa más baja (Lautaro y David).

## Consecuencias Observadas

Pendiente de implementación. Las piezas todavía no se imprimieron.

## Alternativas Futuras

Si el ensayo de barrido diera 120° y el hombro quedara con 40° útiles, hay dos caminos: rehacer el
reparto de dientes con relaciones menores, o volver a 6 V mediante un convertidor desde el riel de
+12 V, lo que recupera 1,5 kg·cm y permite bajar la reducción a 2,5:1. La señal que indicaría esto
es el ensayo n.º 1 de la lista de [Estado y pendientes](Estado-y-pendientes).

## Referencias

- `Dimensionamiento_brazo.ipynb`, secciones 5, 6 y 9 — cálculo de pares, reparto de dientes y
  verificación de Lewis.
- TowerPro, MG996R Digital Servo, hoja de datos del fabricante.
- Informe de Avance 1, sección 4.7 y Anexo C.

## Historial

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-09-28 | Creación | Matias Lopez |
| 2026-10-02 | Se confirma el reparto 20:60 / 20:30 / 30:20 / 60:30 tras fijar la geometría | Matias Lopez |
