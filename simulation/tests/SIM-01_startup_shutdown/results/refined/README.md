# SIM-01 numerical refinement — 2026-09-18

Resolved for the documented scenario: Normal solver, maximum timestep 1 us,
explicit `.options trtol=1`, unchanged circuit and load. Both modes complete
140 ms. No invented ESR, added parasitic capacitance, or looser reltol was
needed. Netlist comparison against the earlier 1 us files shows only the
new trtol directive (apart from the source filename).

Accepted original runs:

- 5 V: `SIM-01_trtol_5V`, 140.0004605 ms endpoint.
- 3.3 V: `SIM-01_finalcheck_33V`, full record and completed log.

Copies promoted to `SIM-01_check_step_<mode>` retain original names inside
their log headers. `accepted_sources.json` records that provenance;
`manifest.json` hashes all archived attempts. `comparison.json` gives complete
metrics and differences against the unchanged nominal 2 us runs.

Diagnostic history (incomplete trials are not accepted evidence):

- Earlier default-control 1 us trials stalled around 68.5 ms; retained in previous_fine.
- `refined`: reltol=1e-4, still slow/stalled at 105.934 ms (5 V) and 84.579 ms (3.3 V), stopped.
- `precision`: reltol=1e-5, stopped for impractical speed near 10.8/13.6 ms; this does not establish a convergence failure.
- `trtol_5V`: complete, accepted.
- `trtol_33V`: manually interrupted at 115.18 ms after a period of slow progress near 105.927 ms. It had recovered; its log message alone was not proof of a permanent stall. Repeated to completion as `finalcheck_33V` with the same settings.
- `trtol_alt_33V`: optional alternate-solver run, stopped once both Normal-solver records completed; not needed for acceptance.

The first precision trial had an invalid text encoding and was regenerated
with cp1252 units preserved before the archived runs. Those initial failed
files are not used. Installed LTspice also rejected `debugtran`; it was removed
before the archived reltol trials. No global application settings were changed.

Largest refined timing difference: 1.452 us. Largest initial-pulse difference:
0.322 mV. Reconnection pulse in 5 V differs by 19.2 mV (about 1.7%); do not
claim a precise hardware peak from it. Reported figures show first startup
and first shutdown, whose displayed precision is supported by this check.

User review and eventual bench measurement remain separate from this numerical check.
