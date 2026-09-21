# SIM-06: calibrated full-circuit load transients

## Conditions

8 V source before the input switch, 27 C, same calibrated divider as
SIM-02/03 (R33=14846.5 ohm, RFB2=28759.8 ohm, RFB1=15k).
All regulator and protection stages remain present.

RLOAD is resistive: R(t)=Vnom/Itarget(t). Nominal load is 0.1 A at
startup, increases to 1 A at 80 ms, and returns to 0.1 A at 120 ms.
Itarget (and thus conductance) ramps linearly in 1 us. Actual current
depends on Vout, so its transient is saved and shown rather than assumed
to be an ideal 1 us current ramp. Loads are 50/5 ohm for 5 V and
33/3.3 ohm for 3.3 V. Duration 160 ms; input switch closes at 5 ms.
The stimulus differs from SIM-03's 100 us transitions and from the
historical reduced transient benches. Results are not interchangeable.

## Time resolution

Global maximum step 2 us; no waveform compression (plotwinsize=0).
An isolated BRES voltage source, connected only to its own test node
and ground, ramps during 79.99--80.2 ms and 119.99--120.2 ms.
tripdv=0.001 and tripdt=20n force local timestep refinement. BRES has
no electrical connection to regulator signal or supply nodes.
The mechanism was verified first in results/timestep_probe.cir; its
recorded maximum step inside the ramp was 19.53125 ns. The actual
regulator raw time vector is checked again before reporting results.

ADI's explanation of common timesteps and B-source rejection is at
[EngineerZone, LTspice employee response](https://ez.analog.com/design-tools-and-calculators/ltspice/f/q-a/603200/the-effect-tripdt-setting-has-on-a-device-and-b-device-behavior/597210).
This is simulation infrastructure, not an added physical circuit.

## Measurement definitions

The reference after each transition is the time-weighted final 10 ms
mean (110--120 ms and 150--160 ms). Initial means use 70--80 ms.
Undershoot is final reference minus minimum Vout; overshoot is maximum
Vout minus final reference. Percentages use that final reference.
Extrema are measured across the entire interval before the next change.

Settling is elapsed time from the start of the conductance ramp to the
last inward crossing of the +/-1% band around the final mean. The
crossing is interpolated between original samples; all later samples
through the end of the observation interval must remain in the band.
Peak times use original samples, with no interpolation or smoothing.
Enable must remain active. The preceding and final 10 ms means must
agree within 1 uV; recovery must occur inside the refined window.

## Outputs and reproducibility

prepare_transient.py generates both test schematics. Run their asc files
in LTspice, then analyze_transient.py analyze and analyze_transient.py plot.
results/calibrated contains preparation hashes, archived asc/net/log/raw,
metrics, and CSV windows of original Vout/Iload samples. The figure
shows 5 V, 3.3 V and actual load currents in separate rows, with matched
time axes. Shading indicates +/-1%; dashed lines indicate final means.
These are nominal-model results, with the report's parasitic and thermal
limitations. They do not establish measured PCB response or loop phase margin.

## Completed result

Both 160 ms simulations completed. Maximum recorded step near the
four transitions is below 20 ns, enable stays above 7.226 V, and
final-window mean drift is below 0.065 uV.

| Mode | Load-increase undershoot | Load-decrease overshoot | Settling up/down, +/-1% |
|---|---:|---:|---:|
| 5 V | 171.166 mV (3.423%) | 361.702 mV (7.234%) | 7.274 / 5.975 us |
| 3.3 V | 164.558 mV (4.987%) | 360.038 mV (10.910%) | 7.246 / 14.696 us |

After load decrease, minimum outputs are 4.962543 V and 3.213964 V.
The latter falls outside the 3.3 V +/-1% band and therefore requires
using the last inward crossing, not the first return after overshoot.
Peak output voltages are 5.361721 V and 3.660040 V. These excursions
are retained in the figure and report, not clipped or smoothed.
The returned low-load means agree with their initial values within
0.056 uV. No numerical timestep-halving study was performed for SIM-06;
local sampling resolution is verified directly from the raw time vector.

All calibrated circuit component lines were compared with the SIM-02
pilots: only RLOAD differs, with the isolated BRES monitor additionally
present. The historical table is archived in previous_transient_section.tex.


## Review before freezing — 2026-09-20

Archived RAW data were reprocessed to check all four voltage extrema and
last-entry settling measurements. Eight archived ASC/NET/LOG/RAW files
match their recorded hashes and active copies. The figure manifest matches
the metrics; the plotted PNG was visually reviewed against the reported
excursions. Both runs complete and enable remains active. See
`results/calibrated/review_verification.json`. No new LTspice run was needed.
This confirms extraction and file consistency, not timestep convergence;
the existing limitation on absence of a timestep-halving study remains.
The report figure and table already agree, so no editorial expansion is needed.
Marco's validation and physical measurements remain pending.

### Physical follow-up, deferred

This test is relevant because it measures output deviation and recovery
when the load changes, complementing settled load regulation (SIM-03).
Keep the existing 0.1--1 A simulation as the nominal scenario. For the
board without a heatsink, choose the physical current range after checking
available components and dissipation, then create a separately identified
simulation with those same loads. Do not compare lower-current hardware
results directly with this 1 A scenario. Record actual load transition
time and output response. ESP32 and switch implementation are deferred
until the physical bench is assembled, as requested by Marco.
