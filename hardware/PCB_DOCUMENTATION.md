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

## Next report addition

A clear top-side photograph of the assembled prototype remains pending from the builder; an underside photograph can supplement it if useful. No further placement intent (such as optimized feedback isolation or measured return-path performance) is inferred solely from the routing.

Do not add measured thermal limits, quantified regulation accuracy or fabrication specifications that have not been confirmed.
