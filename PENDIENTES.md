# Correcciones pendientes

---

# ⚠ NUEVO — Revisión del PCB antes de fabricar (4-11-2026)

Detectado al revisar el **netlist real de `brazo/brazo.kicad_pcb`**, que es lo que se
fabrica, contra el mapa de periféricos de sAPI
(`codigo/libs/sapi/documentation/PeripheralMap_EDU-CIAA-NXP.txt`) y la documentación de la
placa. Los dos primeros puntos hay que corregirlos **antes de subir el `.kicad_pro`**.

## N1. El cuarto eje analógico está cableado a un pin sin conversor (Ariana) — BLOQUEANTE

En la placa, `JOY_B_Y` va a **P1 pin 35**, que es `T_FIL3`: una entrada digital de teclado.
La EDU-CIAA expone **tres** canales analógicos —`CH1` en P1 13, `CH2` en P1 11 y `CH3` en
P1 9— más el pin 15, que es la salida del DAC y que sAPI permite remultiplexar como `CH0`.
El pin 35 no puede leer una tensión: ese joystick no se lee nunca.

Confirmado por dos fuentes independientes: el mapa de periféricos de sAPI y
`EDU-CIAA-NXP Mapeo de pines Firmata4CIAA v2.pdf`, que coinciden en que P1 35 es `TFIL3`.

Dos salidas posibles:

- Devolver `JOY_B_Y` al **P1 pin 15**, que es lo que fija
  [ADR-007](Wiki) y lo que hoy está libre en la placa. Es un ruteo corto.
- Dejar el cuarto eje **sin conectar**, que es legítimo porque todavía figura como decisión
  abierta si se usa o no.

El resto del cambio de pines está **correcto** y no hay que tocarlo: `PWM_MUÑECA` en P2 31
es `GPIO2` = `SERVO8` de `sapi_servo`, y `PINZA_BTN` en P2 29 es `GPIO0`, que además
corrige el error viejo de llamar `GPIO0` al pin 31.

## N2. El capacitor del bus no entra en su huella (Ariana)

`C1` es **2200 µF / 16 V** y tiene asignado `CP_Radial_D8.0mm_P5.00mm`. Un electrolítico de
ese valor y esa tensión mide en la realidad **12,5 a 16 mm de diámetro**; 8 mm corresponde
a uno de 220 a 470 µF. El paso de 5 mm entre patas puede cerrar, pero el cuerpo se
superpone con lo que tenga al lado.

Corregir a `CP_Radial_D12.5mm_P5.00mm` o `D13.0mm` y volver a verificar separaciones. Es
además lo que pide el TP3, que exige completar el BOM con la huella que corresponde **según
las dimensiones físicas de cada componente**.

## N3. La masa analógica quedó en una red huérfana (Ariana)

P1 pin 7 es `GNDA` y en el PCB está asignado a una red llamada literalmente `<NO NET>`, con
un solo pad. No es un problema eléctrico —los joysticks toman su masa de `GND`, que sí está
bien conectada— pero es una red suelta con nombre inválido que el DRC va a marcar.

## N4. El cuaderno del PCB describe un cambio que la placa no tiene (Ariana)

`DIseño_PCB.ipynb` dice que `PWM_BASE` se trasladó al P2 pin 35. En la placa **no se
movió**: sigue en P1 pin 36, que es `T_FIL1` = `SERVO0` y es lo correcto. Menos mal, porque
el P2 pin 35 es `GPIO6` y no es salida de servo ni de PWM en sAPI.

Hay que corregir el texto del cuaderno, porque el informe de avance describe la placa a
partir de él y heredaría el error.

## N5. El ancho de pista del bus de +5 V no alcanza para la corriente (Ariana)

Todo el ruteo se hizo con pistas de **0,7 mm**: 168 de los 172 segmentos. Con 35 um de
cobre (1 oz, lo habitual) y la formula de IPC-2221 para conductores externos, una pista de
0,7 mm admite **1,9 A** con 10 C de elevacion y **2,6 A** con 20 C.

El tramo comun del riel de +5 V lleva **4,74 A en regimen** y **6,22 A** en el pico del
arranque escalonado. Falta mas del doble de seccion.

