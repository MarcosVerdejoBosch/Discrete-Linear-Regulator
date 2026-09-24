# Shared-divider calibration

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

The user confirmed that both potentiometers can be adjusted and their
purchased ranges are sufficient. The earlier approximate 13k/25k values
are not fixed constraints. No additional hardware action is needed to
prepare the simulated calibration.

Calibration conditions: 8 V source, 27 C, 5 ohm load for 5 V and 3.3 ohm
for 3.3 V (approximately 1 A in either mode). Both modes must retain
the same R33 and RFB2 settings; RFB1 remains 15k. The selector is on
for 5 V and off for 3.3 V. R33 corresponds to the first adjustable
divider resistance and RFB2 to the switched divider resistance.

Each iteration runs the complete circuit for 80 ms, maximum time step
2 us, with the input switch closed at 5 ms. Output means use 70--80 ms;
the preceding 10 ms provides a settling check. Scripts and each
iteration's raw/log/net/asc files and hashes are preserved under
results/calibration. These are simulated equivalent resistances, not
measurements of the installed potentiometers.

Existing line-regulation curves retain their original adjustments.
Calibration at 8 V does not automatically validate those same numerical
line-regulation results for the new divider settings.

## Verified final adjustment

Iteration 02: R33=14846.5 ohm and RFB2=28759.8 ohm, identical in both
selector states; RFB1 remains 15k. Both transient runs completed.

| Mode | Mean output (V) | Final-window ripple (mV p-p) |
|---|---:|---:|
| 5 V | 5.0000053743 | 0.28753 |
| 3.3 V | 3.3000000864 | 0.29635 |

The differences between consecutive 10 ms means are below 0.001 mV;
enable remains above 7.226 V. Numerical digits document the extracted
averages and do not imply equivalent hardware accuracy. Load currents
are approximately 1 A. Calibration is at 8 V input and 27 C only.

Use SIM-02_cal_02_5V.asc and SIM-02_cal_02_33V.asc as the calibrated
pilot configurations. selected.json records the adopted iteration.
Next: rerun line regulation with these divider settings, then load regulation.

Calibrated line sweeps are now completed; see CALIBRATED_LINE.md. Next: load regulation.
