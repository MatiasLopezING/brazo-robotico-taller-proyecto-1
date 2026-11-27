# PCB del brazo robótico

Placa de una cara para el brazo de 5 servos teleoperado con joysticks, montada
sobre la EDU-CIAA. Proyecto de KiCad: abrir `brazo.kicad_pro`.

| archivo | contenido |
|---|---|
| `brazo.kicad_pro` | proyecto y reglas de diseño |
| `brazo.kicad_sch` | esquemático |
| `brazo.kicad_pcb` | placa |
| `brazo.kicad_dru` | regla propia: 0,5 mm entre pads vecinos |
| `fabricacion/brazo-B_Cu.pdf` | capa bottom con el borde, para imprimir en el ATEI |

## Reglas de diseño (cátedra)

- Pads de la EDU-CIAA (P1, P2): ovalados de 2,0 × 1,5 mm
- Pads del resto de los pines: redondos de 2,0 mm
- Agujeros: 0,7 mm
- Pistas: 1,0 mm como mínimo (señal 1,0; +5 V 1,5 y 2,0)
- Aislamiento: 0,7 mm entre pistas, vías y plano de masa; 0,5 mm entre pads vecinos

## Construcción

- Todo el ruteo está en la cara bottom (B.Cu), con plano de masa.
- En la cara top (F.Cu) sólo hay puentes de alambre, rectos y de agujero a
  agujero: uno para PWM_HOMBRO y tres cortos de masa.
- Las huellas están modificadas a propósito: se quitaron los pines de P1 y P2
  que no se usan. **No actualizarlas desde la biblioteca**, porque volverían
  los pines quitados. Por eso el DRC da advertencias `lib_footprint_mismatch`.
