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
- Registered Sanity Gate S: **FAIL / STOP—unchanged**. The registered
  chemical-block control retained a small bursts/min advantage over BT+.
- Authorized post-registration integrity audit: **PASS—residual structure under
  null**. No leak or realignment was found; the full well shuffle was clean and
  real M1 exceeded all 20 repeated block-null runs on all five endpoints.
- Gate M2: **PASS**. Nominal-90% nested group-CV+ coverage is 91.03–92.40%
  overall, with every NTP/ToxCast cohort above 90%.
- Gate M3: **PASS, mixed by endpoint**. At 70% accepted coverage, firing rate,
  active electrodes, and `r` meet the ≥15% risk-reduction criterion with
  chemical-bootstrap intervals below zero.
- Gate L1: **LOCK**. M1 and the reliability protocol are frozen. The `r`
  normalization caveat and the registered Gate S failure remain visible.

See [`docs/neurochip_data_audit.md`](docs/neurochip_data_audit.md) for exact data
counts, provenance, license, limitations, and the project-selection decision.
See [`docs/phase2_baseline_results.md`](docs/phase2_baseline_results.md) for the
held-out results and gate decision.
See [`docs/integrity_audit.md`](docs/integrity_audit.md) and
[`docs/phase3_m2_m3_results.md`](docs/phase3_m2_m3_results.md) for the audit and
reliability gates.

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
