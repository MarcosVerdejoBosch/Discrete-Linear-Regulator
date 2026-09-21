# Índice de simulaciones

Revision antes de congelar: [estado de esta version](../publication/REVIEW_STATUS.md).

Los identificadores son estables. Los nombres originales se conservan para mantener la trazabilidad y las dependencias. No todos los ensayos están revisados.

| ID | Escenario | Archivo fuente | Estado |
|---|---|---|---|
| SIM-01 | startup_shutdown | [5 V](ltspice/SIM-01_calibrated_startup_5V.asc), [3.3 V](ltspice/SIM-01_calibrated_startup_33V.asc) | Nueva calibracion; corridas nominales y control fino de 140 ms completos en ambos modos (1 us, trtol=1). Revision personal pendiente; ver tests/SIM-01_startup_shutdown/CALIBRATED_STARTUP.md. |
| SIM-02 | line_regulation | [5 V](ltspice/SIM-02_calibrated_line_5V.asc), [3.3 V](ltspice/SIM-02_calibrated_line_33V.asc) | Circuito completo calibrado, ambos barridos verificados; figura y tabla actualizadas. Ver tests/SIM-02_line_regulation/CALIBRATED_LINE.md. |
| SIM-03 | load_regulation | [5 V](ltspice/SIM-03_calibrated_load_5V.asc), [3.3 V](ltspice/SIM-03_calibrated_load_33V.asc) | Circuito completo calibrado, cinco cargas verificadas y control de paso temporal completado. Figura y tabla integradas. Ver tests/SIM-03_load_regulation/CALIBRATED_LOAD.md. |
| SIM-04 | dropout / lower input boundary | [3.3 V](ltspice/SIM-04_calibrated_input_33V.asc), [5 V reused from SIM-07](ltspice/SIM-07_calibrated_protection_5V.asc) | Verificado: retardo/enable apaga antes de observar dropout intrínseco. Umbral dinámico de fuente 5.814 V en ambos modos; no equivale a dropout. Ver tests/SIM-04_dropout/CALIBRATED_INPUT.md. Variante 100 mA con RV10=100k / RV12=47k: caída de regulación observable en 5 V y confirmada con entrada fija; 3.3 V limitado por UVLO. Revisión térmica de Q3/R21 pendiente antes del banco: [detalle](tests/SIM-04_dropout/ADJUSTED_THRESHOLDS.md). |
| SIM-05 | quiescent_current | [5 V](ltspice/SIM-05_calibrated_idle_5V.asc), [3.3 V](ltspice/SIM-05_calibrated_idle_33V.asc) | Consumo total habilitado con carga 1 MOhm verificado: 56.9 / 56.0 mA. Tabla actualizada. Ver tests/SIM-05_quiescent_current/CALIBRATED_IDLE.md. |
| SIM-06 | load_transient | [5 V](ltspice/SIM-06_calibrated_transient_5V.asc), [3.3 V](ltspice/SIM-06_calibrated_transient_33V.asc) | Circuito completo calibrado, cambios 0.1--1 A con transición 1 us; resolución local <20 ns. Figura, texto y tabla verificados. Ver tests/SIM-06_load_transient/CALIBRATED_TRANSIENT.md. |
| SIM-07 | uvlo_ovlo | [Circuito completo 5 V](ltspice/SIM-07_calibrated_protection_5V.asc) | Ciclos completos verificados; umbrales dinámicos de comparadores separados del enable. Figura y tabla integradas. Ver tests/SIM-07_uvlo_ovlo/CALIBRATED_PROTECTION.md. |
| SIM-08 | current_limit | [5 V](ltspice/SIM-08_calibrated_limit_5V.asc), [3.3 V](ltspice/SIM-08_calibrated_limit_33V.asc) | Sobrecarga, corto 50 mOhm y recuperación completados; figura y tabla integradas. Ver tests/SIM-08_current_limit/CALIBRATED_LIMIT.md. |
| SIM-09 | loop_stability | [5 V voltage injection](ltspice/SIM-09_ac_5V_voltage.cir), [3.3 V voltage injection](ltspice/SIM-09_ac_33V_voltage.cir) | Doble inyección de Tian completada con polarizaciones fijas, ~1 A. PM 52.5/52.0 grados, GM 17.3/17.8 dB. Ver método, inyección de corriente y validación en tests/SIM-09_loop_stability/REGULATION_LOOP.md. |

## Published snapshot

See [external model dependencies](EXTERNAL_MODELS.md). Original RAW/log archives are not bundled. Paths in historical methods describe the full local working archive, not a guarantee that every diagnostic artifact is included here. SIM-10 is outside this snapshot. The latest SIM-09 capacitor-free comparison is [here](tests/SIM-09_loop_stability/results/output_cap_options/README.md).
