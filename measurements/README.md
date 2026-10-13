# Physical characterization plan

Status: **planned, not measured**. The board has produced 5 V and 3.3 V according to the builder. No heatsink is installed on the pass transistor. This plan starts with low current and does not qualify continuous high-current operation.

## Available equipment (builder-confirmed)

| Item | Available specification / role |
|---|---|
| UNI-T UTP3315TFL-II | Adjustable 0–30 V, 0–5 A supply; record CV/CC operation |
| UNI-T UT61E | DC voltage and cold resistance readings |
| OWON VDS1022 | Two-channel oscilloscope; save waveform data and screenshots |
| 47 ohm, 2 W | Pack of ten; low-current series combinations |
| 33 ohm, 2 W | Pack of ten; later approximately 100 mA at 3.3 V |
| 3 ohm, 10 W, 5% | One; high-current load, deferred |
| 0.1 ohm and 0.15 ohm, 2 W | Ten of each; possible future sensing resistors, not output loads |
| 1 Mohm, 0.25 W, 1% | Pack of fifty; not a useful power load |
| ESP32 | Planned switching control; board selection and firmware deferred |
| Pass-transistor heatsink | Not installed |

Supply identification: [manufacturer's UTP3300TFL-II series page](https://instruments.uni-trend.com/products/dc-power-supplies/UTP3300TFL-II). Quantities and resistor ratings above are from the builder's purchase list; verify markings and actual resistance before use.

## Bank A — static voltage, load and line regulation

```text
Supply + ---- PCB INPUT       PCB OUTPUT ---- load resistor chain ----+
Supply - ---- PCB GND -----------------------------------------------+
                             |        |
                             +-- DMM -+  Voltage mode: OUTPUT to GND
```

Connect the voltmeter across the output and ground, not in series. With one meter, measure input and output sequentially after settling and record the order. Use the PCB terminals rather than the supply display for input voltage. Supply current includes the regulator's auxiliary circuits and is not output-load current.

### Load choices

Nominal calculations below are preparation values, not measured results. Use the measured load resistance in the final calculation.

| Load | Build from available parts | I at 5 V | I at 3.3 V | Total load power at 5 V / 3.3 V |
|---|---|---:|---:|---:|
| 188 ohm | Four 47 ohm in series | 26.6 mA | 17.6 mA | 0.133 / 0.058 W |
| 94 ohm | Two 47 ohm in series | 53.2 mA | 35.1 mA | 0.266 / 0.116 W |
| 47 ohm | One resistor | 106.4 mA | 70.2 mA | 0.532 / 0.232 W |
| 33 ohm | One resistor | 151.5 mA | 100.0 mA | 0.758 / 0.330 W |
| 3 ohm | One 10 W resistor | 1.67 A | 1.10 A | 8.33 / 3.63 W |

The 3 ohm row is illustrative only: the regulator may enter current limiting, and transistor dissipation is a separate constraint from the resistor rating. Do not use it in the initial bank without a thermal plan.

### First session

1. With power off, record board revision, output-capacitor configuration and jumper settings. Measure the cold resistance of the four-resistor 188 ohm chain. Leave UVLO/OVLO and current-limit adjustments at their current calibrated settings.
2. Connect the 188 ohm load and voltage probes. Start at **8 V input** in one output mode. A **0.2 A input-current limit is a provisional commissioning setting**, not a regulator specification. If the supply enters CC, stop and investigate; the resulting waveform is not comparable to the ideal voltage-source simulation. Account for auxiliary current and inrush before changing this setting.
3. Begin with a short supervised observation. Check output voltage and oscillation with the scope, and monitor component temperature with an appropriate sensor before extending run time or increasing current. No permissible continuous duration has been established without a heatsink. Do not use touch as a junction-temperature measurement.
4. Record terminal Vin, Vout, supply current, CV/CC state, elapsed powered time, ambient temperature and available case-temperature reading. Power down before moving wires or changing load. Repeat for the other output mode.
5. After the thermal and waveform check, use 94 ohm to obtain a second static load point. Keep the same input voltage and calibration. Higher loads are conditional on that review.
6. A subsequent low-load line test can use 188 ohm and 7, 8, 9 and 10 V, provided the regulator stays enabled and within its thermal limits. Record actual input voltage and sweep direction. Do not retune potentiometers between points.

For perspective, the approximate load-related pass loss at 8 V is `(Vin - Vout) * Vout / Rload`: about 0.080 W (5 V) or 0.083 W (3.3 V) with 188 ohm, and twice those values with 94 ohm. These estimates exclude auxiliary/driver dissipation and do not establish a safe junction temperature. Confirm actual transistor conditions before expanding the operating range.

Calculate `Iload = Vout / Rload`, `Pload = Vout^2 / Rload`, and output changes between measured points. Cold resistance can change when hot; report that limitation. Do not claim microvolt-level agreement with simulations from a handheld-meter reading. Record the selected range and resolution and use the instrument's applicable accuracy specification when reporting uncertainty.

The low-current bank is a **bench variant**. Compare it against simulations with the same measured load and input conditions later; keep the 36 validated baseline simulations intact.

## Remaining banks and their order

| Order | Bank | Connections / evidence | Gate before proceeding |
|---|---|---|---|
| 1 | Static DC | Bank A, two output modes, measured load and terminal voltages | Temperature and waveform check |
| 2 | Startup and shutdown | Supply → high-side P-MOS switch → PCB; fixed load; CH1 at PCB input, CH2 at output | Assemble and verify input switch independently; measure actual edges |
| 3 | Load transients | Fixed load plus a switched resistor branch; CH1 at load-control signal, CH2 at output | Choose load levels from thermal results; validate switch and pulse duration |
| 4 | UVLO/OVLO | Slowly sweep supply with low load; record rising/falling thresholds and enable state | Check allowable input and dissipation; preserve calibration |
| 5 | Current limiting | Controlled load increase/pulses; record output voltage and current | Thermal review, suitable switching/load hardware and pulse limits |

For the input switch, the existing design proposal uses an IRF4905 with a BJT gate driver; [TI SLVA716A, section 3](https://www.ti.com/lit/an/slva716/slva716.pdf) is its topology reference. Parts and wiring will be finalized before construction. ESP32 is a control source, not a measurement instrument.

Both scope ground clips go to board GND. Do not put a ground clip on a high-side sense or gate node. With two channels, repeat captures to inspect internal supply or enable while retaining a common timing reference; repeated captures are not simultaneous measurements of all signals. Check USB/ground connections before connecting the scope and ESP32.

Dropout after changing the UVLO threshold remains an optional diagnostic with a clearly recorded temporary adjustment. It is not a required demonstration of the nominal protection configuration. Loop-gain measurement needs a separate injection/instrumentation plan and is not promised by these banks.

## Records and report

Use `static_dc_template.csv` for Bank A. Keep raw readings, waveform exports, screenshots, photographs and session notes under a dated session folder. Record wiring, actual component values, instrument settings and any departures from the plan. Blank fields mean not measured, never zero.

The report should include a compact bank diagram, conditions, uncertainty, representative measurements and comparison to matching simulations. Keep detailed assembly instructions and raw records here. The installed BOM and prototype photos remain pending; freezing the KiCad release does not close these tasks.
