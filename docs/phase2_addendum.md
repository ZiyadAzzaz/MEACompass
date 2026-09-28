# Phase 2 addendum: Sanity Gate S

Registered: 2026-09-28  
Status: controlling protocol where it differs from the frozen preregistration  
Original preregistration commit: `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`

This is a registered deviation, not a replacement for the original protocol.
All five endpoints and all original BT comparisons remain mandatory.

## Execution order

1. Finish M1 and evaluate Gate M1 exactly as pre-registered.
2. Run Sanity Gate S before M2.
3. Continue to M2 and M3 only if Gate S permits it.

## S-a: stronger baseline

- Add B0 to the reported results table.
- Define BT+ as the best of B0, B1, B1b, and B2 for each endpoint and outer fold.
- Select BT+ using inner validation folds only; outer folds are evaluation only.
- Report delta MAE against both original BT and BT+.

## S-b: permutation negative control

- Within each outer training fold, permute DIV12 targets at the canonical-CAS
  group level using fixed seed `20260928` and split seed 0.
- Keep every well, concentration, and replicate belonging to a shuffled chemical
  together.
- Implement this as a bijection of donor chemical target blocks. Within each
  block, order rows by dose, plate, and well. When donor and recipient block sizes
  differ, align the complete donor block to recipient rows by deterministic
  empirical-percentile interpolation. One donor chemical supplies every target
  assigned to one recipient chemical; targets are never shuffled well by well.
- Retrain B3. Expected result: no meaningful positive skill over BT+.
- If any endpoint has beneficial delta MAE versus BT+ with a chemical-bootstrap
  confidence interval excluding zero, stop immediately and report suspected
  leakage. Do not continue to M2.

## S-c: dose-stratified evaluation

- Evaluate B3 and M1 against BT+ on zero, low, mid, and high dose strata.
- Derive low/mid/high cut points from positive doses in each outer training fold
  only and apply them unchanged to its outer test fold. The cut points are the
  1/3 and 2/3 quantiles of positive-dose eligible training rows, computed
  separately for each endpoint and outer fold. Zero dose is always its own
  stratum.
- Report all five endpoints.

## S-d: per-cohort evaluation

- Report NTP and ToxCast separately for all five endpoints.
- Treat this as descriptive robustness analysis, not cross-cohort generalization.

## S-e: quick time ablation

- Train B3 with DIV5-only early inputs plus the registered dose and cohort inputs.
- Compare it with standard DIV5+DIV7 B3.
- Do not use DIV9.

## Gate S decision

- **STOP — suspected leakage:** the permutation control has beneficial delta MAE
  versus BT+ with a confidence interval excluding zero.
- **PASS:** gain versus BT+ is at least 5% with a beneficial confidence interval
  excluding zero on at least two endpoints, and gain is present in low and/or mid
  dose strata.
- **WEAK:** gain versus BT+ is concentrated only at high dose. Continue, but
  shift the headline toward reliability and abstention.
- **STOP:** gain versus BT+ disappears across endpoints. Report before M2.

## Early lock and reporting

Declare Gate L1 LOCK immediately only after M1 is complete and evaluated, Gate S
passes, and Gate M3 is PASS or WEAK. After lock, freeze CellTwin-X and begin the
Streamlit demo. Report Gate S and Gate M3 using the Phase 2 Section 9 format.

## Safety and deferred work

- Do not delete, move, rename, or overwrite any external file, dataset, or
  checkpoint without explicit approval.
- Reconstruct the historical B3/B4 tuning log only after M3 and only if estimated
  runtime is below two CPU-hours. Never rerun held-out predictions unless a
  validity problem is found.
- Always report all five endpoints. Treat active electrodes and coordinated
  activity (`r`) as limitations unless later gates materially change them.
