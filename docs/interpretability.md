# Frozen-model interpretability and case studies

Date: 2026-09-28

This analysis refits only the five seed-0 outer models per endpoint with their
preserved M1 settings. XGBoost's exact tree contribution output is calculated on
the corresponding held-out chemicals. It does not retune or change predictions.
For residual variants, contributions describe the learned correction around the
separately reported B2 anchor; they are not incorrectly presented as the whole
prediction.

## Global pattern

Early electrophysiology dominates. DIV7 neural features account for 56.9-77.3%
of total mean absolute contribution across endpoints, and DIV5 neural features
add 3.7-17.6%. Chemistry is complementary rather than dominant: Morgan and RDKit
features together account for 11.2-31.8%. Cohort contributes at most 1.0%, and
explicit dose at most 7.1%.

| Endpoint | DIV5 | DIV7 | Morgan | RDKit | Dose | Cohort |
|---|---:|---:|---:|---:|---:|---:|
| Mean firing rate | 17.0% | 71.3% | 8.6% | 2.9% | 0.2% | 0.0% |
| Bursts/min | 3.7% | 56.9% | 17.3% | 14.4% | 7.1% | 0.6% |
| Active electrodes | 9.4% | 77.3% | 10.2% | 2.6% | 0.5% | 0.0% |
| Network spikes | 8.3% | 61.9% | 18.1% | 8.6% | 2.2% | 1.0% |
| Coordinated activity (`r`) | 17.6% | 64.1% | 14.4% | 3.7% | 0.1% | 0.0% |

The highest individual features are biologically coherent temporal measurements:
DIV7 mean firing rate for firing, DIV7 active electrodes for active electrodes,
and DIV7 coordinated activity for bursts, network spikes, and `r`. Chemistry bits
enter the top five for active electrodes, network spikes, and `r`, consistent with
the measured M1-versus-B3 improvement on active electrodes and `r` rather than a
claim that chemistry alone predicts the assay.

## Descriptive cases

Cases were selected only after Gate L1 for explanation, never for performance
estimation or default demo choice. Among non-zero-dose held-out wells having all
three Gate-M3 passing endpoints, three distinct chemicals with the lowest mean
endpoint-scaled absolute error and two with the highest were selected.

| Type | Chemical | CAS | Dose | Mean scaled error | All three accepted? |
|---|---|---|---:|---:|---|
| Correct | Fluorene | 86-73-7 | 0.30 | 0.030 | No |
| Correct | Glycerol | 56-81-5 | 1.00 | 0.033 | No |
| Correct | Picoxystrobin | 117428-22-5 | 0.03 | 0.047 | Yes |
| Failure | Tributyltin chloride | 1461-22-9 | 0.03 | 56.905 | No |
| Failure | Mercuric chloride | 7487-94-7 | 0.30 | 49.810 | Yes |

The correct cases are mostly driven by DIV7 state with smaller DIV5 and chemistry
corrections. Tributyltin's firing failure contains an unusually large DIV5
contribution, indicating a trajectory conflict between early days. Mercuric
chloride demonstrates an important limitation: a narrow interval can still
coincide with a large error under an extreme or shifted biological response.
Reliability is therefore probabilistic, not a safety guarantee.

The `r` explanations remain subject to its extreme-tail percent-control pathology.
Fingerprint-bit contributions are reproducible model features, not inherently
human-readable substructures; structural interpretation would require a separate
bit-to-atom mapping analysis.

Machine-readable outputs are `results/feature_importance.csv`,
`results/case_studies.csv`, and `results/case_contributions.csv`.