Lo que hace falta es del orden de **2,3 mm** de ancho en ese tramo (o duplicarlo en las dos
caras). No afecta a las lineas de senal: las PWM y las entradas analogicas con 0,7 mm
sobran.

Conviene ademas crear una **clase de red** propia para `+5V` y `GND`, con su ancho y su
separacion. Hoy el proyecto tiene una sola clase, `Default`, con `track_width = 0.2`, y los
0,7 mm reales se fijaron a mano traza por traza: cualquier retoque futuro vuelve a salir en
0,2 mm sin avisar.

## N6. Cuatro astillas de pista de 0,2 mm sobre `+5V`

Quedaron cuatro segmentos de 0,2 mm de ancho y entre **0,01 y 0,1 mm de largo** (en
110.18,48.8 / 129.74,48.9 y dos mas en el mismo punto, dos en F.Cu y dos en B.Cu). Son
restos del ruteo, no conducen nada, y son justamente la clase de 0,2 mm de N5 asomando. El
DRC y el fabricante los informan como astillas de cobre. Se borran y listo.

> N5 y N6 se detectaron al escribir la seccion 4.8 del informe de avance 2, y ya estan
> documentados ahi junto con N1, N2 y N3, de modo que la catedra ve que el grupo los
> encontro solo. N4 no esta en el informe porque es un error de documentacion interna, no
> del diseno.

---

# Pendientes anteriores que siguen abiertos

Lo que sigue viene de la revisión del 3-10-2026. **Ya se resolvieron y se quitaron de esta
lista**: la asignación de las tres entradas analógicas a canales ADC reales, el pulsador de
la pinza en P2 29, la masa de P2, el conector `J_PWR_6V`, el fusible de 10 A y el cajetín
con «Grupo 4».

## 1. Símbolos `+6V` sueltos en el esquemático (Ariana)

`brazo.kicad_sch` conserva **seis símbolos de alimentación `+6V`** colocados en la hoja. No
llegan al PCB —el netlist de la placa solo tiene `+5V`, `+3.3V` y `GND`— pero aparecen en
el dibujo, y el Anexo A del informe muestra ese dibujo. Contradice toda la sección de
alimentación, que es un riel único de 5 V.

## 2. `diseño_esquemático.ipynb` (Ariana)

- Conserva una mención a `+6V` y tres a «la tira P2 de la EDU-CIAA» para las salidas de los
  servos. Cuatro de las cinco salidas están en P1.
- Conserva `ANALOG_GND` y `GPIO_GND` como nombres de red, que no son los del plano actual.

## 3. `Firmware_Control_bajo_nivel.ipynb` (Lautaro)

La tabla rotula `CH1` como «Joystick 1 eje X». Según el plano vigente, las lecturas son
`CH3` → `JOY_A_X`, `CH2` → `JOY_A_Y` y `CH1` → `JOY_B_X`. Es un intercambio de etiquetas en
software, y hay que alinearlo antes de escribir el firmware o las lecturas salen cruzadas.

## 4. `Diseño_de_SW.ipynb` (David)

- Dice que la HAL configura el **SCTimer** para las PWM; `sapi_servo` usa los **Timer 1, 2 y
  3**, según documenta Lautaro a partir de `sapi_servo.h`. Hay que definir cuál se usa y
  alinear la sección correspondiente del informe.
- Habla de «tubos de ensayo»; en el resto del proyecto la carga es un recipiente con
  líquido.
- Numera las capas al revés que el informe. El orden de exposición es el mismo; solo cambia
  el número.

## 5. Cobertura del enunciado

- **La interfaz con el usuario de la Parte 2 sigue sin cubrirse.** El canal físico ya está
  documentado —el micro-USB de depuración, que sAPI expone como `UART_USB`, sin consumir
  ningún pin—; lo que falta es definir el protocolo y escribir las dos puntas.
- **No hay registro fotográfico del avance**, que el requerimiento 3.4 pide. Queda cubierto
  en parte con la foto de los componentes comprados y el ensayo de barrido del servo
  previsto para el jueves 5-11.
