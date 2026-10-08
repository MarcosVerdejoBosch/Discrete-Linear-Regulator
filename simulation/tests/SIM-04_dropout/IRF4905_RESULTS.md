# SIM-04 current results — IRF4905

## Bounded adjusted-threshold study

Both runs completed 120 ms. The source stays at 8 V for 80 ms and then falls at 0.1 V/ms to 4 V. RV10 = 100 kohm and RV12 = 47 kohm; loads are 50 / 33 ohm. Other component values are unchanged. Solver: Normal for 5 V, Alternate for 3.3 V; maximum step 2 us, trtol=1. No cshunt or other numerical parasitic was added.

| Mode | Event | Time (ms) | Board input (V) | Output (V) |
|---|---|---:|---:|---:|
| 5 V | Output loss 100 mV | 110.504 | 4.9467 | 4.9000 |
| 5 V | UVLO transition | 111.982 | 4.7991 | 4.7529 |
| 3.3 V | Output loss 100 mV | 112.137 | 4.7850 | 3.2000 |
| 3.3 V | UVLO transition | 112.058 | 4.7930 | 3.3012 |

In 5 V, the output-loss criterion precedes UVLO. The independent fixed-input holds confirm about 100 mV loss at a 4.95 V source. In 3.3 V, UVLO acts first, so this test does not extract intrinsic dropout in that mode.

The former deep-brownout protocol continued to 2.8 V and 142 ms. It repeatedly stalled around 136.8 ms after the relevant events; it remains unresolved. The new protocol is a separately executed, complete 8-to-4 V test, not a truncated RAW file presented as completed.

## Evidence and bench relevance

- [Current ramp metrics and hashes](results/adjusted/metrics.json), [diagnostic figure](results/adjusted/SIM-04_adjusted.pdf).
- [Fixed-input holds](results/adjusted_settled/metrics.json), [terminal-power calculation](results/driver_thermal/metrics.json).
- [Load-only pulses](results/pulsed_load/metrics.json), [pulses with external drive inhibition](results/pulsed_load_inhibit/metrics.json).

R21 stays at 10 ohm / 0.25 W as built. Near the 5 V dropout condition, pass-base current is about 147 mA and Q3 dissipation about 0.35 W. These electrical simulations do not establish safe sustained hardware operation; the previously proposed 100 ohm candidate is historical.
