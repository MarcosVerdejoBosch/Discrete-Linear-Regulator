# Public download check — 2026-09-22

Public snapshot tested: `dd288d5`, downloaded without authentication from GitHub codeload and extracted into a new directory.

1. Ran the published `simulation/prepare_windows.ps1` against the existing local model folder. The default `LTspice-local` destination was created successfully.
2. Ran the published `run_sim09.ps1` for 5 V and 3.3 V with Alternate solver. Both logs reported completion and both RAW files were newly generated.
3. Recomputed the Tian return and margins from these new results with the published optional Python script: PM 52.51 / 51.98 degrees; GM 17.28 / 17.75 dB.

The checked ASC/BIAS/PLT files match the corrected interactive version previously inspected in LTspice and successfully executed by the builder. The launchers were tested without opening another viewer window; this download check verifies preparation, execution and numerical results.

This is **download + local model preparation + execution**, not a self-contained model bundle. The same existing third-party libraries were supplied locally. It is not a clean-machine dependency test and does not rerun SIM-02 through SIM-08 or establish physical performance.
