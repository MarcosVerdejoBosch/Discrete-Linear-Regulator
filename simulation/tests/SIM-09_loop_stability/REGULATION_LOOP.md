# SIM-09 - Nominal regulation-loop stability

**U17 follow-up (2026-09-24):** the fixed-bias core below is unchanged. The full-circuit tone cross-check was rerun with IRF4905; use the [current record](../../../publication/U17_REVALIDATION_2026-09-24.md) and updated `results/core/validation.json` for its numerical differences.

## Scope and preserved circuit

This is a small-signal regulation-stage bench at approximately 1 A in both
calibrated output modes, 27 C. It is NOT an AC model of the complete switching
auxiliary supply or a stability guarantee for every load and temperature.
It retains the discrete differential/VAS/output stages, PNP pass device,
feedback selection, compensation, output capacitor/ESR, enable drive interface,
current-sense and current-limit amplifier/diode path. R67 (reference-input
resistance) and D13 (pass protection diode, LTspice designators) are retained.
No regulator resistor, transistor or compensation value is retuned.

The input and startup/reference/sequencing blocks are replaced by ideal DC
bias sources VEE, VCTRL, VREF and TTL. Their values are time-weighted means
from 70--80 ms of the complete SIM-08 runs at an 8 V source and 1 A load.
Exact values are in results/core/bias_reference.json. The output ground-shunt
JFET and its bias resistors remain, with the auxiliary source represented by
14.9 V and its comparator treated as released. The rest of the auxiliary
reference/comparator circuitry and its output-connected loading is omitted.
Supply/reference impedances, doubler ripple and changes of enable state are
therefore outside the AC bench. Input power cannot be inferred from it.

Direct static attempts on the complete circuit and preliminary isolated
benches did not provide accepted DC solutions. They are diagnostic attempts,
not report evidence. The accepted bench first settles for 10 ms with a 200 ns
maximum step and saves its bias. AC analyses load this bias; their final OP
outputs agree with the complete-circuit reference within 1 uV. Both injection
runs have the same DC operating point and about 1 A load current.

## Probe and definitions

The original lg_single probe lies between FB and the EA input node N033.
Two runs activate the voltage source (lg=-1) and current source (lg=+1).
DC loop continuity and the compensation network are preserved. Processing
uses the expression in the installed LTspice Educational/LoopGain2 example,
based on Tian et al., Striving for Small-Signal Stability, IEEE Circuits and
Devices Magazine 17(1), 31--41, January 2001:
https://www.kenkundert.com/docs/cd2001-01.pdf

Let xv and iv be V(lgs:x), I(lgs:Vi) in the voltage-injection run, and xi,
ii the same quantities in the current-injection run. Define
Q = 2*(iv*xi - xv*ii) + xv + ii, then T = Q/(1-Q).
The adopted return ratio uses the critical point -1. The sweep is 1 Hz to
60 MHz, 200 points per decade. Phase is unwrapped; unity and odd -180-degree
crossings are interpolated in log frequency. All crossings are recorded.
Phase margin is 180 degrees + phase at unity; gain margin is minus the gain
in dB at -180 degrees. Gain at 1 Hz is not labeled DC gain.

Sources for applicability and operating-point limitations:
https://sites.google.com/site/frankwiedmann/loopgain
https://www.analog.com/en/resources/technical-articles/ltspice-speed-up-your-simulations.html

## Validation and limits

- Analytic G-R-C loop, T = 100/(1+s*0.001): maximum relative extraction error
  5.1e-14. This checks processing and sign convention, not regulator accuracy.
- Auxiliary bias changed from 14 to 16 V in the 5 V AC bench: margin changes
  below 0.00001 degree and 0.00001 dB. This checks the released shunt bias
  approximation only; it does not validate omission of all supply dynamics.
- A voltage-only ratio differs from the Tian result near crossover by about
  1.5 dB and 6 degrees. It is not substituted for the double-injection result.
- Complete-circuit tone tests inject 500 uV at each calculated crossover
  after 80 ms startup. A local 10 ns timestep bound resolves the sinusoid.
  The last 80 cycles are fitted with time-weighted sine/cosine, offset and
  drift terms. The complete-circuit voltage-return ratio is compared with
  the SAME voltage-return ratio in the isolated AC bench, not directly
  confused with the two-injection Tian quantity. See validation.json.

These tests address the main regulation loop at one operating load. They do
not establish all internal-loop stability, protection-loop behavior, periodic
stability of the switching doubler, or margins over tolerances and load range.

## Reproduce in order

1. Run prepare_core.py. Execute both SIM-09_core_start_*.cir and wait until
   completed logs and SIM-09_core_*.bias files are present. The base
   SIM-09_core_*.cir files are templates, not accepted OP scenarios.
2. Run prepare_ac.py. Execute the four SIM-09_ac_*.cir, the four
   SIM-09_check_dbl*.cir, and the two SIM-09_analytic_*.cir files.
3. Run analyze_loop.py analyze, then prepare_validation.py.
4. Execute both SIM-09_full_tone_*.cir and wait for complete 80.25 ms results.
5. Run analyze_loop.py validate and analyze_loop.py plot.

Read results/core/metrics.json and validation.json before interpreting curves.
Valid scenarios, raw files, logs, bias files, extracted CSVs and hashes are
archived under results/core. Existing full-circuit scenarios remain unchanged.

## Accepted nominal results

| Mode | Crossover (kHz) | Phase margin (deg) | Gain margin (dB) |
|---|---:|---:|---:|
| 5V | 557.712419 | 52.508002 | 17.277603 |
| 33V | 530.472614 | 51.978546 | 17.752152 |

One unity crossing and one -180 degree crossing were found in each sweep.
Complete-circuit single-tone voltage-return differences (full minus core):
- 5V: -0.037325 dB, 1.113249 degrees.
- 33V: -0.051174 dB, 0.941926 degrees.
The report rounds the cross-check bound upward to 0.06 dB and 1.2 degrees.
This is not an extraction of the full switching circuit Tian return ratio.
No component values were adjusted to improve margins.


## Detailed review — 2026-09-20

See [review and numerical evidence](results/review/REVIEW.md). Eight additional
AC runs check tenfold frequency resolution and reversed probe orientation.
Maximum changes from frequency refinement: 3.009 Hz in crossover,
0.00007 degree in phase margin and 0.000161 dB in gain margin. Reversing the
probe reproduces the return ratio within 1.77e-8 relative error. Reported
rounded margins remain unchanged. Archived baseline OP and tone data were
also rechecked. The full-circuit agreement bound applies specifically to
the final 80-cycle fit; shorter windows produce slightly different values.
The next extension is load and output-capacitor/ESR sensitivity, not a claim
of complete-system stability. User and hardware validation remain pending.


## Additional operating loads — 2026-09-20

[Load sensitivity](results/load_sensitivity/README.md) now covers 100 mA
and 1 Mohm in both modes, with newly settled operating points and nominal
auxiliary biases held fixed. Near-no-load margins are lower than at 1 A.
An additional restored-output-branch control changes phase margin by <0.1
degree. See the separate metrics and comparison figure; original nominal
results are preserved. COUT/ESR and near-no-load transient checks remain next.


## Capacitor / ESR extension — 2026-09-21

See [sensitivity and transient controls](results/cap_esr/README.md).
One-factor diagnostic variations completed; real capacitor identification
remains pending. Original nominal results are unchanged.


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
