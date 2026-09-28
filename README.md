# NeuroChip-Twin

**Reliability-Aware Early Prediction of Neural Network Development from
Microelectrode-Array Assays**

*Toward Functional Digital Twins for Neural Organ-on-Chip Screening*

NeuroChip-Twin asks whether DIV5 and DIV7 functional measurements from a rat
cortical neural microelectrode-array assay can predict DIV12 outcomes for unseen
chemicals—and whether calibrated uncertainty can identify cases that should
continue to the full assay.

The EPA source is a neural MEA assay, not an organ-on-chip dataset. The intended
application is decision support for functional readouts used in neural in-vitro
and organ-on-chip workflows.

## Current status

- Data feasibility gate: passed.
- Pre-registration: frozen at commit `8671fd84` before predictive results.
- Leakage controls and chemical-disjoint splits: passed (Gate D2).
- Registered B0--B4 benchmark: complete across five outer folds and three seeds.
- Gate B2: **STRONG**. B3 cleared every criterion on three of five endpoints.
- Next registered stage: M1 early-measurement + chemistry fusion, followed by
  uncertainty calibration and abstention.

See [`docs/neurochip_data_audit.md`](docs/neurochip_data_audit.md) for exact data
counts, provenance, license, limitations, and the project-selection decision.
See [`docs/phase2_baseline_results.md`](docs/phase2_baseline_results.md) for the
held-out results and gate decision.

## License

Project code is licensed under Apache-2.0. EPA data are not redistributed through
Git and retain the terms linked from the data audit.
