# PCB documentation status

## Confirmed

- The repository PCB is byte-identical to the builder's final desktop KiCad PCB at this review (SHA256 `7f70b1153bd202565e5f7471c31c86c702fb2748de2014b0acfa6eefc1dd15bb`).
- Four copper layers. The board-edge bounding box, including its drawing stroke, is 200.05 × 160.05 mm; the report uses approximately 200 × 160 mm.
- Both inner layers contain ground-connected copper zones. This observation alone does not establish noise, thermal or current-handling performance.
- The builder confirmed fabrication by JLCPCB, separate component procurement and manual soldering.
- The builder identifies the current KiCad files as the final design after iterations. The installed BOM still requires reconciliation.
- Initial 5 V and 3.3 V output checks were reported by the builder. Detailed hardware characterization remains pending.

## BOM review

The two local workbooks `2.0ReguladorBOM.xlsx` and `2.0ReguladorBOM - Copy.xlsx` have identical cell contents across the populated 69 × 8 area of their `2.0ReguladorBOM` sheet. Neither filename independently establishes an as-built revision. Both specify Q8/Q21 generically as `PJFET` in E64, while the PCB identifies J175. Some connector/power-device references also require mapping to the current PCB references. The older `ReguladorBOM.xlsx` includes earlier values and alternative-value annotations.

The workbooks were read without modification. They are not yet published as a definitive manufacturing BOM.

## Placement figure and layout rationale

On 2026-10-11 the builder confirmed that four layers were selected for electromagnetic-compatibility and circuit-noise considerations and easier signal/power routing. The inner layers serve as the GND reference; the outer layers carry supply and signal routing. Inspection also shows ground copper on the outer layers. This records design intent, not measured EMC or noise performance.

`docs/figures/pcb_placement.pdf` is a vector export of the final board's front silkscreen and outline, with six numbered landmarks: amplifier arrays U1-U3, feedback trimmers RV1/RV2, Q_PASS, U4, U7 and Q_POL. Leader lines identify components, not block boundaries. References are those of the PCB and must not be assumed identical to LTspice references. The figure replaces the stacked copper illustration in the report to keep the section concise; the original `coopper.pdf` remains available unchanged.

Regenerate with Python, KiCad 9 CLI, pypdf, reportlab and pypdfium2:

```text
python docs/tools/generate_pcb_placement.py --kicad-cli "path/to/kicad-cli"
```

The script reads the board without modifying it. Annotation coordinates refer to this revision and need review after any layout change.

## Routing maps

`docs/figures/pcb_routing.pdf` complements placement with a full-board supply/output map and a magnified feedback/reference map. Geometry comes from KiCad's read-only pcbnew API: actual tracks (including arcs), vias, and saved filled zone polygons, with holes retained. F.Cu and B.Cu are projected together from above; GND fills are omitted. Other nets and the original front silkscreen provide muted context. Pad centers are marked by circles, not reproduced as manufacturing pad shapes. Filled copper is translucent for readability. The map is an explanatory figure, not a fabrication output or a current-density/EMC result.

The power paths are VCC (input), VEE (after Q_POL), VCTRL (startup output/pass emitter), and the collector-to-Rsns-to-OUT path. The last path contains two distinct nets, deliberately sharing a color across Rsns. The detail shows OUT, FB to U1 pin 11, and VREF plus the separate net after R44 to U1 pin 14. No bridge is drawn across those resistors. `PCB_NET_MAP_EVIDENCE.json` records the PCB hash, KiCad version, geometry counts and exact connected pads for the selected nets. VCC and VREF have saved copper zones but no track segments; a track-only illustration would omit their connections.

To regenerate (temporary output names below are examples):

```text
<KiCad Python> docs/tools/extract_pcb_nets.py geometry.json
kicad-cli pcb export pdf --layers F.Silkscreen,Edge.Cuts --mode-single --black-and-white -o silkscreen.pdf hardware/kicad/Regulador.kicad_pcb
python docs/tools/generate_pcb_routing.py geometry.json --silkscreen silkscreen.pdf
```

No board save or zone refill is performed. Review the crop and explanatory labels if the layout changes. The report includes only these two complementary maps, rather than repeating every net individually.

## Component-level routing atlas

Four additional maps are included in the report and collected in
`docs/figures/pcb_subcircuit_atlas.pdf` for full-size review:

- `pcb_power_path.pdf`: INPUT -> Q_POL -> Q4B -> Q_PASS -> Rsns -> OUTPUT, with the external supply/load and conceptual GND return in a separate flow strip.
- `pcb_current_sense.pdf`: differential pickup through R33/R34, U4A amplification, R40/RV13 and U4C threshold, and U4B/R42/D5 limiting action.
- `pcb_enable_control.pdf`: permission signals, Q25-Q27/Q23 logic, Q6 gate control, Q4A and R21 pass-base drive.
- `pcb_startup_control.pdf`: Q4B, Q14/Q15, C11/R58 feedback and the VCTRL/C12 output.

Selected components use the actual footprint graphics from F.Fab, falling back to F.Silkscreen when fabrication graphics are absent. A stronger colored contour with a subtle halo makes each footprint recognizable; the former pad-envelope boxes are removed. References remain bold with no white background. The atlas background is exported without reference designators to avoid duplicate labels. These outlines describe the footprint, not a 3D component model. Pad markers are not to scale. Both outer copper layers are projected together, GND fills are omitted, and all crops are explicitly illustrative. The power figure distinguishes the two sides of Rsns with different colors. Other figures group several separate nets along a functional signal path without inventing copper connections across components.

Q4 units were verified against the KiCad schematic symbol: section A uses gate pin 2 and source/drain pins 1/7; section B uses gate pin 4 and source/drain pins 3/5. Unconnected duplicate pins in the custom symbol are not presented as additional paths. Names and pins in `PCB_SUBCIRCUIT_EVIDENCE.json` come from the final PCB, not from matching LTspice reference strings.

Regenerate all four maps and their atlas after extracting the geometry. Use a separate silkscreen export without reference designators for these component-highlight views; the original routing overview still uses the export with references:

```text
kicad-cli pcb export pdf --layers F.Silkscreen,Edge.Cuts --mode-single --black-and-white --exclude-refdes -o subcircuits-base.pdf hardware/kicad/Regulador.kicad_pcb
python docs/tools/generate_pcb_subcircuits.py geometry.json --silkscreen subcircuits-base.pdf
```

The 3D presentation is a subsequent task. These figures do not modify the board or its fabrication outputs.

## Remaining evidence

A clear top-side photograph of the assembled prototype remains pending from the builder; an underside photograph can supplement it if useful. No further placement intent (such as optimized feedback isolation or measured return-path performance) is inferred solely from the routing.

Do not add measured thermal limits, quantified regulation accuracy or fabrication specifications that have not been confirmed.
