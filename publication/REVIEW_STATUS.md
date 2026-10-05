# Review status — 2026-10-05

The original GitHub history and license are preserved. This remains a simulation review snapshot, not a hardware-qualified release.

## Completed

- The user reports that all 16 principal selector entries executed successfully after the U17/convergence revisions. This is user-reported simulation review, not physical validation.
- U17 is identified as IRF4905. Its official model is used in the full-circuit scenarios; other IRF7328 devices are unchanged.
- All 16 primary SIM-01–SIM-09 entries completed locally. Report figures and tables were updated from the new results.
- The selector applies each verified solver and opens the saved waveform view. Fresh preparation, source matching and netlist generation were checked.
- SIM-09 retains its two interactive schematics and original Tian expression. Its fixed-bias core does not contain U17.
- A separate selector now provides 20 completed SIM-09 load/external-capacitance combinations and two bounded UVLO-bypass diagnostic schematics. Four comparative Bode figures are included in the report. These additions await the user's review.
- SIM-08 3.3 V overload currents were checked against the user's completed RAW: load 1.4655 A; sense branch 1.4815 A. The report distinguishes these quantities.
- The approximately 47 A connection spike in selector entries 8/9 was traced predominantly to C20 in the doubler. A separate assumed-impedance sensitivity gives approximately 12.1 A; neither value is a hardware measurement.

See [current numerical evidence and supplementary checks](U17_REVALIDATION_2026-09-24.md). Earlier manifests and review notes remain historical records.

## Before a frozen hardware release

1. Review the additional studies and perform the planned physical measurements.
2. Identify capacitor ESR/tolerance and relevant wiring, thermal and component variations.
3. Validate driver/pass-transistor temperatures and safe bench conditions. Electrical current limiting is not a continuous-short thermal rating.
4. Review redistribution permission for the remaining external libraries. Setup still requires the owner's model folder.
5. Decide whether capacitor-free operation remains a target requiring circuit changes: current evidence does not establish it across the load range.

## Stability comparisons retained

- [Output capacitor absent / 1 uF / 10 uF](../simulation/tests/SIM-09_loop_stability/results/output_cap_options/README.md).
- [Load sensitivity](../simulation/tests/SIM-09_loop_stability/results/load_sensitivity/README.md).
- [Series resistance and capacitance sensitivity](../simulation/tests/SIM-09_loop_stability/results/cap_esr/README.md).

The assembled branch has a 1 uF capacitor and an explicit 1 ohm discrete resistor. Historical `ESR` labels denote modeled total series resistance; their 0.1 ohm case is hypothetical. The [new external-capacitor study](../simulation/ESTUDIOS_ADICIONALES.md) keeps that branch intact and adds a separate CEXT/REXT branch. The historical replacement/removal studies above must not be confused with that addition. A 10 uF capacitor is not a universal stability improvement at every load.
