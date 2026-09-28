# NeuroChip-Twin competition deck outline

## Slide 1 — A five-day earlier decision, with permission to wait

Visual: DIV5 → DIV7 → forecast/abstain → DIV12 timeline.

Message: Forecast unseen-chemical DIV12 neural activity from DIV7; quantify
uncertainty; continue the assay when uncertain.

## Slide 2 — The scientific boundary is explicit

Visual: two-column “what this is / what this is not.”

- Is: retrospective rat cortical MEA decision-support research.
- Is not: organ-on-chip training data, human validation, or autonomous stopping.

## Slide 3 — Evaluation designed around the real generalization unit

Visual: chemical-group split diagram showing doses/wells/replicates locked together.

Message: 136 chemicals, ~4,200 complete trajectories, 3 × 5 outer folds, inner-only
selection, chemical-level bootstrap. Random well splitting is prohibited.

## Slide 4 — M1 beats the fair comparator on all five endpoints

Visual: paired MAE/gain chart from `results/gate_s_main.csv` and
`results/bt_plus_plus.csv`.

Headline: 14.2–39.0% gain versus BT+; 12.3–42.9% versus stricter BT++; all paired
chemical-bootstrap intervals exclude zero. Show every endpoint.

## Slide 5 — The negative control stopped us

Visual: STOP → bounded audit → conditional continuation flow.

Message: registered Gate S failed for bursts. The record stays visible. Full
shuffle was clean, no leakage/alignment fault was found, and real M1 exceeded all
20 block-null runs on every endpoint. BT++ was added as an extra safeguard.

## Slide 6 — Calibrated uncertainty turns prediction into a workflow

Visual: calibration plot plus interval badge from the demo.

Headline: nominal 90% intervals achieve 91.0–92.4% coverage; minimum cohort
coverage is 90.36%.

## Slide 7 — Abstention helps three endpoints, not five

Visual: 70%-coverage risk-reduction bars with a 15% threshold line.

- Pass: firing 18.9%, active electrodes 18.0%, coordinated activity 28.4%.
- Limitation: bursts 4.6%, network spikes 5.3% with CI crossing zero.

## Slide 8 — DIV7 is the useful decision point

Visual: MAE by DIV5, DIV5+7, DIV5+7+9.

Message: DIV5 alone is weaker; DIV7 creates the primary signal; DIV9 is a post-lock
ablation. Accepted forecasts are available five days before DIV12, about 3.5
expected decision-days overall. No cost claim.

## Slide 9 — Physiology leads; chemistry adds context

Visual: stacked contribution-family bars and one disclosed failure case.

Message: DIV7 accounts for 56.9–77.3% of absolute contribution. Chemistry accounts
for 11.2–31.8%. M1 significantly beats B3 on two endpoints, not all five; SHAP-like
contributions are predictive, not causal.

## Slide 10 — Live prototype: observed, predicted, hypothesis

Visual: Streamlit screenshot or live app.

Demo sequence: choose a generic held-out case → show early observations → display
forecast/interval → show accept or continue verdict. Never cherry-pick a
best-looking example.

## Slide 11 — What would make this deployable?

Visual: prospective-validation checklist.

Message: frozen human neural OoC protocol, external devices/labs/batches, untouched
chemical test set, interval recalibration, drift monitoring, governance, human
override. This prototype does not terminate assays.

## Slide 12 — Audited evidence, reproducible in minutes

Visual: four commands and evidence tree.

```text
make setup
make test
make reproduce-lite
make demo
```

Close: “Forecast when evidence is strong; continue when it is not.”
