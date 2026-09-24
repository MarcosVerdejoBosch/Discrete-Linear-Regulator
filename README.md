# Discrete Linear Regulator

A largely discrete linear regulator with selectable **5 V / 3.3 V outputs**, a fabricated PCB, and documented LTspice studies.

**Review snapshot â€” September 2026.** The assembled board has produced both output voltages. Detailed bench characterization remains pending. Numerical results below are simulations, not hardware specifications.

## Run in LTspice

**2026-09-24 revalidation:** all 16 primary SIM-01–SIM-09 scenarios completed locally with LTspice 17.1.15. U17 now uses the official IRF4905 model in the full-circuit cases; report figures and tables were regenerated. The SIM-09 fixed-bias core is unchanged and was rerun. [Scope, numerical settings and evidence](publication/U17_REVALIDATION_2026-09-24.md).

Download and extract this review branch, then double-click `PREPARAR_LTSPICE.cmd`. Select your existing project-model folder once. In `LTspice-local`, open `ELEGIR_SIMULACION.cmd` and choose a case: it selects the verified solver, runs LTspice and opens the saved curves. Windows and LTspice are required; Python is optional.

**External models are still required**; this is not a dependency-free download. The setup checks dependencies before creating the folder. [Three-step instructions and SIM-09 plots](simulation/QUICKSTART.md).

## Start here

- **[Read the report (PDF)](docs/regulator.pdf)** â€” architecture, implementation, simulation results and limitations.
- [Simulation index](simulation/README.md) â€” SIM-01 through SIM-09.
- [What is verified and what remains](publication/REVIEW_STATUS.md).
- [Current organized KiCad project](hardware/kicad/Regulador.kicad_pro), [schematic](hardware/kicad/Regulador.kicad_sch), [PCB](hardware/kicad/Regulador.kicad_pcb).
- [Original published KiCad snapshot](hardware/legacy-github/) â€” retained separately; it differs from the organized copy.

## Current stability finding

The nominal bench uses a 1 uF output capacitor and an **external 1 ohm series resistor**. Intrinsic capacitor ESR is additional and remains uncharacterized. The installed capacitor was identified by the builder as radial tantalum, sold as 1 uF / 35 V.

The fixed-bias regulation-core studies do **not** establish capacitor-free operation across the load range: without the external output capacitor, the near-no-load cases have negative loop margins and persistent oscillation in the corresponding transient checks. Increasing capacitance to 10 uF improves phase margin at approximately 1 A but reduces it near no load. This is not a universal recommendation for an unspecified electrolytic capacitor.

[Output-capacitor comparison and conditions](simulation/tests/SIM-09_loop_stability/results/output_cap_options/README.md).

## Repository structure

| Folder | Contents |
|---|---|
| `docs/` | Compiled report, LaTeX source, bibliography and report figures |
| `hardware/kicad/` | Organized board project |
| `hardware/legacy-github/` | Previously published board files, preserved for comparison |
| `simulation/ltspice/` | Selected scenario definitions and saved bias files |
| `simulation/tests/` | Methods, extracted metrics, selected CSVs, scripts and diagnostic comparisons |
| `publication/` | Snapshot status and provenance manifest |

## Reproduction status

The PDF is ready to read. LaTeX build instructions are in [docs/README.md](docs/README.md).

**A self-contained LTspice download is not yet available.** A [local preparation and verification workflow](simulation/LOCAL_REVIEW.md) uses the owner's existing models. Third-party models are not bundled; see [external model dependencies](simulation/EXTERNAL_MODELS.md). Large RAW files and duplicate simulator logs remain in the local evidence archive. SHA256 records refer to those original files. Some analysis scripts require the RAW archive; preparation scripts may require additional original baseline files. Selected CSV exports support inspection without LTspice.

Scenario copies use relative model filenames. A fresh prepared folder was checked against the accepted sources, all 16 primary netlists were generated, and both SIM-09 modes were exercised through the launchers. This is local reproduction evidence, not cross-machine qualification. The [original manifest](publication/manifest.json) is historical; the [current revalidation record](publication/U17_REVALIDATION_2026-09-24.md) identifies the new results. Hardware measurements remain pending.

## License

The repository's existing [MIT license](LICENSE) is retained for project-owned material. Third-party component models and cited publications retain their own terms and are not relicensed by this repository.
