# MEACompass: Reliability-Aware Early Prediction of Neural Network Development from Microelectrode-Array Assays

**Toward Functional Digital Twins for Neural Organ-on-Chip Screening**

## 0:00–0:20 — The decision problem

“A neural assay reaches its functional endpoint at day 12. MEACompass asks a
simple question: by day 7, can we forecast that outcome for a chemical the model
has never seen—and can we refuse when the forecast is unsafe?”

On screen: the full title and subtitle, “Toward Functional Digital Twins for
Neural Organ-on-Chip Screening.” Then: “Forecast early. Quantify uncertainty.
Continue when uncertain.”

## 0:20–1:00 — Show the working prototype first

Open the Streamlit app. Select a generic held-out chemical and endpoint.

“Everything shown here is precomputed outer-test evidence. **OBSERVED** contains
only DIV5 and DIV7 measurements. **PREDICTED** shows the DIV12 forecast and its
calibrated 90% interval. The reliability badge applies the frozen policy. A wide
interval means abstain and continue the assay. **HYPOTHESIS** labels anything not
validated by this study, including human organ-on-chip transfer.”

Change the endpoint once. Show that prediction, interval, baseline comparator, and
verdict update together. Do not select a case because it looks favorable.

## 1:00–1:40 — Fair evaluation

Show the main-results figure.

“We grouped by canonical chemical, not by well. Every dose, replicate, and alias
of a chemical stays on one side of the split. Across three repetitions of five
outer folds, M1 reduced mean absolute error versus the inner-selected BT+ baseline
by 14.2% for firing rate, 17.0% for bursts, 39.0% for active electrodes, 15.6% for
network spikes, and 22.7% for coordinated activity. Every paired chemical-level
confidence interval excluded zero. Against the stricter BT++, all five comparisons
also remained significant.”

## 1:40–2:20 — Lead with the integrity challenge

Show the audit decision graphic or table.

“One negative control did not behave as expected: a chemical-block permutation
showed a small burst improvement. Our registered rule stopped the pipeline. We
kept that failure visible. A bounded audit found no future-derived feature, a
clean full target shuffle, no alignment defect, and a dose-plus-trajectory effect
inside the original null construction. The real model then beat all 20 independent
block-null runs on every endpoint. Continuation was conditional on that audit and
on adding the stricter BT++ comparator.”

## 2:20–3:05 — Reliability, not automatic stopping

Show calibration and risk–coverage plots.

“Nominal 90% intervals attained 91.0% to 92.4% coverage. At 70% retained coverage,
accepted-case MAE fell from 39.29 to 31.87 for firing rate, 20.42 to 16.75 for
active electrodes, and 48.61 to 34.81 for coordinated activity. Bursts and network
spikes did not meet the registered 15% risk-reduction threshold, and we report
them as limitations. This is why the system is decision support: uncertainty
means continue, not terminate.”

## 3:05–3:40 — Why DIV7 matters

Show the time-ablation figure.

“DIV5 alone was weaker. Adding DIV7 produced the primary gains. DIV9 was tested
only after lock and improved four endpoints, while coordinated activity remained
flat. Under the frozen 70% acceptance policy, an accepted forecast is available
five days before DIV12—41.7% of the stated assay duration, or about 3.5 expected
decision-days across all predictions. We make no money-saving claim.”

## 3:40–4:15 — What the model uses

Show the contribution-family figure and one correct plus one failure case.

“Exact contribution values from the frozen tree models show DIV7 physiology as
the dominant family, with chemistry contributing complementary context. Chemistry
improved some endpoints, not all. We also show failures—such as Tributyltin
chloride and Mercuric chloride—because a trustworthy system must expose where it
breaks, not curate only attractive examples.”

## 4:15–4:45 — Scope and limitations

“This is rat cortical neural MEA data, not organ-on-chip data. Coordinated activity
has a normalization tail, two abstention endpoints miss threshold, and the potency
analysis is appendix-only because official EC50 values summarize a different
ontogeny-AUC target. Human neural organ-on-chip transfer requires a frozen,
prospective external study.”

## 4:45–5:00 — Close

“MEACompass’s contribution is not an automatic lab decision. It is an audited,
reproducible path from early neural measurements to a forecast, a calibrated
uncertainty estimate, and an honest option to wait. Forecast when evidence is
strong; continue the assay when it is not.”

On screen: `make test`, `make reproduce-lite`, and the repository evidence paths.
