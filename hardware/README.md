# Frozen PCB and schematic — hardware-v1.0

This is the final KiCad design identified by the builder. The PCB was manufactured by JLCPCB; components were purchased and soldered by the builder. The installed BOM still needs reconciliation. Initial 5 V and 3.3 V operation has been reported; quantitative characterization is pending.

## Download and open

[Download the KiCad package](https://github.com/MarcosVerdejoBosch/Discrete-Linear-Regulator/releases/download/hardware-v1.0/Discrete-Linear-Regulator-KiCad-v1.0.zip).

1. Install KiCad 9 with its standard libraries and extract the entire ZIP.
2. Open `hardware/kicad/Regulador.kicad_pro` and select the schematic or PCB editor.
3. For a read-only schematic, open `hardware/exports/Regulador_schematic.pdf`.

The schematic includes its symbol definitions and the board includes its placed footprints. Standard KiCad libraries provide the referenced 3D models. Library updates and design edits are outside the frozen baseline. The package excludes caches, personal settings, backups, redundant historical designs and large intermediate render files.

## Fabricated board reference

`hardware/manufacturing/Manufacturing_Regulador.zip` is the **unchanged archive the builder identified as the file sent to JLCPCB**. It contains 11 Gerber layers, the Gerber job file and two drill files. Preserve this archive as the fabrication reference; exporting a new set is not a replacement for the original.

The four copper layers are F.Cu, In1.Cu, In2.Cu and B.Cu. The internal layers provide ground reference planes; the external layers carry power and signals. Routing and 3D illustrations are available in the repository's report and [PCB documentation](https://github.com/MarcosVerdejoBosch/Discrete-Linear-Regulator/blob/codex/simulation-review-v0.1/hardware/PCB_DOCUMENTATION.md).

## Verification and scope

`hardware/HARDWARE_FREEZE.json` records SHA-256 hashes and checks. The three project files match the final desktop project byte for byte. The original manufacturing ZIP members match the saved desktop fabrication exports. KiCad 9.0.1 successfully exported the schematic PDF and board Gerbers without saving or refilling the board.

Nine Gerber layer streams match after removal of generated headers. The external copper layers have identical aperture definitions and compared geometric primitives, with different serialization order. Drill files were preserved and matched to the saved exports; regenerated drill equivalence was not tested. These checks establish archive traceability, not a claim of clean ERC/DRC or formal manufacturing qualification.

The release ZIP includes `SHA256SUMS.txt` for its payload. Release-level checksums also identify the downloadable archives. The source tag freezes this design independently of future report and measurement updates.

## Still open

- Confirm the actually fitted BOM, including substitutions and potentiometer values/settings.
- Photograph the assembled board.
- Perform and document bench measurements. See the repository's measurement guide.

Do not describe the source schematic's nominal values as a verified installed BOM. A future intentional design change should receive a new revision rather than replacing this release.
