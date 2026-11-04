# brazo_description

Modelo **URDF** del brazo robótico teleoperado del Grupo 3 — Taller de Proyecto I (E0306), UNLP.

El URDF es el formato con el que la industria describe un robot: lo leen ROS 2, MoveIt, Gazebo,
MATLAB (`importrobot`), PyBullet, Isaac y RoboDK. Este paquete lo usa para **ver y mover el brazo en
RViz 2** antes de que exista el prototipo.

| Qué hay | Dónde |
|---|---|
| El modelo | `urdf/brazo.urdf` |
| El generador del modelo | `scripts/genera_urdf.py` |
| La verificación contra los cuadernos | `scripts/verifica_urdf.py` |
| La tarea completa como nodo ROS 2 | `scripts/tarea.py` |
| Lanzador de RViz 2 | `launch/display.launch.py` |

## El modelo

Cuatro articulaciones de giro más la pinza, con los ángulos **en la misma convención que los
cuadernos de cálculo**, de modo que el valor de cada junta es directamente el ángulo documentado:

| Junta | Eje | Qué mide | Ventana (ADR-010) |
|---|---|---|---|
| `base` | z | giro del brazo entero | −180° a 180° |
| `hombro` | y | desde la vertical | 50° a 110° |
| `codo` | y | desde el eslabón anterior | 0° a 120° |
| `muneca` | y | desde el eslabón anterior | −108° a 40° |
| `dedo_izq` / `dedo_der` | y | cierre de cada mordaza (`mimic`) | 0° a 62° |

Eslabones de 120, 120 y 85 mm; hombro a 190 mm de la mesa (100 mm de caja base + 90 mm de
pedestal). El enlace `punta` es el punto que calculan los cuadernos, entre las dos mordazas.

**El URDF no inventa cotas**: `genera_urdf.py` las toma de `brazo_parametros.py`, en la raíz del
repositorio, que es la única fuente de cotas del proyecto. Si una cota cambia, se cambia ahí y se
vuelve a generar. `verifica_parametros.py`, también en la raíz, comprueba que ninguna de las otras
copias —el nodo, la página HTML, los cuadernos— haya quedado atrasada.

**No lleva bloques `<inertial>`.** Las piezas todavía no están modeladas en 3D, así que no hay masas
ni tensores de inercia medidos, y no se inventan. El modelo sirve para visualizar, verificar
cinemática y planificar; para simular dinámica en Gazebo hay que agregarlos.

## Verificación

```
python3 scripts/verifica_urdf.py
```

Recorre la cadena del URDF con un lector propio —solo `xml` y `numpy`, sin ROS— y compara contra la
fórmula de la cinemática directa en 5 000 configuraciones al azar. Si están instalados, cruza además
contra `yourdfpy` y contra el *Robotics Toolbox* de Peter Corke, que leen el archivo por su cuenta.
Las tres comparaciones dan del orden de 10⁻¹⁶ m, que es ruido de punto flotante.

## Cómo verlo

Hace falta ROS 2 (probado con Jazzy; Humble funciona igual). En Windows, dentro de WSL 2 con Ubuntu.

```bash
mkdir -p ~/ros2_ws/src && cp -r brazo_description ~/ros2_ws/src/
cd ~/ros2_ws && colcon build --packages-select brazo_description
source install/setup.bash
ros2 launch brazo_description display.launch.py
```

Se abre RViz 2 con el brazo y una ventana de sliders, uno por articulación, con los topes del URDF
ya puestos: no deja salirse de las ventanas de recorrido.

Para ver la tarea completa —bajar, cerrar, levantar, girar la base 47°, bajar, abrir— en vez de los
sliders:

```bash
ros2 launch brazo_description display.launch.py modo:=tarea
```

El nodo `tarea.py` resuelve **cada cuadro con la cinemática inversa cerrada**, a radio constante y
con la pinza horizontal. No es una animación dibujada: si una pose no cerrara dentro de las ventanas,
el nodo lo avisa al arrancar.

## Sin ROS

El URDF se usa igual sin instalar nada de ROS:

```python
import yourdfpy                       # pip install yourdfpy
r = yourdfpy.URDF.load('urdf/brazo.urdf')
r.update_cfg({'hombro': 1.6, 'codo': 1.1, 'muneca': -1.2})
r.show()
```

En MATLAB, con la Robotics System Toolbox: `robot = importrobot('brazo.urdf'); show(robot)`.

## Lo que falta

1. **Mallas de las piezas reales.** Hoy cada eslabón es un prisma de dibujo; cuando estén los STL
   del modelado 3D se reemplazan las geometrías `<box>` por `<mesh>` y el modelo pasa a servir para
   verificar interferencias.
2. **Masas e inercias**, que son lo que habilita Gazebo y el cálculo dinámico.
3. **`ros2_control`**, si alguna vez se quiere mover el brazo real desde ROS 2. Hoy el control vive
   en la EDU-CIAA, que no corre ROS: haría falta un nodo puente por puerto serie.

## Referencias

- Wiki del proyecto: páginas *Cinemática directa*, *Cinemática por Denavit-Hartenberg*,
  *Jacobiano y singularidades* y *Modelo URDF*.
- `Cinematica_brazo.ipynb` y `Jacobiano_brazo.ipynb` en la raíz del repositorio.
