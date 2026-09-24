# SIM-05 - Enabled near-no-load input consumption

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

Complete calibrated regulator, ideal 8 V source, 27 C, normal enable/protection
sequence, both output modes. External RLOAD = 1 Mohm: approximately 5 uA or
3.3 uA. This is a near-no-load test, not an exact open circuit or shutdown mode.
R33 = 14846.5 ohm and RFB2 = 28759.8 ohm are unchanged. All auxiliary circuits
remain present, including the voltage doubler, protection, references and indicator.

## Method

Input switch closes at 5 ms. Transient simulation runs to 120 ms, maximum step
2 us, waveform compression disabled. Source current is -I(VBAT), including
all current supplied through the normal input path. A time-weighted mean over
100--120 ms is used; adjacent 10 ms windows are compared to check averaging.
Output voltage, enable, external load current and voltage-doubler output are
saved. Currents of the auxiliary test sources V5, V10 and V1 are checked so
that hidden ideal sources do not silently supply power in the measurement window.

Reported input current includes the small external-load current. The separate
input-minus-external-load value is retained in metrics for clarity; neither
quantity isolates the error amplifier or any single internal block.

## Reproduce

Run prepare_idle.py, execute the two SIM-05_calibrated_idle_*.asc files in
LTspice, then run analyze_idle.py analyze and analyze_idle.py plot with the
project Python environment. The analyzer requires completed logs/endpoints.
Results include raw/log/net/asc archives, hashes, CSV waveforms, metrics and
the exact netlist changes relative to the calibrated baseline.

The source waveform averages describe nominal electrical models at 27 C.
Hardware consumption, temperature dependence and shutdown consumption are
separate measurements. Historical TEST_IQ.asc remains unchanged.

## Verified results

| Mode | Mean source current (mA) | External load (uA) | Source power (mW) | Mean output (V) |
|---|---:|---:|---:|---:|
| 5V | 56.858782 | 5.000021 | 454.870256 | 5.000021 |
| 33V | 56.028087 | 3.300002 | 448.224698 | 3.300002 |

Both runs completed at 120 ms and stayed enabled in the measurement window.
The four 10 ms current averages spanning 80--120 ms have spreads of
0.01752 mA (5 V) and 0.00947 mA (3.3 V). These endpoint-dependent ripple
averages agree within 0.02 mA, below the chosen report resolution of 0.1 mA.
All saved auxiliary-source currents I(V5), I(V10), I(V1) are zero in the
measurement interval. No hidden source power was subtracted from the result.
The supporting plot shows 119--120 ms, without smoothing; the report uses
a paragraph and updated table rows rather than a redundant waveform figure.
The prior 14.995 / 14.564 mA bench results have been replaced, not interpreted
as comparable measurements of this calibrated complete circuit.


## Review before freezing — 2026-09-20

Archived RAW reanalysis reproduces the reported means. All eight archived
ASC/NET/LOG/RAW files match their recorded SHA256 and the active scenario
files. Completion, enable state and zero auxiliary test-source currents
were checked again. See `results/calibrated/review_verification.json`;
`verify_archive.py` repeats this check without overwriting simulation data.
No new LTspice run was needed. Marco's review and hardware measurement
remain pending. Existing report paragraph and table are sufficient.

For a later bench comparison, measure total supply current at 8 V with the
regulator enabled, recording both output settings, external load and input
voltage at the board. This test does not require ESP32 switching. Compare
settled readings, not the startup current or shutdown state.
