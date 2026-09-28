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
- Gate M1 selected the fusion model on 2/5 endpoints versus B3.
- Sanity Gate S: **STOP — suspected leakage/confounding**. The registered
  chemical-group permutation control retained a small significant bursts/min
  advantage over BT+. M2/M3 have not been run pending an integrity audit.

See [`docs/neurochip_data_audit.md`](docs/neurochip_data_audit.md) for exact data
counts, provenance, license, limitations, and the project-selection decision.
See [`docs/phase2_baseline_results.md`](docs/phase2_baseline_results.md) for the
held-out results and gate decision.

## Reproduction interface

```bash
make setup
make test
make reproduce-lite
make demo
```

`reproduce-lite` is result-only: it reads registered CSV artifacts, validates the
frozen prediction schema, and regenerates tables and figures. It never launches
training. Missing result files cause an explicit failure rather than an implicit
retraining step. The schema is documented in
[`schemas/prediction_schema_v1.yaml`](schemas/prediction_schema_v1.yaml).

## License

Project code is licensed under Apache-2.0. EPA data are not redistributed through
Git and retain the terms linked from the data audit.
