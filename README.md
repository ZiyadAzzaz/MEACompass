# NeuroChip-Twin

**Reliability-aware early prediction of neural network development from
microelectrode-array assays**

NeuroChip-Twin uses measurements available by day in vitro 7 (DIV7) to forecast
five DIV12 functional outcomes for unseen chemicals. It adds calibrated 90%
intervals and abstains on the least certain 30% of cases.

The source is a **rat cortical neural MEA assay, not an organ-on-chip dataset**.
This is a retrospective research decision-support prototype, not an autonomous
assay-termination system. Human neural organ-on-chip transfer requires prospective
external validation.

## Locked result

- M1 improves MAE versus inner-selected BT+ by 14.2–39.0% on all five endpoints;
  every chemical-bootstrap paired interval excludes zero.
- Against the stricter post-audit BT++, gains are 12.3–42.9% and remain significant
  on all five endpoints.
- Nested group CV+ attains 91.0–92.4% empirical coverage at nominal 90%.
- At 70% retained coverage, abstention clears the registered 15% risk-reduction
  criterion for firing rate, active electrodes, and coordinated activity. Bursts
  and network spikes are explicit limitations.
- The registered permutation gate originally stopped. A bounded integrity audit
  found no leakage, produced a clean full-shuffle result, and separated real M1
  from 20 independent chemical-block null runs. The failed gate remains recorded.
- Gate L1 is **LOCK**: the model, reliability protocol, and claims are frozen.

Read the integrated [report](docs/report_draft.md), [integrity audit](docs/integrity_audit.md),
[defense Q&A](docs/defense_qa.md), [video script](docs/video_script.md), and
[competition deck outline](docs/slides_outline.md).

## Reproduce without retraining

```bash
make setup
make test
make reproduce-lite
make demo
```

`reproduce-lite` validates the frozen prediction schema and regenerates tables and
figures from saved result artifacts only. It never launches training and fails
explicitly if required files are missing. The Streamlit demo likewise uses only
precomputed held-out predictions.

## Evidence map

- Data provenance and license: `docs/neurochip_data_audit.md`
- Preregistration and append-only decisions: `docs/preregistration.md`,
  `docs/decisions.md`
- Main and stricter comparator results: `results/gate_s_main.csv`,
  `results/bt_plus_plus.csv`
- Integrity controls: `results/audit/`
- Calibration and selective risk: `results/m2_calibration.csv`,
  `results/m3_risk_coverage.csv`
- Time and practical analysis: `results/time_ablation.csv`,
  `results/practical_value.csv`
- Interpretation and cases: `results/feature_importance.csv`,
  `results/case_studies.csv`

## License

Project code is Apache-2.0. EPA data are not redistributed through Git and retain
the terms linked from the data audit.
