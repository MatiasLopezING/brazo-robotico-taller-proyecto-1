# Revisión del circuito impreso — 6-11-2026

Hecha sobre `brazo.kicad_pcb` leyendo el archivo directamente, sin abrir KiCad.
Acompaña a `brazo_revisado.kicad_pcb`, que trae aplicados los tres cambios
mecánicos del final de este documento.

---

## 1. Cortocircuitos en las tiras de pines — BLOQUEANTE

**42 islas de P1 y P2 están invadidas por una pista de otra red.** No son
holguras escasas: son solapamientos de hasta 0,30 mm, o sea contacto.

La causa es geométrica. Las islas de P1 y P2 miden **2,0 mm** y el paso es
**2,54 mm**, de modo que entre isla e isla quedan **0,54 mm** libres. Las
pistas son de **0,7 mm**. No entran. Hoy el ruteo cruza por dentro del campo
de islas de las dos tiras.

No hay salida por el lado del ancho: para pasar entre dos islas haría falta una
pista de 0,3 mm con 0,12 mm de separación a cada lado, que está por debajo de
lo que resuelve el proceso del taller. **Las pistas tienen que salir de adentro
de las tiras y rodear el conector.**

Esto es lo único de la lista que no se puede postergar: una placa con las
pistas cortocircuitando los pines del conector no funciona ni fabricándola.

### Listado completo

```
F1 — 1 islas invadidas
   pin  2  ( 70.50,  57.23)  red Net-(J_PWR_5V1-Pin_1) invadida por GND              -0.05 mm

P1 — 19 islas invadidas
   pin  9  (143.00, 103.72)  red /JOY_A_X         invadida por /PWM_HOMBRO      -0.20 mm
   pin 10  (145.54, 103.72)  red sin conexion     invadida por /PWM_HOMBRO      -0.20 mm
   pin 12  (145.54, 106.26)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 14  (145.54, 108.80)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 16  (145.54, 111.34)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 18  (145.54, 113.88)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 20  (145.54, 116.42)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 22  (145.54, 118.96)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 24  (145.54, 121.50)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 26  (145.54, 124.04)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 28  (145.54, 126.58)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 30  (145.54, 129.12)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 32  (145.54, 131.66)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 33  (143.00, 134.20)  red sin conexion     invadida por /PWM_BASE        -0.08 mm
   pin 34  (145.54, 134.20)  red sin conexion     invadida por /PWM_HOMBRO      -0.05 mm
   pin 35  (143.00, 136.74)  red /JOY_B_Y         invadida por /PWM_BASE        -0.20 mm
   pin 36  (145.54, 136.74)  red /PWM_BASE        invadida por /PWM_HOMBRO      -0.05 mm
   pin 38  (145.54, 139.28)  red sin conexion     invadida por /PWM_HOMBRO      -0.09 mm
   pin 40  (145.54, 141.82)  red sin conexion     invadida por /PWM_HOMBRO      -0.20 mm

P2 — 22 islas invadidas
   pin  1  ( 70.30,  93.56)  red +3.3V            invadida por GND              -0.30 mm
   pin  2  ( 72.84,  93.56)  red sin conexion     invadida por GND              -0.30 mm
   pin  3  ( 70.30,  96.10)  red sin conexion     invadida por GND              -0.06 mm
   pin  4  ( 72.84,  96.10)  red sin conexion     invadida por GND              -0.06 mm
   pin 19  ( 70.30, 116.42)  red sin conexion     invadida por /PWM_MUÑECA      -0.30 mm
   pin 20  ( 72.84, 116.42)  red sin conexion     invadida por /PWM_MUÑECA      -0.30 mm
   pin 21  ( 70.30, 118.96)  red sin conexion     invadida por /PWM_MUÑECA      -0.12 mm
   pin 22  ( 72.84, 118.96)  red sin conexion     invadida por /PWM_MUÑECA      -0.06 mm
   pin 25  ( 70.30, 124.04)  red sin conexion     invadida por /PWM_PINZA       -0.06 mm
   pin 26  ( 72.84, 124.04)  red sin conexion     invadida por /PWM_PINZA       -0.06 mm
   pin 27  ( 70.30, 126.58)  red GND              invadida por /PWM_PINZA       -0.30 mm
   pin 28  ( 72.84, 126.58)  red sin conexion     invadida por /PWM_PINZA       -0.30 mm
   pin 29  ( 70.30, 129.12)  red /PINZA_BTN       invadida por GND              -0.30 mm
   pin 30  ( 72.84, 129.12)  red sin conexion     invadida por GND              -0.30 mm
   pin 31  ( 70.30, 131.66)  red /PWM_MUÑECA      invadida por GND              -0.30 mm
   pin 32  ( 72.84, 131.66)  red sin conexion     invadida por GND              -0.30 mm
   pin 33  ( 70.30, 134.20)  red sin conexion     invadida por /PWM_PINZA       -0.06 mm
   pin 34  ( 72.84, 134.20)  red sin conexion     invadida por /PWM_PINZA       -0.06 mm
   pin 36  ( 72.84, 136.74)  red sin conexion     invadida por /PWM_PINZA       -0.05 mm
   pin 38  ( 72.84, 139.28)  red sin conexion     invadida por /PWM_PINZA       -0.05 mm
   pin 39  ( 70.30, 141.82)  red sin conexion     invadida por GND              -0.30 mm
   pin 40  ( 72.84, 141.82)  red /PWM_PINZA       invadida por GND              -0.30 mm
```

