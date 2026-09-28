# NeuroChip-Twin report draft

This draft intentionally contains no conclusion about model superiority. Results,
claims, and showcase examples remain blocked until the registered gates finish.

## 1. Problem

Developmental neurotoxicity and neural in-vitro studies use longitudinal
electrophysiology to measure the emergence of firing, bursting, active electrodes,
network spikes, and coordinated activity. Waiting for a late assay readout delays
triage. An early forecast is useful only when it generalizes to unseen chemicals,
beats a strong dose-informed expectation, and communicates when it is unsafe.

NeuroChip-Twin studies a research decision-support workflow: use information
available by DIV5 and DIV7 to forecast DIV12, construct a calibrated uncertainty
interval, and abstain when the interval is too wide. It is not an autonomous
assay-termination system. Prospective validation is required before operational
laboratory use.

## 2. Data

The source is the U.S. EPA Network Formation Assay associated with Shafer et al.
(2019). It is a **rat cortical neural microelectrode-array assay, not an
organ-on-chip dataset**. Its relevance to neural organ-on-chip research is that
MEA functional readouts are also used in neural in-vitro and chip workflows; the
present study does not establish transfer to a human neural chip.

### Dataset audit

| Measure | Audited value |
|---|---:|
| Official test entries | 146 |
| Canonical chemicals | 136 |
| Longitudinal records | 17,224 |
| Plates/batches | 99 |
| Plate-well trajectories | 4,344 |
| Complete DIV5/7/9/12 trajectories | 4,192 (96.50%) |
| NTP records | 5,712 |
| ToxCast records | 11,512 |
| Electrophysiology columns available | 18 |
| SMILES resolved | 130/136 (95.59%) |

The stable experimental key is `(cohort, Plate.SN, well)`. Raw treatment aliases
and biological replicates are canonicalized to CAS RN before splitting. Missing
burst-conditional measurements are retained with explicit missingness indicators.
The complete audit, checksums, exclusions, and limitations are in
`docs/neurochip_data_audit.md`.

### Licensing

The official EPA catalog provides public access and links the EPA ScienceHub
license. Unless otherwise specified, works produced by U.S. EPA employees are
public domain under 17 U.S.C. §105. The source carries no warranty, and EPA names,
seals, or logos must not imply endorsement. Repository code is Apache-2.0.
Chemical structures were resolved through the public PubChem PUG REST interface;
raw EPA data and cached datasets are not redistributed through Git.

## 3. Protocol

### Preregistration and deviations

The primary endpoints, target, time-causal feature contract, grouped folds,
metrics, chemical bootstrap, baseline grid, uncertainty rules, and gates were
frozen at commit `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0` before predictive
results. Subsequent changes are append-only decisions rather than silent edits.

BT+ was registered after B0 unexpectedly demonstrated that the original BT set
was not always the strongest comparator. BT+ is selected from B0, B1, B1b, and B2
using inner validation MAE only. Outer-test outcomes never choose it. The original
BT comparison remains reported as the preregistered analysis. Sanity Gate S and
the controlling Phase 3 rules are documented in `docs/phase2_addendum.md`,
`docs/phase3_protocol.md`, and `docs/decisions.md`.

### Chemical-disjoint nested cross-validation

The outer evaluation uses five stratified group folds repeated for seeds 0, 1,
and 2. Canonical CAS RN is the group: every alias, concentration, plate, well,
and biological replicate for a chemical stays on one side of a split. The inner
three-fold grouped split selects baselines, model variants, and hyperparameters.
This design estimates generalization to unseen chemicals. A random well split
would leak closely related measurements from the same chemical into training and
test data and is therefore invalid for the stated question.

### Time causality

Primary inputs may contain raw DIV5 and DIV7 measurements, their missingness
flags, dose, cohort, and structure-only chemical descriptors. DIV9 is reserved
for an explicit time ablation. DIV12 measurements, DIV12 controls as features,
EC50 values, hit labels, and late viability measurements are forbidden inputs.
DIV12 plate-control values define target units only and never select a prediction.
Automated tests fail closed on future-derived feature names.

### Targets and endpoints

For each endpoint, the target is DIV12 as percent of the same-plate, same-DIV
zero-dose control median. The five frozen endpoints are mean firing rate,
bursts/min, active electrodes, network spikes, and coordinated activity `r`.
The unstable behavior of percent control for `r` near a zero denominator remains
an explicit limitation; the transform is not changed to improve results.

### Metrics and uncertainty

The protocol reports MAE, RMSE, Spearman correlation on DIV12, MAE and Spearman
on change from DIV7, paired MAE difference, and relative MAE gain. Confidence
intervals use 1,000 bootstrap draws of canonical chemical groups. Wells are never
bootstrapped independently because wells from one chemical are correlated and do
not constitute independent generalization units.

## 4. Reproduction

The intended result-only path is:

```bash
make setup
make test
make reproduce-lite
make demo
```

`reproduce-lite` reads only saved prediction and result files. It never imports a
training entry point or retrains automatically. It fails with an explicit list if
any registered result artifact is absent. The demo likewise loads standardized,
precomputed predictions and works offline after dependencies and artifacts are
present.

The frozen prediction contract is `schemas/prediction_schema_v1.yaml`. Required
fields include endpoint, model, chemical identifier, cohort, dose, truth,
prediction, uncertainty bounds/width, fold, and seed. Missing uncertainty or dose
values may be null in legacy pre-calibration artifacts but the columns themselves
must be present.

## 5. Sources and licenses

- EPA dataset catalog and DOI: https://doi.org/10.23719/1503191
- Data.gov catalog record: https://catalog.data.gov/dataset/data-for-evaluation-of-chemical-effects-on-network-formation-in-cortical-neurons-grown-on-
- Shafer et al. (2019): https://doi.org/10.1093/toxsci/kfz052
- EPA ScienceHub license: https://pasteur.epa.gov/license/sciencehub-license.html
- PubChem PUG REST: https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest
- Project code license: `LICENSE` (Apache-2.0)
