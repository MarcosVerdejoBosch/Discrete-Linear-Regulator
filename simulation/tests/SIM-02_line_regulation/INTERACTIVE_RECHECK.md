# SIM-02 3.3 V: interactive execution recheck

## Observed problem

On 2026-09-24, the user reported that opening SIM-02_calibrated_line_33V.asc and pressing Run stopped advancing near 28.2 ms. The desktop log repeatedly reported Heightened Def Con around 28.2205 ms. Its ASC and circuit netlist matched the validated version, apart from the netlist's source path; compared external model files also matched.

The unchanged ASC completed again in batch with Normal. Thus the earlier completed result remains valid, but did not demonstrate reliable interactive execution. The exact internal cause of the different numerical trajectories has not been isolated.

## Change and verification

Only the 3.3 V line-regulation case now includes `.options itl4=100`. Component values, stimuli, 320 ms stop time, 2 us maximum timestep and accuracy tolerances were not changed. The generator preserves this setting. ITL4 is the transient iteration limit per time point; see [Analog Devices simulator option reference](https://github.com/analogdevicesinc/ltspice-reference/blob/main/ai_ref/SIMULATION-COMMANDS-REFERENCE.md).

The modified ASC completed 320 ms in interactive mode (launched with `-norm -Run`, without `-b`) on LTspice XVII 17.1.15, using the local preferences. The unchanged batch control also completed. This is a local verification, not a guarantee for every LTspice version or preference combination.

All seven final-10-ms output means differed from the published reference by at most 0.0425 uV. The reported line-regulation conclusions and rounded table values therefore remain unchanged. These small differences describe numerical repeatability, not physical measurement accuracy.

See [comparison and file hashes](results/interactive_recheck/comparison.json) and the two completion logs beside it. The redundant modified batch attempt was stopped deliberately while the same variant continued interactively; it is not counted as a completed run.

## User action

Stop the old stalled run, close its schematic, and reopen the updated ASC. Use Normal solver, or choose entry 4 in ELEGIR_SIMULACION.cmd. No component edits are needed.
