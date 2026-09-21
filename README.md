# Discrete Linear Regulator

A largely discrete linear regulator with selectable **5 V / 3.3 V outputs**, a fabricated PCB, and documented LTspice studies.

**Review snapshot — September 2026.** The assembled board has produced both output voltages. Detailed bench characterization remains pending. Numerical results below are simulations, not hardware specifications.

## Start here

- **[Read the report (PDF)](docs/regulator.pdf)** — architecture, implementation, simulation results and limitations.
- [Simulation index](simulation/README.md) — SIM-01 through SIM-09.
- [What is verified and what remains](publication/REVIEW_STATUS.md).
- [Current organized KiCad project](hardware/kicad/Regulador.kicad_pro), [schematic](hardware/kicad/Regulador.kicad_sch), [PCB](hardware/kicad/Regulador.kicad_pcb).
- [Original published KiCad snapshot](hardware/legacy-github/) — retained separately; it differs from the organized copy.

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

**LTspice execution from a clean clone is not yet verified.** Third-party models are not bundled; see [external model dependencies](simulation/EXTERNAL_MODELS.md). Large RAW files and duplicate simulator logs remain in the local evidence archive. SHA256 records refer to those original files. Some analysis scripts require the RAW archive; preparation scripts may require additional original baseline files. Selected CSV exports support inspection without LTspice.

Scenario copies use model filenames in place of machine-specific absolute include paths. Numerical validation predates that packaging-only change; [the manifest](publication/manifest.json) records original and exported hashes. This is a review snapshot, not a fully portable release or a frozen hardware specification.

## License

The repository's existing [MIT license](LICENSE) is retained for project-owned material. Third-party component models and cited publications retain their own terms and are not relicensed by this repository.
