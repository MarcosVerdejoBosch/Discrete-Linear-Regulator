# External output capacitor comparison — 2026-09-21

## Decision

The present evidence does not support capacitor-free operation over the load
range. In the fixed-bias core without the external output capacitor, near-no-load
AC margins are negative and time-domain responses continue oscillating through
the 100 us observation window. This is model evidence, not a PCB measurement.
A 10 uF capacitor is not universally more stable: at 1 A it improves margins
relative to 1 uF, but near no load it decreases phase margin.

## Conditions

Both output modes, ~1 A and 1 Mohm external loads, 27 C, original fixed
auxiliary biases, auxiliary output branch restored. No feedback calibration
or internal compensation change. Capacitor choices: absent, 1 uF, 10 uF.
Present capacitors retain the external 1 ohm series resistor; intrinsic ESR
is neglected. Therefore 10 uF is an ideal capacitance scenario, not a model
of any specified electrolytic part. With no capacitor both CLOAD and its
series resistor are removed; other compensation capacitors remain.
24 completed AC runs, Alternate solver, 2000 points/decade, 1 Hz--60 MHz.
DC outputs remain regulated and matching between injection runs, even when
the equilibrium is dynamically unstable. Successful OP convergence alone
is not a stability check. Original accepted scenarios are preserved.

| Case | Phase margin deg | Gain margin dB |
|---|---:|---:|
| 5V_1A_none | 37.15 | 11.67 |
| 5V_1A_1u | 52.51 | 17.28 |
| 5V_1A_10u | 58.87 | 17.74 |
| 5V_idle_none | -64.48 | -5.83 |
| 5V_idle_1u | 41.56 | 16.79 |
| 5V_idle_10u | 32.01 | 17.58 |
| 33V_1A_none | 39.13 | 12.52 |
| 33V_1A_1u | 51.98 | 17.75 |
| 33V_1A_10u | 58.39 | 18.19 |
| 33V_idle_none | -75.38 | -7.35 |
| 33V_idle_1u | 31.76 | 16.96 |
| 33V_idle_10u | 26.96 | 17.65 |

## Transient cross-check

Both no-capacitor, 1 Mohm core variants: 100 us, max step 5 ns, 10 uA added
current sink at 10 us, removed at 50 us, 0.1 us edges. Both finish and show
persistent oscillation in the final 20 us. Stored peak-to-peak values are
~0.823 / 0.931 V, diagnostic only; their amplitude has not undergone a
step-size sensitivity study. No exact hardware oscillation amplitude or
frequency is claimed. The lower-level OP values used for initialization
were recomputed by LTspice; this transient tests that equilibrium dynamically.

## Reproduction / files

output_cap_options.py prepare; run SIM-09_outcap_*.cir with Alternate;
output_cap_options.py analyze. The two SIM-09_nocap_transient_*.cir are
standalone transient scenarios in the same LTspice directory. Model and bias
dependencies are inherited from the documented SIM-09 core. metrics.json
and transient_metrics.json preserve archive hashes. CSVs and the supporting
transient figure are retained. User acceptance and hardware checks pending.

Do not describe the design as capacitor-free or assert that a 10 uF
electrolytic universally improves stability. Choosing an electrolytic also
requires its frequency-dependent ESR and the actual connection topology.
