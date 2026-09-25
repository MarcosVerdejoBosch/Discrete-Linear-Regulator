# SIM-04: Dropout and lower input boundary

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

Physical bench preparation: [MEAS-04 lower operating boundary](../../../measurements/MEAS-04_input_protection/LIMITE_INFERIOR.md).
Manual source adjustment and reduced load to be selected from available parts;
no bypass of protection and no intrinsic-dropout claim. Physical measurements pending.

The calibrated complete circuit was checked with all protections active.
The delay/enable path disables output before intrinsic dropout can be extracted.
Both modes cross 98% nominal output at approximately 5.814 V source voltage
for a descending 0.1 V/ms ramp; this is a dynamic shutdown boundary.

See [method and results](CALIBRATED_INPUT.md),
[metrics](results/calibrated/metrics.json), and
[supporting plot](../../../docs/figures/SIM-04_calibrated_input.pdf).

The 5 V data reuse the falling segment from SIM-07. The 3.3 V scenario is
SIM-04_calibrated_input_33V.asc. Scripts recreate/analyze/plot the test;
raw data, logs, netlists, CSV exports and hashes preserve traceability.

Historical TEST_DROPOUT.asc and TEST_DROPOUT_33V.asc remain unchanged.
Their earlier values are removed from the report pending an independently
controlled calibrated bench. No intrinsic dropout number is claimed here.

## Variante con potenciómetros dentro de su rango

RV10=100 kΩ y RV12=47 kΩ, con cargas de 50/33 Ω. En 5 V se observa
pérdida de regulación con enable activo, confirmada con mesetas de entrada.
En 3,3 V UVLO sigue actuando primero. Se identificó corriente de drive elevada
y queda pendiente revisar disipación de Q3/R21 antes de llevar este ensayo
a la placa. Ver [método, resultados y archivos](ADJUSTED_THRESHOLDS.md).

## Revisión térmica completada

La comprobación con corrientes de terminales da 352–353 mW en Q3 cerca de
dropout. No queda justificado el ensayo DC original con los montajes térmicos
de referencia. Una variante solo simulada con R21=100 Ω reduce Q3 a ~45 mW
y R21 a ~28 mW en las mesetas; no fue adoptada en la placa ni en el diseño.
Ver [revisión, supuestos y alternativas de banco](THERMAL_REVIEW.md).

**Decisión vigente (2026-09-20):** R21 se mantiene en 10 Ω / ¼ W por
instrucción de Marco. Los 100 Ω son una comparación histórica descartada;
el próximo banco conservará el circuito original. Ver THERMAL_REVIEW.md.

## Carga pulsada: comprobación completada

La carga pulsada sola no reduce la disipación de Q3 cerca del dropout:
permanece en ~352 mW aun retirando la carga externa. Una segunda corrida
con carga pulsada y bloqueo externo de TTL durante el descanso reduce Q3
a ~8,5 mW entre pulsos; durante la medición recupera la meseta original.
Ambas corridas completaron 210 ms. Se conserva R21=10 Ω / ¼ W.
Ver [método y resultados](PULSED_LOAD.md). La interfaz física y los tiempos
térmicamente admisibles todavía deben definirse; no repetir todavía el
pulso diagnóstico en la placa. El próximo paso es la interfaz ESP32/carga/bloqueo.
