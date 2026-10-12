# SIM-08: Current limiting and recovery

## Estado de esta nota

**Registro anterior a la revalidacion IRF4905 del 2026-09-24.** Se conserva el metodo y la evolucion del estudio; las cifras y afirmaciones de convergencia de esta nota pertenecen a esa revision anterior. Consultar el [registro actual](../../../publication/U17_REVALIDATION_2026-09-24.md) y el [informe actualizado](../../../docs/regulator.pdf) para los resultados aceptados con U17 corregido. Los archivos de metricas de los casos completados se actualizaron; una variante historica no queda revalidada por compartir carpeta.

## Desarrollo anterior

## Current verified scenario

Complete calibrated circuit in both modes; overload, 50 mOhm short and recovery.
See [conditions, method and results](CALIBRATED_LIMIT.md).

- [5 V scenario](../../ltspice/SIM-08_calibrated_limit_5V.asc)
- [3.3 V scenario](../../ltspice/SIM-08_calibrated_limit_33V.asc)
- [Measured simulation metrics](results/calibrated/metrics.json)
- [Report figure](../../../docs/figures/SIM-08_calibrated_limit.pdf)

The preparation, analysis and plotting scripts are in this directory. Archived
raw data, logs, netlists, scenario copies, CSV signals and hashes are under
results/calibrated. The report separates sustained current from transient peaks.
Thermal capability and hardware behavior have not been validated by this test.

## Historical imported scenario

[TEST_AC_Short_Circuit.asc](../../ltspice/TEST_AC_Short_Circuit.asc) is retained
for traceability. Its previous report values have been replaced by SIM-08.
