# Correcciones pendientes

Detectadas al revisar el Informe de Avance 1 contra el esquemático y los cuadernos del
grupo, el 3-10-2026. El informe entregado ya está corregido; lo que sigue es lo que queda
desalineado en el repositorio.

## 1. Numeración de pines del esquemático (Ariana)

El plano asigna las entradas analógicas y la entrada digital a pines que en la
EDU-CIAA-NXP tienen otra función. Verificado contra
`codigo/documentation/CIAA_Boards/NXP_LPC4337/EDU-CIAA-NXP/EDU-CIAA-NXP v1.1 Board - 2019-01-03 v5r0.pdf`
y contra el mapeo de Firmata, que coinciden.

| Red | Pin en el plano | Esa posición en la placa | Pin correcto |
|---|---|---|---|
| `JOY_B_X` (codo) | P1 3 | RESET | **P1 9** (CH3) |
| `JOY_A_X` (base) | P1 5 | ISP | **P1 11** (CH2) |
| `JOY_A_Y` (hombro) | P1 7 | GNDA | **P1 13** (CH1) |
| `JOY_B_Y` (reserva) | P1 9 | CH3 | sin canal disponible, dejar sin conectar |
| masa analógica | P1 6 | WAKEUP | **P1 8** (o 10/12/14/16/18, todos GNDA) |
| `PINZA_BTN` | P2 31 | GPIO2 | **P2 29** (GPIO0) |
| masa de P2 | P2 29 | GPIO0 | **P2 39** (GND) |

Los cinco PWM están correctos y no hay que tocarlos: P1 35 (`T_FIL3`, SERVO3, muñeca),
P1 36 (`T_FIL1`, SERVO0, base), P1 37 (`T_FIL2`, SERVO2, codo), P1 39 (`T_COL0`, SERVO1,
hombro) y P2 40 (`GPIO8`, SERVO4, pinza).

Tal como está, un potenciómetro queda sobre RESET y otro sobre ISP, y la masa analógica
sobre WAKEUP.

## 2. Tensiones y datos del cajetín del esquemático (Ariana)

`brazo.kicad_sch` sigue con los valores previos al cierre de la alimentación:

- riel `+6V` y conector `J_PWR_6V` → **`+5V`** y **`J_PWR_5V`** (seis apariciones del riel)
- `F1 10A` → **`F1 8A`**
- «Grupo 4» → **«Grupo 3»**

Están corregidos en `esquematico_actualizado.pdf`, que es el plano que usa el Anexo A del
informe, pero no en el archivo de KiCad ni en `esquemático.pdf` / `esquemático.jpg`.
Conviene regenerar los tres desde el `.kicad_sch` una vez aplicados los puntos 1 y 2.

## 3. `diseño_esquemático.ipynb` (Ariana)

- El texto contradice al propio dibujo en los ejes del Joystick A: pone el eje X en el
  pin 7 y el Y en el pin 5; el plano los tiene al revés. Con el punto 1 aplicado, la
  asignación vigente es la de la sección 3.5 del informe.
- La sección de código de colores de los servos dice `+6V` y «las salidas de la tira P2
  de la EDU-CIAA». Las cinco salidas están en P1 salvo la de la pinza, y el riel es de 5 V.
- Asigna el pin 9 a «orientación de la muñeca». La muñeca la calcula el firmware; ese eje
  es reserva y, además, P1 solo expone tres canales ADC.

## 4. `Firmware_Control_bajo_nivel.ipynb` (Lautaro)

- La tabla rotula `CH1` (ADC0_1) como «Joystick 1 eje X». Según el plano, el eje X del
  Joystick A va a CH2 y el eje Y a CH1. Es un intercambio de etiquetas en software.
- Las lecturas quedan: `CH3` → Joystick B eje X (codo), `CH2` → Joystick A eje X (base),
  `CH1` → Joystick A eje Y (hombro).

## 5. `Diseño_de_SW.ipynb` (David)

- Dice que la HAL configura el **SCTimer** para las PWM; `sapi_servo` usa los
  **Timer 1, 2 y 3**, según documenta Lautaro a partir de `sapi_servo.h`. Hay que definir
  cuál se usa y alinear la sección 4.1 del informe, que hoy dice SCTimer.
- Habla de «tubos de ensayo»; en el resto del proyecto la carga es un recipiente con
  líquido. La sección 4 del informe arrastra una mención a «el tubo de ensayo».
- Numera las capas al revés que el informe (llama Capa 4 a la HAL y Capa 1 a `main.c`).
  El orden de exposición es el mismo; solo cambia el número.

## 6. Cobertura del enunciado

- La «interfaz con el usuario / calibración» de la Parte 2 no está cubierta por ninguna
  sección.
- No hay fotografías que documenten el avance del prototipo.
