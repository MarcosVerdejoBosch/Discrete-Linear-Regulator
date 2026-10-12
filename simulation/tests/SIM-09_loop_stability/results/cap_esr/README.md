# SIM-09: output capacitor and ESR sensitivity

Date: 2026-09-21. This study tests a concrete question raised by the earlier
load sweep: how sensitive is the lower near-no-load margin to the output
capacitor model? It is a diagnostic study, not a hardware tolerance rating.

## Conditions and justification

Both output modes, 1 Mohm external load, 27 C, fixed nominal auxiliary
biases from the 1 A core, restored R98/TL431/LM193 output auxiliary branch.
The circuit remains in voltage regulation. Other compensation components,
feedback calibration and R21=10 ohm are unchanged.

COUT is varied to 0.8 and 1.2 uF with ESR=1 ohm. ESR is varied to 0.1 and
3 ohm with COUT=1 uF. These are one-factor illustrative perturbations;
0.8/1.2 uF is not an asserted tolerance of the installed capacitor, and
0.1/3 ohm is not an asserted real ESR interval. Combined extremes, all loads,
input-voltage changes, temperature and model uncertainty are not swept.

Capacitors are open at DC, so the existing settled bias is used to initialize
OP; each AC run still recomputes its OP and its output is checked against the
reference. Both injections are compared. All 20 AC runs complete with the
Alternate solver, 2000 points/decade, 1 Hz--60 MHz. Nominal repeats reproduce
the prior auxiliary-restored results. CSVs, circuits, logs, OP and RAW are
archived with SHA256. Only saved waveforms are restricted to reduce file size.

General rationale: the output load/capacitor and ESR affect loop dynamics;
TI SLVA115A explains the output pole and ESR zero for PNP/PMOS regulators.
Its example-specific acceptable ranges are NOT imported into this design.
Source: https://www.ti.com/lit/an/slva115a/slva115a.pdf

## Results

| Case | COUT uF | ESR ohm | Phase margin deg | Gain margin dB |
|---|---:|---:|---:|---:|
| 5V_nominal | 1 | 1 | 41.558 | 16.791 |
| 5V_C080 | 0.8 | 1 | 43.929 | 16.413 |
| 5V_C120 | 1.2 | 1 | 39.707 | 16.998 |
| 5V_ESR010 | 1 | 0.1 | 35.511 | 20.160 |
| 5V_ESR300 | 1 | 3 | 55.527 | 8.996 |
| 33V_nominal | 1 | 1 | 31.761 | 16.962 |
| 33V_C080 | 0.8 | 1 | 33.274 | 16.526 |
| 33V_C120 | 1.2 | 1 | 30.559 | 17.175 |
| 33V_ESR010 | 1 | 0.1 | 26.415 | 19.200 |
| 33V_ESR300 | 1 | 3 | 43.893 | 8.954 |

Increasing ESR improves phase margin at these points but reduces gain margin.
Therefore these data do not justify selecting 3 ohm as an optimum. The smallest
phase margin among these tested conditions is 26.415 degrees (3.3 V, 0.1 ohm).
Positive margins are not a guarantee of every internal loop or the full PCB.

## Near-no-load transient cross-check

3.3 V, COUT=1 uF, ESR=1 or 0.1 ohm, same isolated auxiliary-restored core.
A diagnostic current sink adds 10 uA to the 1 Mohm base load at 1 ms and
removes it at 3 ms; edges last 1 us. Observe to 5 ms, max step 200 ns,
Alternate solver, no compression. The added current is small relative to
the ~0.62 mA pass collector current; the output excursion is ~69/74 uV.
Both responses show decaying ringing; lower ESR shows more ringing and a
longer return. No persistent oscillation is observed in the simulated window.

transient_metrics.json retains diagnostic last-entry settling in a band of
2% of the peak excursion, NOT +/-1% of nominal Vout as in SIM-06. That band
is only ~1.4 uV and stored float32 output resolution is ~0.24 uV; do not
publish the resulting settling times as precise hardware specifications.
No timestep/amplitude sweep was performed for these transient controls.
The report uses only the qualitative recovery observation. These tests do
not establish response to large load steps or the complete switching system.

## Reproduce

cap_esr.py prepare; run SIM-09_ce_<mode>_<case>_<voltage|current>.cir using
Alternate; cap_esr.py analyze; cap_esr.py plot. Initial biases remain
SIM-09_load_<mode>_idle_aux.bias in simulation/ltspice. The transient
conditions are recorded in transient_conditions.json and the archived
SIM-09_ce_transient_33V_*.cir files. Run those with Alternate, then
analyze_idle_transient.py. verification.json records the archive check.
All original nominal scenarios are preserved. No design modification adopted.

User identified a radial tantalum capacitor sold as 1 uF / 35 V. The supplied
listing was inaccessible during review; manufacturer, series, tolerance and
ESR remain unverified. See installed_capacitor.json. A 1 ohm ESR remains a
simulation assumption. Next: obtain part identification or ESR measurement
to relate the real component to these conditions; plan the corresponding measured transient with realistic
parasitics. A full operating envelope remains outside this limited study.


## Hardware clarification — 2026-09-21 (supersedes earlier ESR interpretation)

Marco confirms a discrete nominal 1 ohm resistor in series with the output
capacitor. The nominal simulation resistance represents this external
component and neglects intrinsic capacitor ESR. Effective branch series
resistance is external resistance plus intrinsic ESR (and other losses);
external-resistor tolerance is not yet specified. The 0.1 ohm total branch
case is hypothetical and does not represent the assembled board. The 3 ohm
case explores higher total series resistance; it does not establish actual
capacitor ESR. Historical file names and numeric ESR fields are retained
for traceability and denote total modeled series resistance in these runs.
TI SLVA115A, Figure 5, illustrates adding an external 1 ohm resistor for
stability in its example regulator. This supports the technique, not an
unconditional stability claim or the exact optimum for this design.
https://www.ti.com/lit/an/slva115a/slva115a.pdf
