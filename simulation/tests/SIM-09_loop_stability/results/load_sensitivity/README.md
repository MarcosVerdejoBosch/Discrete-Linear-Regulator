# SIM-09: load sensitivity — 2026-09-20

## Purpose and scope

Vary the external load while retaining the nominal fixed VEE/VCTRL/VREF/TTL
biases of the 1 A core for each output mode, VDBL=14.9 V, 27 C, COUT=1 uF,
ESR=1 ohm. This isolates load dependence. It does not reproduce the exact
full-circuit light-load supply impedances, voltages or doubler ripple.
No feedback calibration, compensation or R21 value was changed.

Each new core settles for 10 ms, maximum step 200 ns, and saves its own
bias. AC uses two injections, 2000 points/decade, 1 Hz to 60 MHz.
Both injections have matching saved OP quantities. Final 1 ms output samples
show no variation at stored float32 precision; this is not proof of zero
physical ripple. AC output differs from the final startup sample by less
than 0.11 uV across all six variants. Current limiting remains inactive.

## Results

| Mode | External load | Crossover kHz | Phase margin deg | Gain margin dB |
|---|---|---:|---:|---:|
| 5 V | ~1 A, existing reference | 557.712 | 52.508 | 17.278 |
| 5 V | 50 ohm, ~100 mA | 424.022 | 57.272 | 18.349 |
| 5 V | 1 Mohm, ~5 uA | 19.476 | 41.469 | 16.791 |
| 3.3 V | ~1 A, existing reference | 530.473 | 51.979 | 17.752 |
| 3.3 V | 33 ohm, ~100 mA | 415.154 | 53.823 | 18.408 |
| 3.3 V | 1 Mohm, ~3.3 uA | 17.142 | 31.670 | 16.963 |

One unity and one -180-degree crossing occur in each sweep. Positive margins
at these points do not prove every load between them, every internal loop,
or the complete periodic circuit stable. No minimum-load requirement has
been established. The lower near-no-load margins warrant checking output
capacitance/ESR and transient behavior before broadening the conclusion.

## Auxiliary output-loading control

The full circuit contains an output branch missing from the nominal core:
R98 OUT--N031, U20 TL431, R100 from VDBL, and U18 LM193 driving N025.
Two further 1 Mohm variants restore these four original components, keeping
VDBL and other supplies fixed. Results are in ../load_aux/metrics.json.
Phase margins become 41.558 / 31.761 degrees, crossover 19.523 / 17.186 kHz.
The original conclusion changes by less than 0.1 degree. R98 draws about
4.00 / 2.64 uA in these models; it is not a 2 kohm resistor directly to ground.
TIP42 collector currents are about 1.046 / 0.621 mA, showing that near-zero
external load is not zero pass-device current. This control does not restore
switching-doubler dynamics or validate all auxiliary omissions.

## Files, solver and reproduction

load_sensitivity.py actions: prepare, ac, analyze, plot. Run from the project
Python environment. Between prepare and ac, execute the four
SIM-09_load_<mode>_<100mA|idle>_start.cir in simulation/ltspice. Between ac and
analyze, execute their voltage/current .cir files. Use the Alternate solver
for both 3.3 V / 100 mA AC injections; Normal works for the other accepted
main scenarios. The failed Normal DC attempt is preserved in
normal_solver_attempt, not counted as accepted data. No component was
changed to solve convergence.

For auxiliary controls, repeat prepare/ac/analyze with --aux; startup uses
Normal and both AC injections use Alternate. Their files are
SIM-09_load_<mode>_idle_aux*.cir. These controls have a separate result folder.
The main plot compares only the original core topology at three loads.
Archives contain CIR, bias, RAW, OP, logs, CSV and manifests. verification.json
checks all accepted archived hashes and operating conditions. Existing nominal
results remain unchanged. User review and hardware validation are pending.
