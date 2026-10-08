# SIM-02: line_regulation

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

## Versión actual

Ambos modos del circuito completo calibrado están verificados: ver
[CALIBRATED_LINE.md](CALIBRATED_LINE.md). Banco físico preparado en
[MEAS-02](../../../measurements/MEAS-02_line_regulation/README.md), con diagrama,
plantillas y revisión de disipación/resolución. Medición pendiente.

Lo siguiente conserva antecedentes de simulaciones previas; no usar sus cifras
como resultados del escenario calibrado actual.

## Estado

Nueva comprobación del circuito completo, modo 5 V: 0.176193 mV/V entre 6 y
11 V de fuente. Figura y texto incorporados. Ver FULL_CIRCUIT.md para
condiciones, historias de los puntos y dificultad numérica del arranque a
10 V. El modo 3.3 V completo sigue pendiente.

Antecedentes de los bancos DC reducidos:

Datos extraídos, figura y texto integrados al informe. Resultados coinciden con las cifras de la tabla DC. La revisión identificó bancos reducidos distintos de SIM-01; falta validar el circuito completo actual. Ver BENCH_REVIEW.md.

## Fuentes

- `../../ltspice/TEST_DROPOUT.asc`: modo 5 V.
- `../../ltspice/TEST_DROPOUT_33V.asc`: modo 3.3 V.
- `results/imported_dc/`: copias de los esquemas, logs y raw originales del 13 de marzo de 2026; manifest.json registra origen y SHA-256. Los esquemas coinciden byte a byte con las copias organizadas.
- `extract_dc.py`: extrae los datos de los raw preservados, sin ejecutar LTspice. Produce exportaciones de 6 a 11 V y metrics.json.

## Condiciones y resultados

Barridos DC de VBAT: 4--11 V para modo 5 V y 3--11 V para modo 3.3 V, paso 1 mV, 27 C. Se usa el intervalo 6--11 V para regulación de línea.

Carga resistiva: 5 ohm en modo 5 V y 3.3 ohm en modo 3.3 V; corriente aproximadamente 1 A, no una carga de corriente constante.

| Modo | Vout a Vin=6 V | Vout a Vin=11 V | Pendiente entre extremos |
|---|---|---|---|
| 5 V | 5.0133605 V | 5.0077949 V | -1.113129 mV/V |
| 3.3 V | 3.3095429 V | 3.3038628 V | -1.136017 mV/V |

La tabla del informe presenta magnitudes positivas. Debe explicitarse |Delta Vout / Delta Vin|; la salida disminuye con la entrada en estos barridos. El valor típico anterior es la media de los extremos, no una medición a Vin=8 V.

Figura: docs/figures/SIM-02_line_regulation.pdf (también SVG/PNG), dos paneles Vout frente a Vin. make_figure.py reproduce la figura desde las exportaciones; figure_manifest.json registra sus hashes y herramientas. regenerate-figures.cmd incluye SIM-02. La tabla indica las cargas y el cálculo, y ya no presenta la media de extremos como valor típico.
