# NeuroChip-Twin defense Q&A

## What is the single defensible claim?

Using information available by DIV7, M1 forecasts five DIV12 rat cortical MEA
endpoints for held-out chemicals more accurately than BT+ and the stricter BT++
comparator. Nominal 90% intervals attain 91.0–92.4% coverage, and abstention lowers
error by at least 15% on three endpoints at 70% retained coverage. This is a
retrospective decision-support result, not proof of human organ-on-chip transfer.

## Is this an organ-on-chip dataset?

No. It is a rat cortical neural microelectrode-array assay. The relevance is the
shared class of longitudinal electrophysiology readouts and the transferable
evaluation design. Device-specific and human neural organ-on-chip claims require
prospective external data.

## Why is predicting DIV12 from DIV7 not just autocorrelation?

Early physiology is expected to be predictive, so persistence and temporal
baselines are the correct comparators. M1 beat BT+ by 14.2–39.0% and BT++ by
12.3–42.9% across the five endpoints, with chemical-bootstrap confidence intervals
excluding zero. The time ablation also shows DIV5 alone is weaker. We claim useful
incremental prediction, not discovery of an autocorrelation-free signal.

## Why was BT+ added after preregistration?

B0, the prespecified dose-bin mean, was stronger than parts of the original BT set.
Continuing to headline a weaker comparator would overstate value. BT+ includes
B0/B1/B1b/B2 and selects the winner using inner validation only. The deviation is
logged, and all original BT comparisons remain published.

## Why was BT++ added later?

The bounded integrity audit showed that the initial permutation retained generic
dose and trajectory structure. BT++ therefore selects between BT+ and a fixed
dose-smooth comparator inside each outer training fold. This raises the bar after
the audit without using outer-test outcomes to select it. Results versus BT+ and
BT++ are both shown.

## Did the permutation test fail?

Yes. The registered permutation control showed a small significant improvement
for bursts, so Gate S correctly stopped. We did not erase or relabel that result.
A bounded post-registration audit then found no feature leakage, a clean full
shuffle, no alignment defect, and real-model performance beyond 20 independent
chemical-block null runs on all five endpoints. Continuation was conditional on
that audit and the stricter BT++ comparison.

## Could the audit be post-hoc rationalization?

That risk is why its scope, stop record, null ensemble, and outputs are explicit.
The audit did not change endpoints, folds, target definitions, or held-out
predictions. It tested concrete failure mechanisms and imposed a stricter baseline.
It supports a qualified continuation; it does not turn the original control into
a preregistered success.

## Why preregister the protocol?

Preregistration separates choices made before outcomes from choices that outcomes
could influence. It constrains endpoint switching, test-fold tuning, and selective
reporting. Append-only deviation records make later safeguards inspectable.

## Why chemical-disjoint evaluation rather than random wells?

The intended unit of generalization is an unseen chemical. Wells, doses, and
replicates from one chemical share identity and correlated trajectories. Random
well splitting would place related measurements on both sides and produce an
optimistically biased answer to the wrong question.

## Were outer-test labels used to choose a baseline or tune M1?

No. Baseline choice and model tuning occur only within grouped inner folds of each
outer training set. The outer fold is evaluation only. Dose-stratum boundaries and
calibration residuals are likewise learned without outer-test labels.

## Why use gradient-boosted trees rather than deep learning?

There are about 4,200 complete trajectories and only 136 chemical groups. Boosted
trees suit heterogeneous tabular measurements, missingness, descriptors, and
fingerprints; train reliably on CPU; and constrain capacity relative to a deep
network. Credible held-out evidence matters more than architectural novelty here.

## Does chemistry add value?

It adds complementary predictive context, but the answer is endpoint-specific.
M1 significantly beat B3 for active electrodes and coordinated activity; the
confidence intervals crossed zero for bursts, firing rate, and network spikes.
Contribution analysis assigns 11.2–31.8% of mean absolute contribution to combined
structure features, but those are predictive associations, not causal mechanisms.

## Why is uncertainty required?

A point estimate cannot say whether a forecast is reliable enough for early
triage. Nested group CV+ intervals achieved 91.0–92.4% coverage at nominal 90%.
The policy then abstains on the widest 30% of intervals. At 70% coverage, error
fell at least 15% for firing rate, active electrodes, and `r`; it did not do so for
bursts or network spikes, which are reported as limitations.

## Are the intervals valid for new laboratories or human chips?

No such claim is made. They are cross-validated for the audited EPA assay and its
chemical distribution. A new laboratory, platform, species, or protocol can shift
both errors and coverage, so intervals must be prospectively checked and possibly
recalibrated without test leakage.

## Why chemical-level rather than well-level bootstrap?

Chemical is the independent generalization unit. Resampling wells would treat
correlated concentrations and replicates as independent and narrow confidence
intervals artificially. Each bootstrap draw keeps all observations of a sampled
chemical together.

## Why do you still qualify active electrodes and coordinated activity?

Active electrodes had strong prediction and abstention results, but it remains a
species- and assay-specific endpoint. Coordinated activity passed numerically but
its percent-control transform can explode when the plate-control denominator is
near zero. Neither issue should be hidden by aggregate gains.

## Why not claim the EC50 analysis as early potency prediction?

The official EPA EC50 target is an ontogeny area-under-the-curve summary, while the
model predicts DIV12. Their correlations are encouraging but compare different
quantities. Gate P1 is therefore marked `APPENDIX_TARGET_MISMATCH`, and no
five-days-earlier potency claim is made.

## How much time does the prototype save?

Under the declared 70% acceptance policy, accepted cases receive a forecast five
days before DIV12—41.7% of the stated assay duration. Across all predictions this
is about 3.5 expected decision-days. This is a workflow-time estimate, not a cost
or productivity claim.

## Would you let this stop an assay tomorrow?

No. This is a research decision-support system, not an autonomous assay-termination
system. Prospective validation is required before real laboratory deployment. A
qualified scientist must retain authority, uncertain cases must continue, and any
operational version needs drift monitoring, governance, and an override process.

## What would prospective human neural organ-on-chip validation require?

Freeze endpoints and acceptance rules in advance; collect representative devices,
labs, batches, and chemical classes; keep chemicals and sites disjoint; measure
coverage as well as error; recalibrate using validation data only; test failure and
abstention behavior; and retain a truly untouched external test set.

## What are the main weaknesses?

The study is retrospective, small in independent chemical groups, and based on rat
cortical culture. Gate S initially stopped. BT+ and BT++ are documented deviations.
Abstention misses its threshold on two endpoints, `r` has a normalization tail,
cohort analyses are not external transfer tests, and a historical B3 tuning-log
gap remains. These constraints define the next experiments rather than disappear
from the presentation.
