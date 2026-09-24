# Índice de simulaciones

**Revalidacion U17 (2026-09-24):** las 16 entradas principales SIM-01 a SIM-09 completaron la ejecucion local. U17 usa IRF4905 en los circuitos completos. El informe y los resultados nominales fueron actualizados. [Alcance y evidencia](../publication/U17_REVALIDATION_2026-09-24.md).

**Empezar:** [preparacion con doble clic](QUICKSTART.md).

Revision antes de congelar: [estado de esta version](../publication/REVIEW_STATUS.md).

Los identificadores son estables. Los nombres originales se conservan para mantener la trazabilidad y las dependencias. El selector contiene los casos principales revalidados; los estudios complementarios e historicos se identifican por separado.

| ID | Escenario | Archivo fuente | Estado |
|---|---|---|---|
| SIM-01 | startup_shutdown | [5 V](ltspice/SIM-01_calibrated_startup_5V.asc), [3.3 V](ltspice/SIM-01_calibrated_startup_33V.asc) | Nueva calibracion e IRF4905; corridas nominales completas de 140 ms en ambos modos. El control fino anterior pertenece al modelo previo; ver tests/SIM-01_startup_shutdown/CALIBRATED_STARTUP.md. |
| SIM-02 | line_regulation | [5 V](ltspice/SIM-02_calibrated_line_5V.asc), [3.3 V](ltspice/SIM-02_calibrated_line_33V.asc) | Circuito completo calibrado, ambos barridos verificados; figura y tabla actualizadas. Ver tests/SIM-02_line_regulation/CALIBRATED_LINE.md. |
| SIM-03 | load_regulation | [5 V](ltspice/SIM-03_calibrated_load_5V.asc), [3.3 V](ltspice/SIM-03_calibrated_load_33V.asc) | Circuito completo calibrado, cinco cargas verificadas; refinamiento adicional de paso temporal pendiente con IRF4905. Figura y tabla integradas. Ver tests/SIM-03_load_regulation/CALIBRATED_LOAD.md. |
| SIM-04 | dropout / lower input boundary | [3.3 V](ltspice/SIM-04_calibrated_input_33V.asc), [5 V reused from SIM-07](ltspice/SIM-07_calibrated_protection_5V.asc) | Verificado: retardo/enable apaga antes de observar dropout intrínseco. Umbral dinámico de fuente 5.823 V en ambos modos; no equivale a dropout. Ver tests/SIM-04_dropout/CALIBRATED_INPUT.md. Variante 100 mA con RV10=100k / RV12=47k: perdida de regulacion de 5 V confirmada con entrada fija; rampas acotadas de 8 a 4 V completas en ambos modos; en 3.3 V actua primero UVLO. Ver [resultados IRF4905](tests/SIM-04_dropout/IRF4905_RESULTS.md). Revisión térmica de Q3/R21 pendiente antes del banco: [detalle](tests/SIM-04_dropout/ADJUSTED_THRESHOLDS.md). |
| SIM-05 | quiescent_current | [5 V](ltspice/SIM-05_calibrated_idle_5V.asc), [3.3 V](ltspice/SIM-05_calibrated_idle_33V.asc) | Consumo total habilitado con carga 1 MOhm verificado: 56.9 / 56.0 mA. Tabla actualizada. Ver tests/SIM-05_quiescent_current/CALIBRATED_IDLE.md. |
| SIM-06 | load_transient | [5 V](ltspice/SIM-06_calibrated_transient_5V.asc), [3.3 V](ltspice/SIM-06_calibrated_transient_33V.asc) | Circuito completo calibrado, cambios 0.1--1 A con transición 1 us; resolución local <20 ns. Figura, texto y tabla verificados. Ver tests/SIM-06_load_transient/CALIBRATED_TRANSIENT.md. |
| SIM-07 | uvlo_ovlo | [Circuito completo 5 V](ltspice/SIM-07_calibrated_protection_5V.asc) | Ciclos completos verificados; umbrales dinámicos de comparadores separados del enable. Figura y tabla integradas. Ver tests/SIM-07_uvlo_ovlo/CALIBRATED_PROTECTION.md. |
| SIM-08 | current_limit | [5 V](ltspice/SIM-08_calibrated_limit_5V.asc), [3.3 V](ltspice/SIM-08_calibrated_limit_33V.asc) | Sobrecarga, corto 50 mOhm y recuperación completados; figura y tabla integradas. Ver tests/SIM-08_current_limit/CALIBRATED_LIMIT.md. |
| SIM-09 | loop_stability | [5 V: abrir y ejecutar](ltspice/SIM-09_loop_5V.asc), [3.3 V: abrir y ejecutar](ltspice/SIM-09_loop_33V.asc) | Doble inyección de Tian completada con polarizaciones fijas, ~1 A. PM 52.5/52.0 grados, GM 17.3/17.8 dB. Ver método, inyección de corriente y validación en tests/SIM-09_loop_stability/REGULATION_LOOP.md. |

## Published snapshot

See [external model dependencies](EXTERNAL_MODELS.md). Original RAW/log archives are not bundled. Paths in historical methods describe the full local working archive, not a guarantee that every diagnostic artifact is included here. SIM-10 is outside this snapshot. The latest SIM-09 capacitor-free comparison is [here](tests/SIM-09_loop_stability/results/output_cap_options/README.md).
