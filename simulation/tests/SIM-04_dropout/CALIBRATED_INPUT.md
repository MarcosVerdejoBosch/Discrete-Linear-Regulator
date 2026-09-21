# SIM-04 - Falling-input operating boundary with protections active

## Scope

This test determines how the complete calibrated regulator loses regulation as
its input falls. It does not bypass protection, force enable, or substitute
auxiliary supplies. Therefore, if shutdown occurs before an intrinsic dropout
knee, no intrinsic dropout voltage can be extracted from this test.

The 5 V falling-input segment is reused from the completed SIM-07 full-circuit
run. The 3.3 V run uses the same stimulus through 122 ms; only output selection
and the normal load differ. The common divider calibration is unchanged.
The original reduced dropout benches and their old 0.270 V / 0.408 V values
are retained for historical traceability, not validated by this test.

## Conditions

- Ideal source: 8 V through 80 ms, then falls to 4.8 V at 112 ms; holds to 122 ms.
- Source ramp: -0.1 V/ms. Input switch closes at 5 ms.
- Temperature: 27 C. Loads: 5 ohm and 3.3 ohm (approximately 1 A before shutdown).
- Global maximum step: 2 us; waveform compression disabled.
- R33 = 14846.5 ohm and RFB2 = 28759.8 ohm in both modes.
- No protection components or thresholds changed.

## Event definitions

Output exit is the first falling crossing of 98% of the nominal output after
80 ms: 4.9 V or 3.234 V. It is a dynamic system event for this ramp and history,
not a static minimum operating supply, cold-start threshold or intrinsic dropout.
The voltage reported for this event is the ideal source before the test switch
and input polarity MOSFET. VEE and VCTRL are also archived to avoid mixing nodes.
Delay, combined-enable and UVLO midpoint events use 50% of the simultaneous VEE;
this is an observation convention rather than an assumed transistor logic level.
All crossings are interpolated between adjacent saved samples.
A check 0.1 ms before the delay midpoint establishes whether output regulation
was still maintained before the disable sequence.

## Reproduction and traceability

Run prepare_input.py, then SIM-04_calibrated_input_33V.asc in LTspice.
The existing completed SIM-07_calibrated_protection_5V raw/log/net/asc must be
available. Run analyze_input.py analyze and then analyze_input.py plot.
Both source sets are hashed in results/calibrated/metrics.json; 3.3 V files are
archived here, while 5 V files are already archived under SIM-07 results.
The falling segments are exported to CSV without waveform smoothing.

## Verified result

Both logs and endpoints confirm completion. In both modes the event order is
delay permission falling, combined enable falling, output below 98%, then UVLO.
The first three events occur around 101.83--101.86 ms; UVLO follows near 105.03 ms.

| Mode | Source at 98% output (V) | Local VEE at event (V) | Output 0.1ms before delay edge (V) |
|---|---:|---:|---:|
| 5V | 5.814019 | 5.782566 | 4.999206 |
| 33V | 5.813976 | 5.782262 | 3.300563 |

These results identify a protection-induced operating boundary; intrinsic dropout
remains unmeasured with the calibrated regulator stage. Its verification requires
a separately documented bench maintaining enable/reference conditions independently.
The source minus output at the shutdown point must NOT be labeled dropout.
The report removes the old standalone dropout numbers, adds these dynamic system
events to the protection table, and retains SIM-04 plots outside the report to
avoid repeating the shutdown curves already shown in SIM-07.
