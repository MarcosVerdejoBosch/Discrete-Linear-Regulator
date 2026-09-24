# Review status — 2026-09-24

The original GitHub history and license are preserved. This remains a simulation review snapshot, not a hardware-qualified release.

## Completed

- The builder previously executed the scenarios; the new U17 revision is ready for another personal review.
- U17 is identified as IRF4905. Its official model is used in the full-circuit scenarios; other IRF7328 devices are unchanged.
- All 16 primary SIM-01–SIM-09 entries completed locally. Report figures and tables were updated from the new results.
- The selector applies each verified solver and opens the saved waveform view. Fresh preparation, source matching and netlist generation were checked.
- SIM-09 retains its two interactive schematics and original Tian expression. Its fixed-bias core does not contain U17.

See [current numerical evidence and supplementary checks](U17_REVALIDATION_2026-09-24.md). Earlier manifests and review notes remain historical records.

## Before a frozen hardware release

1. Review this revised package and repeat the physical measurements.
2. Identify capacitor ESR/tolerance and relevant wiring, thermal and component variations.
3. Validate driver/pass-transistor temperatures and safe bench conditions. Electrical current limiting is not a continuous-short thermal rating.
4. Review redistribution permission for the remaining external libraries. Setup still requires the owner's model folder.
5. Decide whether capacitor-free operation remains a target requiring circuit changes: current evidence does not establish it across the load range.

## Stability comparisons retained

- [Output capacitor absent / 1 uF / 10 uF](../simulation/tests/SIM-09_loop_stability/results/output_cap_options/README.md).
- [Load sensitivity](../simulation/tests/SIM-09_loop_stability/results/load_sensitivity/README.md).
- [Series resistance and capacitance sensitivity](../simulation/tests/SIM-09_loop_stability/results/cap_esr/README.md).

The assembled branch has an explicit 1 ohm external resistor. Historical `ESR` labels denote modeled total series resistance; the 0.1 ohm case is hypothetical. A 10 uF capacitor is not a universal stability improvement at every load.
