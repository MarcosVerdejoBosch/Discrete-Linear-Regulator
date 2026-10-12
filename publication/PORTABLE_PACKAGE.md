# Downloadable 36-case package

The [simulation package release](https://github.com/MarcosVerdejoBosch/Discrete-Linear-Regulator/releases/tag/simulations-package-v1.0) packages the author's accepted **16 principal cases and 20 external-capacitor SIM-09 cases**. The electrical baseline remains `simulations-v1.0` (`d26b998`); the package is a separate distribution revision.

Download **Regulador-36-LTspice-v1.0.zip** from the release assets. GitHub's automatically generated **Source code** archives are repository snapshots, not this assembled simulation package.

## Use

1. Install LTspice on Windows. The reference version is XVII 17.1.15.
2. Extract the entire ZIP into a writable local folder.
3. In `Simulaciones`, open a scenario ASC and press **Run**. Keep its adjacent PLT, symbols, models and bias files.

No CMD launcher, Python installation or manual import into the LTspice library is needed. The `LEEME.md` table lists the reference solver for each case. In LTspice XVII the solver is a global preference: **Tools → Control Panel → SPICE → Solver**, Normal or Alternate. Run does not automatically change it. The 20 external SIM-09 cases were also accepted by the author with Normal.

## Contents and fidelity

- 36 scenario ASC files and 36 matching PLT profiles, byte-identical to the accepted source snapshot.
- The two bias files referenced by SIM-09.
- The hierarchical `LG_single.asc`/`LG_single.asy` pair (a support block, not a 37th scenario).
- Declared model libraries and required symbols, with original notices preserved.
- A SHA256 manifest, short instructions and scenario/solver table.

The package excludes the simulator, RAW results, generated netlists/logs, historical copies, optional launchers and the four additional dropout/UVLO diagnostics. Libraries named by the schematics are retained intact to preserve model resolution. The original source folder and frozen baseline are unchanged.

LTspice XVII automatically inserts references to its installed `standard.bjt`, `standard.dio`, `standard.jft` and `standard.mos`. Those installed files were compared with the bundled copies. This is not certification that future LTspice library versions produce identical numerical results.

## Third-party dependencies

The project MIT license does **not** license third-party models or symbols. The owner explicitly requested publication of the supplied dependencies after review of their notices. This is not confirmation of redistribution permission from their respective authors. In particular, the National Semiconductor library contains a free-copy/distribution notice excluding resale; several other libraries contain copyright or proprietary notices without a redistribution grant found in the supplied files. No notices were removed and no vendor models were substituted.

## Verification

Packaging and download checks are recorded separately from the author's prior execution of all 36 cases. See `PACKAGE_DOWNLOAD_VERIFICATION.json` for the final downloaded-archive checks and the exact scope of reruns. Tests on this Windows installation do not constitute a test on another physical computer.

The anonymous download and all 113 payload hashes passed. All 36 schematics generated netlists with their dependencies present. The 22 AC cases and two complete-circuit startup cases were rerun successfully, with margins/output plateaus matching the reference. An additional interactive `-Run` test completed with Normal, without batch mode or a CMD launcher; this is not a claim of visual GUI inspection. The other 12 transient cases retain the author's prior validation and were checked for unchanged source and dependencies, rather than fully rerun.

This check corrected one stale catalog entry: **SIM-01 startup 3.3 V uses Normal**, matching the author's completed log. The Alternate trial slowed near 28 ms and was stopped; Normal completed the full 140 ms. No schematic, model or saved plot was changed.
