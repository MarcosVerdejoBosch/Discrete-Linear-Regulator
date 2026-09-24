# U17 revalidation — 2026-09-24

All **16 primary scenarios** completed locally with LTspice **17.1.15 x64**. U17 uses the official IRF4905 model in the full circuit, matching the part identified by the builder. The report figures and tables were regenerated from the accepted runs. This aligns the simulated component identity; it does not establish real parasitics, thermal behavior or production tolerances.

## Execute and review

Follow the [three-step preparation](../simulation/QUICKSTART.md), then use `ELEGIR_SIMULACION.cmd`. No Python is required to view the LTspice curves. The selector uses the solver below and preserves earlier run outputs. Maximum time steps and any additional options are stored in each schematic. External model dependencies still require the initial preparation.

| Primary scenario | Solver | Local result |
|---|---|---|
| SIM-01 | Arranque, apagado y reinicio | 5 V | Normal | Complete |
| SIM-01 | Arranque, apagado y reinicio | 3.3 V | Alternate | Complete |
| SIM-02 | Regulacion de linea | 5 V | Normal | Complete |
| SIM-02 | Regulacion de linea | 3.3 V | Normal | Complete |
| SIM-03 | Regulacion de carga | 5 V | Normal | Complete |
| SIM-03 | Regulacion de carga | 3.3 V | Normal | Complete |
| SIM-04 | Limite inferior con protecciones | 3.3 V | Alternate | Complete |
| SIM-05 | Consumo sin carga | 5 V | Normal | Complete |
| SIM-05 | Consumo sin carga | 3.3 V | Alternate | Complete |
| SIM-06 | Escalon de carga | 5 V | Normal | Complete |
| SIM-06 | Escalon de carga | 3.3 V | Alternate | Complete |
| SIM-07 | UVLO y OVLO | 5 V | Normal | Complete |
| SIM-08 | Limite de corriente y recuperacion | 5 V | Normal | Complete |
| SIM-08 | Limite de corriente y recuperacion | 3.3 V | Alternate | Complete |
| SIM-09 | Ganancia de lazo | 5 V | Alternate | Complete |
| SIM-09 | Ganancia de lazo | 3.3 V | Alternate | Complete |

SIM-04 in 5 V reuses the falling-input portion of SIM-07, so it is not a seventeenth entry. SIM-09 retains two interactive ASC files, one per output mode, each with both Tian injections.

## Main results after U17 correction

- SIM-01: settled outputs 5.000019 V / 3.300002 V; sampled pre-enable peaks 0.856 V / 0.845 V.
- SIM-02: endpoint line-regulation magnitudes 0.159 / 0.319 mV/V.
- SIM-03: endpoint load-regulation magnitudes 0.017 / <0.001 mV/A. The small 3.3 V endpoint difference does not mean zero variation at intermediate loads; the figure shows those points.
- SIM-04 with nominal thresholds: source voltage at the 98% output crossing is approximately 5.823 V in both modes. This is enable-limited shutdown, not intrinsic dropout.
- SIM-05: total enabled near-no-load input current 56.9 / 56.0 mA, including auxiliaries.
- SIM-06: undershoot 172.2 / 164.8 mV and overshoot 362.7 / 361.1 mV for the specified resistive load steps.
- SIM-07: comparator hysteresis approximately 0.364 V for UVLO and 0.868 V for OVLO; system enable thresholds are analyzed separately.
- SIM-08: sustained 50 milliohm short current approximately 1.474 A in both modes; brief peaks remain visible and are not a thermal rating.
- SIM-09: nominal phase margins 52.51 / 51.98 degrees and gain margins 17.28 / 17.75 dB. The unchanged fixed-bias core has no U17. Full-circuit tone cross-checks with IRF4905 differ from the matching AC voltage-return quantity by less than 0.04 dB and 1.3 degrees.

Extra digits in machine-readable results support traceability, not claimed hardware accuracy. [Current report](../docs/regulator.pdf), [scenario index](../simulation/README.md), [source/result hashes](u17_revalidation_manifest.json).

## Supplementary runs

**Not yet frozen:** the additional 1 us load-refinement checks and the older 142 ms deep-brownout protocol down to 2.8 V remain unresolved. The separately executed 120 ms / 4 V adjusted-threshold tests completed in both modes. Their [current results](../simulation/tests/SIM-04_dropout/IRF4905_RESULTS.md) are distinct from the older diagnostic. The updated report uses the completed nominal sweeps and fixed-input dropout holds; it no longer carries the previous model's unconfirmed refinement claim.

These are separate from the 16 primary selector entries. Only rows marked complete are accepted new evidence. Earlier result notes and plots for unresolved variants remain historical and must not be read as revalidated IRF4905 results.

| Supplementary scenario | State | Accepted solver |
|---|---|---|
| `SIM-03_load_stepcheck_33V` | incomplete | — |
| `SIM-03_load_stepcheck_5V` | incomplete | — |
| `SIM-04_adjusted_33V` | complete; 120 ms / 4 V protocol | alt |
| `SIM-04_adjusted_5V` | complete; 120 ms / 4 V protocol | norm |
| `SIM-04_adjusted_settled_5V` | complete | norm |
| `SIM-04_driver_thermal_5V` | complete | norm |
| `SIM-04_pulsed_load_5V` | complete | norm |
| `SIM-04_pulsed_load_inhibit_5V` | complete | norm |
| `SIM-09_full_tone_33V` | complete | alt |
| `SIM-09_full_tone_5V` | complete | norm |

Fixed-input 5 V holds confirm approximately 100 mV output loss at a 4.95 V source with adjusted thresholds. The corresponding driver calculation retains **R21 = 10 ohm**: about 147 mA pass-base current and 0.35 W in Q3. The historical R21 = 100 ohm alternative is not the implemented design. Switching only the external load does not guarantee low driver dissipation between pulses.

## Numerical checks and limits

Completed evidence requires both a finished LTspice log and the intended final simulation time. Analysis checks include settled windows, enable state, voltage/current relationships and event ordering as applicable. Failed or stopped attempts remain in the private evidence archive; partial waveforms do not replace complete results.

The accepted 3.3 V SIM-03 run uses `itl4=100`, as does the 3.3 V full-circuit tone check. This increases iterations per time point without changing components or the specified accuracy tolerances. Solver selection also matters for this model set. See the [Analog Devices convergence guide](https://analogdevicesinc.github.io/ltspice-reference/ai_ref/TROUBLESHOOTING-GUIDE.html). Comparisons involving different solvers are not isolated model-sensitivity experiments.

The original SIM-01 fine-step comparison belongs to the previous U17 model. Its unsuccessful new-model attempt is not claimed as completed. The fixed-bias SIM-09 load/capacitance studies are unchanged; in particular, capacitor-free near-no-load instability and the non-universal effect of 10 uF are retained.

## Reproduction evidence

A fresh prepared folder matched all 16 primary sources, produced all 16 netlists and contained all waveform profiles. Both SIM-09 modes were executed through their launchers. Selected line, idle-current and load-step profiles were also opened and inspected in LTspice. This is a local preparation check, not a test on a second computer.

Physical validation remains pending beyond the builder's existing 5 V / 3.3 V output measurements. The report remains subject to measured ESR, wiring, temperature, instrument uncertainty and any resulting design changes.
