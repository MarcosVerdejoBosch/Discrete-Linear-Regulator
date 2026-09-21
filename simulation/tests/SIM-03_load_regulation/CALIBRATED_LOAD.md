# SIM-03: calibrated full-circuit load regulation

Both modes use R33=14846.5 ohm, RFB2=28759.8 ohm and RFB1=15k,
without readjustment. The source is held at 8 V and temperature at 27 C.
All regulator and protection stages remain present. This experiment
characterizes settled load regulation, not transient undershoot/overshoot.

## Stimulus

The original RLOAD is replaced with a time-dependent resistance:
R(t)=Vnom/Itarget(t). This produces a resistive load at each operating
point; actual current depends on the output voltage and is measured
from I(RLOAD), rather than assumed equal to Itarget.

Start at nominal 1 A, connect the input switch at 5 ms, and wait to
80 ms. Then visit nominal 0.1, 0.25, 0.5, 0.75 and 1 A at 40 ms
intervals, with 0.1 ms transitions of Itarget. The tested resistances
are 50, 20, 10, 6.666667 and 5 ohm in 5 V mode, and 33, 13.2, 6.6,
4.4 and 3.3 ohm in 3.3 V mode. Duration 280 ms, maximum step 2 us.
No independent startup at each load, zero-load test, or current-limit
test is implied by this procedure.

## Extraction

Use time-weighted voltage and current averages over each final 10 ms.
Require complete runs, enable above 5 V, and changes below 0.001 mV
between adjacent 10 ms voltage means. Repeated 1 A output means and
the original calibration point must agree within 1 uV. These numerical
checks are not physical accuracy specifications.

Endpoint sensitivity is abs(delta mean Vout / delta mean Iload), in
mV/A. Also report the signed output change over the sampled load range.
Parasitic and thermal limitations are those stated in the report;
neither hardware tolerances nor self-heating are validated by this run.

## Reproduction and provenance

calibrated_load.py prepare generates both schematics from the SIM-02
calibration pilots; run SIM-03_calibrated_load_5V.asc and
SIM-03_calibrated_load_33V.asc in LTspice, then use inspect and plot.
results/calibrated_load contains preparation metadata, raw/net/log/asc
archives, hashes, metrics and CSV points after successful extraction.
Only RLOAD and transient duration differ from the calibration pilots.
The old TEST_Load_Regulation.asc and earlier table entries are retained
as historical material rather than silently reused as new results.

## Numerical timestep check

The small preliminary endpoint changes warrant checking numerical
sensitivity. SIM-03_load_stepcheck_5V.asc and _33V.asc repeat the same
first 120 ms with maximum step reduced from 2 to 1 us. They retain
the startup 1 A point and the subsequent 0.1 A point. The original
plotwinsize=0 setting disables waveform compression in all these runs.
check_timestep.py compares time-weighted means from the same windows
and archives results separately in results/calibrated_load/stepcheck.
This check tests timestep sensitivity only, not component tolerance
or physical microvolt accuracy.

## Completed primary runs (2 us maximum step)

Both 280 ms runs completed with enable active and the settling checks
satisfied. Signed endpoint sensitivities: -0.0156774 mV/A in 5 V mode
and -0.00168011 mV/A in 3.3 V mode. Output changes from low to high
load: -14.1097 uV and -1.51210 uV. The 3.3 V curve is not strictly
monotonic; these are endpoint sensitivities, not worst-case local slopes.
Returned 1 A means differ from initial values by -0.1414 uV and
-0.07309 uV; initial values agree with calibration within 0.084 uV.
The figure uses mean output change relative to the final 1 A point,
in uV, and identifies the different vertical scales.

## Timestep check completed

Both 120 ms checks completed. Halving the maximum timestep changes the
compared mean outputs by at most 0.13069 uV (5 V) and 0.05774 uV (3.3 V).
Endpoint slopes from the check are -0.0156672 and -0.00161038 mV/A.
This supports reporting the primary results approximately as 0.016 and
0.0017 mV/A; it does not imply hardware microvolt accuracy. Fine structure
of the small 3.3 V curve should not be interpreted as a measured effect.
Figure, DC subsection and four table rows are updated; historical values
remain archived in previous_dc_section.tex. All original external files
remain untouched. The next experiment is SIM-06, load-step transient response
with this calibration and explicitly defined transition speed.
