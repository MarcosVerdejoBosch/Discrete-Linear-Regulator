# First review snapshot

Date: 2026-09-21. Original GitHub history and license are preserved. This branch reorganizes the working material for review; it is not a hardware-validated release.

## Evidence

- Board: fabricated and assembled; 5 V and 3.3 V outputs checked by the builder.
- SIM-01: calibrated startup/shutdown and numerical refinement completed.
- SIM-02/03: line/load regulation, specified operating points and averaging windows documented.
- SIM-04: original enable-limited input boundary distinguished from adjusted-threshold dropout studies. Driver thermal limits remain relevant; no sustained dropout bench clearance.
- SIM-05: complete enabled near-no-load current, including auxiliaries.
- SIM-06: resistive load-step response; no hardware-equivalent peak accuracy claimed.
- SIM-07: dynamic comparator hysteresis distinguished from system enable thresholds.
- SIM-08: electrical current limit and recovery; no continuous-short thermal guarantee.
- SIM-09: fixed-bias main-loop studies and checks, plus load/capacitance/series-resistance variants. No-capacitor near-no-load instability is recorded, not omitted.

## Before a frozen release

1. Builder reviews report and selected scenarios. This snapshot does not mark that review complete.
2. Resolve clean-clone model/symbol dependencies and redistribution terms.
3. Resolve the polarity-MOSFET annotation/model mismatch (IRF4905 vs irf7328).
4. Identify real capacitor ESR/tolerance and complete appropriate physical measurements.
5. Determine whether capacitor-free operation remains a design target requiring changes; current evidence does not establish it.

## Read the comparisons

[Output capacitor absent / 1 uF / 10 uF](../simulation/tests/SIM-09_loop_stability/results/output_cap_options/README.md).

[Load sensitivity](../simulation/tests/SIM-09_loop_stability/results/load_sensitivity/README.md).

[Series resistance and capacitance sensitivity](../simulation/tests/SIM-09_loop_stability/results/cap_esr/README.md).

The explicit 1 ohm external resistor was confirmed after the initial sensitivity study. Historical labels `ESR` in filenames/metrics denote the modeled total series resistance; the 0.1 ohm test is hypothetical and does not represent the assembled branch.

## Local execution follow-up

SIM-01 (both modes) and the four nominal SIM-09 AC runs completed again in a separately assembled local folder. Twelve SIM-02 through SIM-08 schematics generated netlists. See [local review](../simulation/LOCAL_REVIEW.md) and [verification](local_execution_verification.json). Full cross-machine portability and model redistribution remain pending. Component/model corrections and report results remain subject to change after rerunning affected scenarios.
