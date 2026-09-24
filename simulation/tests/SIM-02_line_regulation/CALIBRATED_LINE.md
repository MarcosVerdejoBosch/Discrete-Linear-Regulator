# SIM-02: calibrated full-circuit line regulation

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

## Conditions

Both modes use the verified calibration (R33=14846.5 ohm,
RFB2=28759.8 ohm, RFB1=15k), at 27 C. Loads: 5 ohm for 5 V and
3.3 ohm for 3.3 V. These are resistive loads, approximately 1 A,
not constant-current sources. No divider readjustment between points.
All regulator and protection stages remain present.

Each run starts with an 8 V source and connects the input switch at
5 ms. At 80 ms the source begins visiting 6, 7, 8, 9, 10 and 11 V.
Each change takes 0.1 ms; successive changes are separated by 40 ms.
Run duration: 320 ms; maximum time step: 2 us. The voltage axis is
the ideal source before the series input switch, not the voltage at
the regulator input after its switch and protection components.

Use calibrated_line.py prepare to generate the two schematics from
SIM-02_cal_02_5V.asc and SIM-02_cal_02_33V.asc. Run the resulting
SIM-02_calibrated_line_5V.asc and SIM-02_calibrated_line_33V.asc in LTspice.
Then run calibrated_line.py inspect and calibrated_line.py plot.

## Acceptance and extraction

Extraction requires a completed log and raw data extending to 320 ms.
Each point uses a time-weighted average of its final 10 ms. Require
the difference from the preceding 10 ms mean to be below 0.001 mV
and enable above 5 V throughout the final window. The initial and
repeated 8 V means must agree within 1 uV. These are numerical
consistency checks, not physical accuracy specifications.

Line regulation is the magnitude of the endpoint slope in mV/V.
Output-window extrema and maximum nominal deviation use the six
sampled mean voltages; they do not establish statistical tolerance
limits, unsampled extrema, temperature performance or startup at
every input voltage. Figures connect sampled means without smoothing.

## Traceability

results/calibrated_line/preparation.json records inputs and changes.
metrics.json records averages, settling checks, signed slopes, input
after the switch, load current and hashes of archived asc/net/log/raw.
Earlier reduced and uncalibrated tests remain in their original
result directories; the report will present the calibrated results
after the two runs pass the checks above.

## Completed results

Both runs completed and passed all checks. Signed endpoint sensitivities:
+0.158343933 mV/V (5 V) and -0.318396468 mV/V (3.3 V).
Sampled mean output ranges: 4.999597218--5.000388938 V and
3.299175929--3.300767911 V. Maximum sampled mean deviations from nominal
are 0.00805564% and 0.02497185%, respectively, for nominal models only.
Repeated 8 V means differ by 0.0163 uV and 0.00376 uV.

The report now uses these calibrated results, replacing historical line plots
and six SIM-02 table entries. previous_dc_section.tex preserves the earlier
narrative. Other electrical-characteristic rows remain from earlier benches
and are explicitly identified as pending verification with this calibration.
Figure PDF/PNG/SVG and the sampled_points.csv export are available.
