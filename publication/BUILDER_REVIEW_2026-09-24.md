# Builder review — 2026-09-24

The builder reports having run all simulation scenarios successfully. This records execution confirmation, not an independent numerical review of every curve or physical validation.

Two explanatory comments edited in the builder's `SIM-01_calibrated_startup_5V.asc` were propagated verbatim to the 32 published SIM-01 through SIM-08 ASC files, including diagnostic variants: the error-amplifier diode during OVLO, and the output-discharge JFET. The existing VCTRL comment was unchanged. Only comments changed; electrical lines were compared and remained identical. SIM-09 files were excluded and their hashes remained unchanged. Historical result archives are preserved.

The builder confirmed that U17 is an IRF4905. Current full-circuit simulations still assign `irf7328` to this instance. This is now a confirmed model mismatch, pending import and verification of the IRF4905 model and rerunning affected scenarios. The present numerical baseline has not been silently relabeled as IRF4905 results.
