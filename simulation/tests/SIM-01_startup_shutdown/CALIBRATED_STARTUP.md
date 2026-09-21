# SIM-01 - Calibrated startup, shutdown and reconnection

Status: both nominal and refined 140 ms runs completed, including reconnection. User review remains pending before freezing.

Both output modes inherit the complete calibrated SIM-02 circuit: R33=14846.5 ohm, RFB2=28759.8 ohm. The source is 8 V, temperature 27 C, and resistive loads are 50 ohm / 33 ohm (approximately 0.1 A). Calibration is unchanged between startup, shutdown and reconnection. The lighter load is intentional for sequencing; SIM-02 DC line characterization uses approximately 1 A.

The input switch connects at 5 ms, opens at 55 ms and reconnects at 85 ms. Its control ramps over 1 us. The transient ends at 140 ms with a 2 us maximum step and data compression disabled. Disconnection opens the supply path; it does not force the downstream node to zero.

## Files and reproduction

- prepare_startup.py derives the two SIM-01_calibrated_startup_*.asc files from SIM-02_cal_02_*.asc and records hashes.
- run_calibrated.cmd uses the installed LTspice Normal solver via -norm. The final load is a constant behavioral resistance, using R=5/table(time,0,0.1,140m,0.1) or R=3.3/table(time,0,0.1,140m,0.1), electrically equal to 50 or 33 ohm. The launcher uses the usual local installation path and makes no model changes.
- analyze_startup.py analyze requires completed logs, complete time records, asserted enable and settled output. It archives the accepted files and metrics.
- analyze_startup.py plot renders both modes from RAW samples, without smoothing.
- check_step.py compares complete 2 us nominal and 1 us refined records, including reconnection. The refined files explicitly set `.options trtol=1`, use the Normal solver and unchanged components. The script requires completed logs and full 140 ms data. run_step_check.cmd reproduces these refined runs. This is a combined timestep/error-control refinement, not an isolated timestep-only experiment.

## Diagnostic attempts

Normal solver / default integration stalled during shutdown in 5 V and near enable in 3.3 V. Gear integration also encountered the enable transition. These incomplete runs remain under diagnostic_* result folders and are not evidence for the report. The textual solver=alt option is unsupported by this installed version, the alternate solver was tried via -alt but did not resolve all transitions. Final nominal runs use Normal solver and the behavioral resistor representation already used in SIM-06. RAW files left over after a syntax failure must never be treated as a completed retry.

Solver command reference: https://www.analog.com/media/en/news-marketing-collateral/solutions-bulletins-brochures/ltspice-keyboard-shortcuts.pdf

## Scope and hardware comparison

See BENCH_PLAN.md for objectives, loads, switch equivalence, oscilloscope channels and timing definitions. Initial pulse and discharge depend on load, source impedance and parasitics. C11 has no explicitly specified ESR in this nominal model. No ideal input-current peak will be presented as a hardware requirement. The input MOSFET annotation/model discrepancy remains a project-level limitation.

Hardware feasibility: Marco confirmed an OWON VDS1022 (2 channels), adjustable source and resistors. BENCH_PLAN.md separates broad and fast captures for the 5K memory and records actual KiCad pads, including the distinction between TP_TTL and net TTL.

The earlier SIM-01_startup_shutdown_5V.asc and results/input_switch are preserved as historical material with the earlier calibration; do not mix their numbers with the new run.

## Completed nominal results

| Mode | Mean output (V) | Enable delay (ms) | Output 98% delay (ms) | Initial pulse (V) | Output below 50 mV (ms after opening) | VCTRL below 50 mV (ms after opening) |
|---|---:|---:|---:|---:|---:|---:|
| 5V | 5.000019 | 23.818 | 29.188 | 0.854 | 0.394 | 12.475 |
| 33V | 3.300002 | 23.818 | 29.187 | 0.842 | 0.332 | 12.479 |

Complete-record refinement: extracted timing changes remain below 1.5 us; settled means differ by less than 0.1 uV. First-startup pulse changes are 0.322 mV (5 V) and -0.030 mV (3.3 V). The reconnection pulse is more sensitive in 5 V: 1.16282 versus 1.18202 V (19.2 mV difference); it is not reported as a precision peak measurement. These comparisons establish numerical agreement for the reported sequencing metrics, not hardware accuracy or proof for every operating condition.

See results/refined/README.md for the diagnostic history and accepted source filenames. Original incomplete fine runs are retained in results/refined/previous_fine. The accepted complete files are archived under results/calibrated, with hashes in step_check.json. Existing nominal curves and reported values remain unchanged.

Additional unresolved limits: source impedance/ESR sensitivity and the IRF4905 annotation versus irf7328 model discrepancy. Retain these in the freeze review.
