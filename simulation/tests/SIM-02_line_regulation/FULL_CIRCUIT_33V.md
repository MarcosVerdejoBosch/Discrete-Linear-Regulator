# Selector-off full-circuit verification

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

## Pilot, 17 September 2026

Derived from SIM-02_full_line_5V_pilot.asc. R62 (selector gate feed)
is removed to represent an open selector input; R60 remains connected
from the gate of U8 to ground. No protection stages are removed.
LTspice designators differ from the PCB: U8 is the selector MOSFET.
The load is 3.3 ohm, the source 8 V, temperature 27 C, duration 80 ms,
maximum step 2 us. The switch connects at 5 ms.

The unmodified divider uses RFB1=15k, R33=14.5k, RFB2=25k.
The final 70--80 ms average is 3.391257663 V, with 0.294447 mV
peak-to-peak variation. The difference from the preceding 10 ms
average is -0.000049366 mV. Enable remains above 7.2255 V.
This confirms the simulated operating point at these conditions;
it is not a calibrated 3.3 V result or a hardware measurement.

Pilot inputs and results are preserved in results/full_circuit_33V,
with SHA-256 hashes in pilot_manifest.json. Scripts prepare_33V.py
and inspect_33V.py reproduce preparation and extraction.

KiCad labels RV1 and RV2 as R_Potentiometer without numeric values.
The user reports approximately 13k and 25k respectively. Clarification
is pending on whether these are adjusted wiper-to-terminal resistances
or total pot resistances. No simulated recalibration has been made:
the test retains R33=14.5k and RFB2=25k and therefore must not be
described as reproducing those reported hardware adjustments.

## Line-change run

SIM-02_full_line_33V_changes.asc retains this divider adjustment.
After 80 ms at 8 V, the source visits 6, 7, 8, 9, 10 and 11 V,
with 0.1 ms ramps and 40 ms intervals. Final 10 ms windows are
compared with the preceding windows. The repeated 8 V point checks
agreement with the initial operating point. Completion and extracted
results must be checked with analyze_33V_changes.py before reporting.

## Completed result

The 320 ms run completed. Output averages are 3.391970312 V at 6 V
and 3.390493111 V at 11 V: signed endpoint slope -0.295440 mV/V.
All final windows retain enable above 5 V; adjacent-window average
differences are below 0.001 mV. Repeated 8 V averages agree within
0.004 uV (numerical agreement, not an accuracy claim).
The uncalibrated curve is stored as docs/figures/SIM-02_full_line_selector_off
in PDF, SVG and PNG; the report includes only a concise paragraph.
Input files, raw results and hashes are in results/full_circuit_33V.

Update: the user authorized adjustment and confirmed sufficient potentiometer ranges. Calibration is now completed; see CALIBRATION.md. Earlier uncalibrated results above retain their original meaning.
