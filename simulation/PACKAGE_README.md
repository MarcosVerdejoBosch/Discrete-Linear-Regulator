# Discrete Linear Regulator — 36 validated simulations

1. Install LTspice on Windows. The reference version is XVII 17.1.15.
2. Extract the **entire ZIP** into a writable local folder.
3. Open a scenario `.asc` in `Simulaciones`, select its reference solver below, and press **Run**. The adjacent `.plt` file supplies the saved plot configuration.

No CMD launcher, Python installation or manual library import is required.
Do not open schematics inside the ZIP. Keep the extracted files together.
`LG_single.asc` is a hierarchical support block, not an additional scenario.

## Solver selection

In LTspice XVII, select **Tools → Control Panel → SPICE → Solver**, then **Normal** or **Alternate**, as listed below. This is a global application preference; opening an ASC does not select it automatically.

**Both SIM-01 startup scenarios use Normal.** The old Alternate entry for the 3.3 V startup was corrected after checking the accepted log and repeating the complete simulation.

If a run stalls, check the listed solver and available disk space. The author also executed all twenty external-capacitor SIM-09 cases successfully with Normal.

## Scope

The package contains 16 principal scenarios and 20 additional SIM-09 cases: two output settings, two load currents and five external-capacitance/series-resistance combinations. Cext is additional to the regulator's existing output capacitor and its discrete 1 ohm series resistor.

The ASC and PLT files are unchanged from the author's accepted baseline. The package includes required model libraries, symbols and two bias files. It excludes the simulator, RAW results, generated logs/netlists, historical copies and the four optional dropout/UVLO diagnostics. Physical-board characterization remains separate from simulation validation.

## Integrity and third-party notices

`MANIFEST.json` records the SHA256 hash of each simulation/dependency file. The ZIP's adjacent `.sha256` file records the archive hash.

Third-party models and symbols retain their original notices and are **not** covered by the project's MIT license. Redistribution permission has not been established for every supplied dependency. Libraries explicitly referenced by the schematics are retained intact to preserve their definitions and resolution order; vendor models have not been substituted.

## Scenarios

| File in Simulaciones | Reference solver |
|---|---|
