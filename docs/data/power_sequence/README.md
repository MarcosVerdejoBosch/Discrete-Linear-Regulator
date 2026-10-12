# Power-on and input-fault sequence

The approved figure combines the 5 V power-on window of SIM-01 (50 ohm load) with the undervoltage and overvoltage windows of SIM-07 (5 ohm load). These are separate experiments. It is not a new simulation.

The NPZ files contain every original sample in the plotted windows, including the original float32 voltage values and float64 times converted to milliseconds. No smoothing or decimation is applied. `sources.json` records the original RAW hashes and the hashes of the exported arrays. Those RAW hashes were checked against the accepted `metrics.json` manifests in `simulation/tests`. The selected channels and times are sufficient to regenerate the figure without the local RAW archive. Event positions come from those same accepted metrics.

Control traces are divided by the local VEE supply. Bands use a 50% VEE convention; transistor-logic thresholds are not inferred from those crossings. The initial output pulse remains in the data, but the dedicated SIM-01 initial-transient figure resolves it better.

From the repository root, with NumPy and Matplotlib installed:

```text
python docs/tools/generate_power_sequence.py
```

Outputs are `docs/figures/power_sequence.pdf`, `.png`, and `.svg`. The script verifies the input hashes before plotting. `figure_manifest.json` records the sources, windows, loads and processing. Detailed physical measurements remain pending.
