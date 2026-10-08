# Simulations v1.0 — 2026-10-07

This baseline closes the simulation review: **16 principal selector entries and 20 additional SIM-09 operating conditions** were executed and accepted by Marco. It preserves the exact latest local ASC/PLT files, including the moved annotation. This is a versioned baseline; later report or hardware work may justify a new revision.

## Evidence

All 20 fresh local SIM-09 logs report completion. Netlists regenerated from the latest saved ASC files match the previous electrical netlists exactly after excluding comments and ordering. Phase/gain-margin differences from the figure data are below 0.00001 degree/dB. The source schematics, plots and result hashes are recorded in `SIMULATION_CLOSURE_2026-10-07.json`. No recalculation or alteration of the report figures was needed.

## Dropout decision

The 5 V adjusted-threshold test was executed by the builder. It remains useful as a diagnostic of the circuit's lower input boundary, not as an operating mode to implement. The adjusted 3.3 V and UVLO-bypass variants are retained for traceability and do not block this baseline. No intrinsic-dropout hardware specification is claimed. The nominal protection thresholds in the validated principal cases remain the reference.

## Recovery

GitHub preserves the schematics, plot profiles, bias files, analysis code, documented results and report sources/PDF. Public redistribution of all third-party models is still unresolved. The private `Congelado-36-2026-10-07.zip` additionally preserves the exact local dependencies, installed LTspice library and available RAW/log results, based on the earlier 16-case backup. That private ZIP is not uploaded to the public repository. A local ZIP is not confirmation of off-device backup or OneDrive synchronization; clean-machine restoration remains untested.

Open a prepared ASC and press Run; launchers are optional. Do not separate the models, symbols, bias files and PLT from their scenarios. Figure review is deferred by the user; detailed hardware measurements remain pending and are not implied by simulation acceptance.
