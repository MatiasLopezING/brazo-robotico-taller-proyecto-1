# brazo_control

Control del brazo robótico del Grupo 3 — Taller de Proyecto I (E0306), UNLP.

El paquete expone el brazo **como lo expone un robot industrial**: por la acción
`control_msgs/FollowJointTrajectory`, que es lo que hablan los drivers de ABB, UR o Fanuc, lo que
consume MoveIt y lo que implementa `joint_trajectory_controller`. Encima de esa interfaz se agregan
las funciones que el proyecto necesita: ir a un punto resolviendo la cinemática inversa, memorizar
poses y reproducirlas.

## Arquitectura

```
  demo.py  ──ir_a_punto──►  planificador  ──FollowJointTrajectory──►  controlador  ──►  /joint_states
  (cliente)                 (inversa +                                (hoy simula;            │
                             trayectoria)                              mañana, hardware)      ▼
                                                                                      robot_state_publisher
                                                                                           → RViz 2
```

La separación no es decorativa: **debajo del controlador hoy hay una simulación cinemática y mañana
hay un puente serie a la EDU-CIAA o un `ros2_control`**. Cuando eso pase, el planificador, la
demostración y RViz no se tocan, porque todos hablan la interfaz estándar.

| Nodo | Qué hace |
|---|---|
| `controlador` | acción `follow_joint_trajectory`, publica `/joint_states`. Revisa la trayectoria **entera antes de aceptarla** |
| `planificador` | acción `ir_a_punto` y servicios `resolver_inversa`, `memorizar_pose`, `ir_a_pose` |
| `demo` | cliente que corre la tarea completa pidiendo puntos; no sabe nada de cinemática |

| Módulo | Qué contiene |
|---|---|
| `cinematica.py` | directa, inversa cerrada, ventanas y guarda. Sin ROS ni numpy: se prueba con pytest |
| `perfil.py` | el perfil de quinto orden y el tiempo mínimo por tramo |

## Las tres decisiones que están implementadas

**Movimiento guardado.** El controlador revisa cada punto de la trayectoria contra las ventanas de
recorrido (ADR-010) y contra la guarda de la caja base **antes de aceptar la meta**, y la rechaza
entera si alguno no pasa. En la taxonomía del control supervisor esto es *guarded motion*: el
operador manda y el sistema no ejecuta lo que lo dañaría.

**Rechazar, no saturar.** Si el punto pedido no es alcanzable, la acción se aborta con el motivo
—`fuera de alcance`, `fuera de ventana: hombro`, `el brazo chocaría la caja`— y el brazo se queda
donde está (ADR-011). No se proyecta al borde: el borde es irregular, parte lo fija la caja y parte
el tope del hombro.

**Se memorizan ángulos, no coordenadas.** Reproducir una pose guardada no necesita inversa, no puede
fallar por alcance y no arrastra el error del modelo. La inversa sirve para *calcular* un destino;
lo que se guarda es el resultado (`config/poses.yaml`).

## Trayectorias, no sólo caminos

Un camino es una secuencia de puntos; una trayectoria es ese camino con marca temporal, y tiene que
ser suave. Cada movimiento se interpola con el **polinomio de quinto orden**
`s(t) = 10t³ − 15t⁴ + 6t⁵`, que arranca y termina con velocidad y aceleración nulas.

La duración, si no se pide una, es **la mínima que respeta los dos topes**: la aceleración de la
punta —0,98 m/s², el supuesto cuasi-estático sobre el que está calculado todo el par— y la velocidad
de cada articulación, que no son iguales entre sí. Si se pide una duración más corta que esa mínima,
el movimiento se rechaza y dice cuál es el mínimo.

## Cómo correrlo

```
cd ~/ros2_ws && colcon build --packages-select brazo_interfaces brazo_description brazo_control && source install/setup.bash
```

```
ros2 launch brazo_control control.launch.py
```

Se abre RViz con el brazo. Desde otra terminal:

```
ros2 action send_goal /ir_a_punto brazo_interfaces/action/IrAPunto "{punto: {x: 0.20, y: 0.14, z: 0.07}, alfa_grados: 90.0, duracion_s: 0.0}" --feedback
```

```
ros2 service call /resolver_inversa brazo_interfaces/srv/ResolverInversa "{punto: {x: 0.40, y: 0.0, z: 0.07}, alfa_grados: 90.0}"
```

La segunda devuelve `alcanzable: false, motivo: 'fuera de alcance'`, que es el comportamiento que se
quiere ver: el sistema explica por qué no puede.

Para memorizar la pose actual y volver a ella más tarde:

```
ros2 service call /memorizar_pose brazo_interfaces/srv/MemorizarPose "{nombre: entrega}"
```

```
ros2 service call /ir_a_pose brazo_interfaces/srv/IrAPoseMemorizada "{nombre: entrega, duracion_s: 0.0}"
```

Y la tarea completa, automatizada:

```
ros2 launch brazo_control control.launch.py demo:=true
```

## Pruebas

```
colcon test --packages-select brazo_control && colcon test-result --verbose
```

Ocho pruebas sin ROS: los casos de control de la cinemática directa, que la inversa deshace a la
directa en todo el espacio alcanzable, que nunca hay dos ramas, que cada frontera informa su propio
motivo, la pose que mete la muñeca en la caja con los cuatro ejes en ventana, y que el perfil y el
tiempo mínimo respetan los topes de aceleración y de velocidad.

## Lo que falta

1. **El puente al hardware**: un `hardware_interface` de `ros2_control` que hable con la EDU-CIAA por
   puerto serie, o un nodo puente equivalente. Es lo que reemplaza la simulación del controlador.
2. **La pinza**, que hoy se publica abierta y fija: abrir y cerrar es del firmware, y acá haría falta
   un servicio más.
3. **Encadenar tramos** en una sola trayectoria en vez de un movimiento por meta, para que la
   demostración no se detenga entre pasos.
