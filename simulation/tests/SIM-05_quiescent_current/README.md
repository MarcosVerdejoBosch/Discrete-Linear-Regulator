# SIM-05: Enabled near-no-load consumption

Complete calibrated circuit verified at 8 V and 27 C, with a 1 Mohm external
load in both modes. Mean source currents: 56.9 mA (5 V) and 56.0 mA (3.3 V).
These include all auxiliary blocks and the small external load; not shutdown.

See [conditions and results](CALIBRATED_IDLE.md),
[metrics](results/calibrated/metrics.json), and
[supporting waveform](../../../docs/figures/SIM-05_calibrated_idle.pdf).

Scenarios are SIM-05_calibrated_idle_5V.asc and SIM-05_calibrated_idle_33V.asc
in simulation/ltspice. Preparation/analysis/plot scripts, raw/log/net/asc
archives, hashes, netlist differences and CSV exports preserve traceability.

Historical TEST_IQ.asc is unchanged. Its previous report values have been
replaced by this completed full-circuit test.
