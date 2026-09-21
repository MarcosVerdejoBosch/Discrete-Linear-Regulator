# SIM-08: Current limiting and recovery

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
