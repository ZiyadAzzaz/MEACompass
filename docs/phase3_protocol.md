# Phase 3 controlling protocol

Registered: 2026-09-28, with 26/75 M1 checkpoints complete and before aggregate
M1 results were available.  
Priority: this protocol controls where it differs from Phase 2.  
Original preregistration: `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`  
Gate S deviation: `0623e48`

## Ordered gates

1. Finish all 75 M1 checkpoints.
2. Evaluate M1 against B3 and BT+.
3. Run Gate S with the selected main model.
4. Continue to M2 and M3 only if Gate S permits it.
5. Apply Gate L1 immediately after M3.

## Gate M1

- Select M1 only if it beats B3 with a chemical-bootstrap confidence interval
  excluding zero on at least two of the five primary endpoints.
- If M1 ties B3 or is worse, select B3 and report that chemistry adds no
  significant value beyond early electrophysiology.
- Report M1 against BT+ as well, but do not use that comparison to conceal a
  failure to improve upon B3.

## Headline comparator

BT+ is the best of B0, B1, B1b, and B2 selected exclusively by inner validation
folds for every endpoint and outer fold. Outer-test outcomes never select BT+.
All headline gains use BT+. Original BT results remain in the appendix and in the
full five-endpoint results table.

## Gate S, M2, M3, and L1

- Gate S uses the registered permutation control, fair BT+ comparison, dose
  strata, cohort descriptions, and DIV5-only ablation.
- A beneficial permutation-control confidence interval triggers an immediate
  suspected-leakage stop.
- Gate S passes with at least 5% gain versus BT+, a beneficial confidence
  interval on at least two endpoints, and gain present at low and/or mid dose.
  High-dose-only gain is WEAK; disappearance across endpoints is STOP.
- M2 requires 85–95% overall coverage for nominal 90% intervals and at least 80%
  in each cohort. One CV+/CQR switch is allowed.
- M3 passes when 70%-coverage accepted-case MAE is at least 15% below full
  coverage with a beneficial chemical-bootstrap confidence interval; a reduction
  whose interval crosses zero is WEAK.
- Lock NeuroChip after Gate S PASS/WEAK and Gate M3 PASS/WEAK. Gate S PASS with
  M3 FAIL also locks with the reduced early-prediction headline. Any other state
  stops for user review.

## Claims and safety

- Always show all five endpoints. Treat active electrodes and coordinated
  activity `r` as limitations unless later evidence changes their status.
- Do not change the pre-registered `r` transform.
- Never claim that the EPA data are organ-on-chip data; they are rat cortical
  neural MEA assay data relevant to functional readouts used in neural in-vitro
  and organ-on-chip workflows.
- Never fabricate costs or results. Dataset and checkpoint safety rules remain
  in force.
