# SIM-07: full-circuit input-voltage protection

## Test configuration

Calibrated 5 V mode, 5 ohm load, 27 C. All physical circuit component
lines match SIM-02_cal_02_5V.net except the source waveform. No UVLO,
OVLO, time-delay or hysteresis component has been adjusted. This run
does not independently validate protection behavior in 3.3 V mode.

Start at 8 V, input switch closes at 5 ms. Hold to 80 ms; descend to
4.8 V at 112 ms; hold to 122 ms; rise to 12 V at 194 ms; hold to
204 ms; descend to 8 V at 244 ms; hold to 264 ms. Source ramp magnitude
is 0.1 V/ms. Maximum timestep 2 us; waveform compression disabled.

## Signal mapping, verified against the generated netlist

- V(N034): ideal source, before the series input switch.
- V(VBAT): after the input switch, before the polarity-protection MOSFET.
- V(VEE): supply after both elements; input of the protection dividers.
- V(1): UVLO permission, output of U15 (LM339).
- V(2): OVLO permission, output of U12 (LM324).
- V(LDO_2): time-delay permission.
- V(TTL): combined enable; monitor independently from comparator outputs.
- V(COMP): auxiliary reference; V(N086)/V(N085): UVLO/OVLO sense inputs.

The time-delay path senses the startup-circuit output. It can therefore
remove enable independently of UVLO and OVLO. Do not identify the
system-enable switching voltage with a comparator threshold without
checking all three permissions.

## Extraction and interpretation

Ignore initial startup before 70 ms. Record every crossing of each
control output through 50% of the simultaneously sampled VEE supply,
linearly interpolating between the bracketing samples. Report the actual
VEE voltage at that instant and preserve the source voltage separately.
These are dynamic switching thresholds for the stated source ramp,
not a zero-slew DC sweep or a statistical tolerance specification.

UVLO hysteresis: permission rising threshold minus falling threshold.
OVLO hysteresis: permission falling threshold minus rising threshold.
Enable events are extracted separately, together with the states of the
other permissions, to identify which condition controls the output.
Plateau averages verify output behavior and reference availability.

The figure uses actual VEE and Vout, with control voltages normalized
to VEE in the lower panels. These traces are normalized analog voltages,
not idealized Boolean waveforms. Comparator markers do not label the
thresholds of the complete enable sequence.

## Reproduction

prepare_protection.py creates SIM-07_calibrated_protection_5V.asc.
Run in LTspice, then analyze_protection.py analyze and plot. Results,
original samples, netlist, log, schematic and SHA-256 hashes are under
results/calibrated. Old TEST_UVLO_OVLO.asc remains historical material.

## Completed observations

The 264 ms run completed, with one falling and one rising midpoint
crossing per protection comparator after startup. Dynamic midpoint
thresholds at the protection-divider supply:

| Comparator | Input rising (V) | Input falling (V) | Separation (V) |
|---|---:|---:|---:|
| UVLO | 5.859048 | 5.494902 | 0.364147 |
| OVLO | 11.002978 | 10.135078 | 0.867900 |

The delay path falls at 5.785534 V and combined enable falls at
5.783763 V, while UVLO remains high. On recovery, UVLO crosses its
midpoint at 5.859048 V, delay at 6.123305 V, and enable at 6.129679 V.
Therefore the UVLO comparator alone does not determine the system's
observed low-input shutdown/restart thresholds under this ramp.

OVLO midpoint crossings and enable crossings also differ: enable falls
at 11.094574 V and rises at 10.253548 V. In particular, enable can rise
before the OVLO output reaches half supply: the discrete BJT enable
stage does not use a half-supply logic threshold. The recorded
other_controls_above_half_supply fields are measurement comparisons,
not assertions that the physical inputs are logically valid/invalid.
No zero-slew threshold or ramp-rate independence is claimed.

During the low/high fault holds, mean Vout is 0.228/0.275 mV; the
auxiliary reference remains near 2.474 V. Initial/final mean Vout is
5.000005374/5.000005387 V, confirming resumed regulation at 8 V.
The report figure, explanation and six comparator rows replace the
historical values. Short-circuit results are documented separately in SIM-08.


## Review before freezing — 2026-09-20

The archived 264 ms RAW was reprocessed: all comparator, delay and enable
crossings and all recorded plateau means reproduce the stored results.
Four archived ASC/NET/LOG/RAW hashes match the manifest and active copies.
The figure manifest matches the metrics, and the plotted figure was visually
reviewed. See `results/calibrated/review_verification.json`; reproduce this
check with `verify_archive.py`. No new LTspice run was needed.
The existing report figure, text and table agree; no expansion is required.
Marco's review and physical validation remain pending.

Keep this original-threshold scenario separate from SIM-04's adjusted
RV10/RV12 exploration. The results cover the 5 V mode and the stated ramp,
not both output modes or ramp-rate independence. For a later bench check,
record the protection-divider input voltage together with the comparator
output, then repeat observing enable/output. Output alone cannot identify
the UVLO comparator threshold. Physical load and input sweep will be defined
at implementation; ESP32 details are deferred. Next review: SIM-08.
