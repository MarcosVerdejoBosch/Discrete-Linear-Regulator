# U17: IRF4905 correction and initial SIM-01 verification

**Follow-up:** [full primary-scenario revalidation](U17_REVALIDATION_2026-09-24.md) supersedes the pending-rerun status in this initial comparison. Numerical diagnostics below are retained for traceability.

The builder identified U17 as IRF4905. SIM-01 through SIM-08 sources now assign irf4905 to U17; other IRF7328 devices are unchanged. SIM-01 completed in both modes. The 32 corrected ASC files generated netlists successfully. SIM-02 through SIM-08 numerical results and report figures remain the prior baseline pending reruns. SIM-09 is unchanged.

## Model and connections

[Official Infineon model](https://www.infineon.com/assets/row/public/documents/24/50/irf4905.spi?fileId=5546d462533600a4015356faeff336bb), generated 1996-06-19, SPICE3. SHA256: D6363459B4A5086A3F91CD0C973636CA1A4E38215D85DF5D3463C37AF85849F0.

Drain/gate/source order matches the existing symbol. The generated instance is `XU17 VBAT N063 VEE irf4905`. Only U17 model assignment and its model-file attribute change. Other devices and external wiring remain unchanged. The model is downloaded from the supplier with original copyright notices, not republished under MIT.

## Completed comparison

Both old-model baselines completed 140 ms using Normal solver. New 5 V completed using Normal; new 3.3 V completed using Alternate. Both new runs include startup, shutdown and restart. The 3.3 V comparison changes solver as well as model and is not an isolated model sensitivity measurement. Conditions: 8 V source, 50 ohm load in 5 V and 33 ohm in 3.3 V, 27 C, 2 us maximum step, unchanged tolerances.

| SIM-01 5 V metric | Previous model | IRF4905 |
|---|---:|---:|
| Settled output, 45-55 ms | 5.000019 V | 5.000019 V |
| Time from connection to 98% output | 29.187665 ms | 29.187459 ms |
| Sampled pre-enable peak | 0.853778 V | 0.855568 V |
| Disconnection to below 50 mV | 0.393938 ms | 0.393435 ms |

Extra digits support numerical comparison, not hardware accuracy. [Machine-readable results](../simulation/tests/SIM-01_startup_shutdown/u17_review/comparison.json).

## Convergence checks and selected solver

Normal stalled near 105.929 ms during restart; a separate 1 us / trtol=1 control stalled near 105.902 ms. Both were stopped and partial RAW/log files retained locally. They are not completed evidence. Gear also stalled near 28.245 ms and was stopped. Alternate completed all 140 ms: settled output 3.3000019 V, restart output 3.3000018 V, pre-enable peak about 0.84497 V. Numerical convergence difficulty alone does not establish physical instability.

SIM-01 launchers now select Normal for 5 V and Alternate for 3.3 V. Rerun affected SIM-02 through SIM-08 scenarios before updating report results. No component value was changed to hide the issue.

## Reproduction

Prepare the ordinary workspace: the canonical SIM-01 sources already include the accepted correction. The copies in `simulation/tests/SIM-01_startup_shutdown/u17_review` preserve the initial comparison. Run `simulation/get_irf4905.ps1 -Destination "PATH_TO_PREPARED_FOLDER"` with PowerShell to fetch and hash-check the official model. The helper download was tested successfully. Run 5 V with Normal and 3.3 V with Alternate, or use the canonical SIM-01 launchers in the prepared folder.
