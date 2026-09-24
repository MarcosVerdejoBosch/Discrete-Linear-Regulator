# Local LTspice review

The circuit, real component identities and report results remain subject to revision. Preserve the current numerical baseline; rerun affected tests before changing report tables and figures. Local execution is not hardware validation.

## Recommended Windows setup

Use [QUICKSTART.md](QUICKSTART.md) and the root `PREPARAR_LTSPICE.cmd`. No Python is needed for native plots.

## Alternative Python preparation

`prepare_local.py` assembles a separate private folder from this repository and the owner's original model/symbol directory. It requires Python 3, the already installed LTspice libraries and the project-specific files listed in the script. It does not download models, establish redistribution rights or overwrite an existing destination.

```powershell
python simulation/prepare_local.py --models "PATH_TO_ORIGINAL_PROJECT_MODELS" --ltspice-lib "$env:LOCALAPPDATA/LTspice/lib" --destination "PATH_TO_NEW_PRIVATE_FOLDER"
```

The preparation includes the hierarchical `LG_single.asc`/`.asy` pair and changes the copied 2N7000 symbol's absolute model path to `phil_fet.lib`. No component values are changed. Normal built-in symbols still come from the installed LTspice application.

## First test: SIM-01

In the prepared folder, run `PROBAR_SIM01_5V.cmd`, then `PROBAR_SIM01_33V.cmd`. These launchers use Normal for 5 V and Alternate for 3.3 V following the IRF4905 update, wait for completion, check the log and open the RAW file. They assume LTspice is installed under `%LOCALAPPDATA%/Programs/ADI/LTspice`.

Waveform presets are provided. If traces are not restored automatically, add:

- `V(vbat)`: input after the supply switch.
- `V(vctrl)`: soft-start circuit output.
- `V(comp)`: UVLO/OVLO reference.
- `V(ttl)`: enable.
- `V(out)`: regulator output.

Conditions: 8 V source, 50 ohm / 33 ohm load, switch connection at 5 ms, disconnection at 55 ms, reconnection at 85 ms, stop at 140 ms. Inspect the initial pulse, enable delay, settled output, discharge and restart. Opening an ASC only displays the schematic; a completed simulation is a separate check.

See ../publication/U17_IRF4905_REVIEW.md for the current SIM-01 comparison and pending SIM-02 through SIM-08 reruns.

SIM-09 uses two injections and post-processing. Do not interpret a single injection plot as the Tian loop return. See the [method](tests/SIM-09_loop_stability/REGULATION_LOOP.md).

## Verification scope

The published sources were assembled with the owner's installed models on 2026-09-21. Primary SIM-02 through SIM-08 schematics generated netlists successfully. SIM-01 was rerun from its schematic and SIM-09's four nominal AC runs were rerun from CIR files. See [local verification results](../publication/local_execution_verification.json).

This check does not rerun every SIM-02 through SIM-08 transient or all diagnostic variants. Their earlier numerical evidence remains in the test folders. Third-party dependencies remain excluded from GitHub; another machine requires supplying them. The corrected SIM-09 magnitude/phase presets were visually checked in LTspice for both modes on 2026-09-22. The builder also confirmed successful execution. This statement does not extend to every other preset.