---

## 2. El 3,3 V da una vuelta larga

La red `+3.3V` tiene **332 mm de pista**, más que el `+5V` (156 mm), para
alimentar cuatro islas: P1-1 (143,0; 93,6), P2-1 (70,3; 93,6),
J_JOY_A1-1 (88,5; 150,5) y J_JOY_B1-1 (115,8; 150,5).

Un árbol que las una por el camino más corto mide del orden de **150 mm**, así
que el recorrido actual es **2,2 veces** el mínimo. Conviene revisarlo cuando se
rehaga el ruteo del punto 1, porque buena parte de esa vuelta pasa justamente
por dentro de las tiras.

No es un problema eléctrico —los joysticks consumen menos de 1 mA— pero es
cobre y espacio que hoy estorba.

---

## 3. Ancho de pista del bus de potencia

Todo el ruteo está en **0,7 mm**. Con 35 µm de cobre y la fórmula de IPC-2221
para conductores externos, eso admite del orden de 1,9 A con 10 °C de elevación
y 2,6 A con 20 °C. El tramo común del riel de +5 V lleva **4,74 A en régimen** y
**6,22 A** en el pico del arranque escalonado, de modo que necesita unos
**2,3 mm** de ancho.

Conviene además crear una **clase de red** propia para `+5V` y `GND`. Hoy el
proyecto tiene una sola clase, `Default`, con `track_width = 0,2 mm`, y los
0,7 mm reales se fijaron a mano traza por traza: cualquier retoque futuro vuelve
a salir en 0,2 mm sin avisar.

---

## 4. Pendientes de esquemático

Estas dos no se pueden tocar desde el archivo de placa.

- **`JOY_B_Y` en P1 pin 35**, que es `T_FIL3` y no tiene conversor
  analógico-digital. La señal vuelve al pin 15. Es bloqueante.
- **`GNDA` (P1 pin 7) en una red suelta** llamada literalmente `<NO NET>`. Hay
  que unirla a `GND`.

---

## 5. Bornera de tres bocas

Recomendada por la cátedra: una entrada para 3,3 V, otra para 5 V y otra para
tierra, en lugar de la bornera de dos bocas actual (`J_PWR_5V1`). Implica
colocar la huella y rerutear la alimentación, así que va junto con el punto 1.

---

## Lo que trae `brazo_revisado.kicad_pcb`

Tres cambios mecánicos, ninguno de criterio de diseño. **Hay que abrirlo en
KiCad, rellenar las zonas (tecla B) y correr el DRC antes de confiar en él.**

1. **Capas invertidas.** Las pistas pasaron de F.Cu a B.Cu y el relleno de GND
   las acompañó. La placa queda con el cobre en la cara inferior (azul) y los
   puentes en la superior (rojo), que es como se lee una placa de una sola faz.
   Quedan 159 segmentos en B.Cu y 4 en F.Cu.
2. **Puentes enderezados.** Los cuatro tramos que estaban hechos con varios
   segmentos quebrados pasaron a ser un único segmento recto entre sus extremos,
   que es lo único que se puede hacer con un trozo de alambre. Verifiqué que
   ninguno de los cuatro pasa a menos de 0,25 mm de una isla de otra red.

   | Red | De | A | Largo |
   |---|---|---|---|
   | GND | (147,7; 89,1) | (139,6; 55,9) | 34,2 mm |
   | +5V | (110,2; 48,9) | (129,7; 48,9) | 19,5 mm |
   | PWM_BASE | (120,5; 82,5) | (138,0; 131,0) | 51,6 mm |
   | PWM_CODO | (139,3; 138,5) | (140,8; 78,5) | 60,0 mm |

   Los dos últimos son alambres largos que cruzan media placa. Funcionan, pero
   si al rehacer el ruteo del punto 1 se pueden acortar, mejor.
3. **Astillas borradas.** Cuatro restos de ruteo de 0,2 mm de ancho y entre
   0,01 y 0,1 mm de largo sobre la red `+5V`, que el verificador informa como
   astillas de cobre.

Lo que **no** trae: el ruteo del punto 1, la bornera del punto 5 y las
correcciones de esquemático del punto 4. Eso es trabajo de KiCad.
