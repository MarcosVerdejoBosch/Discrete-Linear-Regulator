# SIM-08 - Calibrated current limiting and recovery

## Conditions and reproducibility

Complete calibrated circuit, 8 V ideal source, 27 C, both output modes.
R33 = 14846.5 ohm and RFB2 = 28759.8 ohm are unchanged. Only the load,
transient duration and saved signals differ from the calibrated baseline.
The input switch closes at 5 ms. Observation starts after initial settling.

| Interval | 5 V load | 3.3 V load | Purpose |
|---|---:|---:|---|
| Before 80 ms | 5 ohm | 3.3 ohm | Approximately 1 A |
| 80--110 ms | 2.5 ohm | 1.65 ohm | Would draw 2 A at nominal voltage |
| 110--140 ms | 5 ohm | 3.3 ohm | Recovery from overload |
| 140--170 ms | 0.05 ohm | 0.05 ohm | Resistive short circuit |
| After 170 ms | 5 ohm | 3.3 ohm | Recovery from short |

Conductance changes linearly over 10 us at each listed edge. The load is a
positive time-dependent resistor, not an ideal forced current sink.
Simulation duration is 210 ms, maximum time step 2 us, compression disabled.
The numerical current-limit setting is preserved; it is not retuned to 1.5 A.

Run prepare_limit.py to recreate the two scenarios in simulation/ltspice.
Run each SIM-08_calibrated_limit_*.asc in LTspice. Then run analyze_limit.py
analyze followed by analyze_limit.py plot with the project Python environment.
The analyzer requires a completed log and the full simulation endpoint.

## Measurement definitions

Time-weighted plateau averages use the final 10 ms of each interval.
I(RLOAD) is the load current. -I(R25) is the current through the sense resistor
toward the output (LTspice designators). These currents need not match during
transients because the output capacitor and sensing branches also draw current.
Metrics retain plateau extrema and half-window drift, and sampled transient peaks.
Peak values are diagnostic, not characterized high-bandwidth peak specifications.
The figure uses original waveform samples with no smoothing.

The results apply to nominal electrical models. They do not establish continuous
short-circuit thermal capability or the pass transistor safe operating area.
Hardware validation and a separate thermal assessment remain necessary to claim
continuous short-circuit protection.

## Verified results

| Mode | Overload current (A) | Overload output (V) | Short current (A) | Short output (mV) | Final output (V) |
|---|---:|---:|---:|---:|---:|
| 5V | 1.485228 | 3.713072 | 1.473772 | 73.688624 | 5.000005 |
| 33V | 1.465455 | 2.418001 | 1.473773 | 73.688670 | 3.300000 |

Both runs completed. Enable stays above 7.09 V. Final output returns within
1 uV of its pre-fault mean. Fault-current half-window mean drift is below 1 uA.
Short onset has a sampled peak around 6.65 A in both load and sense current.
This peak has not undergone time-step sensitivity characterization; it is shown
in the waveform and discussed qualitatively, not tabulated as a guaranteed peak.
No manual limit adjustment, thermal simulation or hardware validation was performed.


## Review before freezing — 2026-09-20

Both archived runs reach 210 ms with completed logs. Eight ASC/NET/LOG/RAW
hashes match their manifests and active copies. Plateau means, extrema,
half-window drift and sampled event extrema were recalculated successfully.
Enable remains above 7.09 V and final outputs return within 1 uV of their
pre-fault means. The figure manifest matches the metrics; the PNG was
visually reviewed against the report. See `results/calibrated/review_verification.json`
and `verify_archive.py`. No new LTspice run or peak-convergence study was
performed. Existing report text, figure and table agree and are retained.
Marco's review and physical validation remain pending.

The figure is relevant because it shows the transition from voltage
regulation into current limiting and recovery after fault removal in both
modes. Retain the brief current excursion: the sampled short-onset peak is
about 6.65 A in both load and sense-resistor current. Its amplitude remains
a diagnostic nominal-model result, not a characterized peak specification.
Do not use these electrical simulations as evidence for continuous short
survival. Physical current setting, fault duration and thermal/SOA checks
will be defined before implementation, particularly without a heatsink.
ESP32 details remain deferred. Next review: SIM-09 loop stability.
