# Defense Q&A: protocol and deployment

This document deliberately excludes final numerical results until the registered
gates finish.

## Why is this relevant to organ-on-chip if the training data are not OoC?

The data are a rat cortical neural MEA assay, not organ-on-chip data. The relevance
is methodological: neural organ-on-chip systems can use the same class of
longitudinal electrophysiology readouts, and uncertainty-aware early forecasting
could support their workflows. This study establishes neither device-specific nor
human-chip transfer. Those require prospective external validation.

## What are the limitations of rat cortical MEA data?

Species biology, primary-cell composition, culture conditions, maturation,
exposure kinetics, electrode geometry, and assay protocol can differ from human
iPSC-derived or microfluidic neural systems. A model can be valid for this EPA
assay yet fail under those distribution shifts.

## What is required before transferring conclusions to human neural OoC systems?

An external, prospectively specified study on representative human neural OoC
devices is required. It should freeze endpoints and acceptance criteria, measure
device and laboratory batch effects, recalibrate intervals without test leakage,
and verify performance and safety under the intended operating conditions.

## Why was BT+ added after preregistration?

The original BT compared temporal heuristics B1/B1b/B2. Completed baseline results
showed that the prespecified B0 dose-bin mean could be stronger on some endpoints.
Continuing to headline the weaker set would overstate value. BT+ therefore adds B0
and selects among all four candidates using inner validation only. It is logged as
a deviation; original BT results remain visible.

## Why preregister the protocol?

Preregistration separates scientific choices made before outcomes from choices
that could be influenced by them. It limits endpoint switching, test-fold tuning,
and selective reporting, while the deviation log makes necessary corrections
auditable.

## Why chemical-disjoint evaluation?

The intended question concerns unseen chemicals. Grouping by canonical CAS RN
prevents concentrations, aliases, wells, and replicates of one chemical from
appearing on both sides of a split.

## Why not random well splitting?

Wells from the same chemical share exposure identity and correlated trajectories.
A random well split would let the model recognize a chemical through related
training wells and would exaggerate generalization.

## Why use simple tree models instead of deep learning?

The dataset contains roughly four thousand trajectories and 136 chemical groups.
Gradient-boosted trees handle heterogeneous tabular features and missing values,
are CPU-feasible, and impose less capacity than a deep network. The goal is
credible held-out performance, not architectural novelty without data support.

## Why is uncertainty required?

A point prediction cannot communicate whether an unfamiliar chemical resembles
the training domain or whether its forecast is precise enough for early triage.
Calibrated intervals support an explicit abstention path: uncertain cases continue
to DIV12.

## Why is early stopping not an autonomous laboratory decision?

The output is research decision support, not an autonomous assay-termination
system. It has not been prospectively validated for operational deployment. A
qualified scientist remains responsible, and real use would require external
validation, governance, monitoring, and a documented override process.

## Why use a chemical-level rather than well-level bootstrap?

The independent generalization unit is the chemical, not the well. Resampling
wells would treat correlated concentrations and replicates as independent and
produce overconfident intervals. Chemical bootstrap draws retain every associated
well and concentration together.

## How would a laboratory use this research prototype?

The prototype would display a forecast, interval, and continue/early-decision
recommendation beside observed early measurements. It would not terminate an
assay. A laboratory would first run a prospective validation, define acceptable
error and coverage, train staff, and retain human review for every decision.
