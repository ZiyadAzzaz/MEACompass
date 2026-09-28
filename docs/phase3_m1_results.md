# Phase 3 Gate M1 results

Evaluation date: 2026-09-28  
Original preregistration: `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`  
Phase 3 rule registered before M1 completion: `932f024`  
M1 implementation: `2085c30`

All values use five chemical-disjoint outer folds and seeds 0/1/2. MAE and
correlations are mean seed metrics. Paired confidence intervals resample canonical
chemical groups 1,000 times after averaging each sample's three seed predictions.
Negative delta MAE is beneficial. BT+ was selected from B0/B1/B1b/B2 using inner
validation only.

| Endpoint | BT+ MAE | B3 MAE | M1 MAE | M1 Spearman y12 | M1 Spearman delta | M1 delta MAE vs original BT [95% CI] | M1 delta MAE vs BT+ [95% CI] | M1 gain vs BT+ | M1 delta MAE vs B3 [95% CI] |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bursts/min | 32.739 | 26.704 | 27.171 | 0.485 | 0.757 | -18.594 [-22.840, -16.457] | -6.371 [-8.295, -4.615] | 19.47% | -0.233 [-0.902, 0.428] |
| Mean firing rate | 45.792 | 40.519 | 39.295 | 0.533 | 0.594 | -8.815 [-14.611, -7.566] | -7.541 [-13.444, -2.055] | 16.94% | -3.140 [-8.385, 1.439] |
| Active electrodes | 33.504 | 28.930 | 20.423 | 0.530 | 0.718 | -11.446 [-15.203, -9.508] | -12.537 [-16.084, -9.434] | 38.96% | -8.856 [-19.408, -0.243] |
| Network spikes | 48.259 | 39.728 | 40.724 | 0.461 | 0.581 | -16.946 [-20.725, -12.003] | -8.177 [-10.865, -5.266] | 16.95% | 0.445 [-0.513, 1.624] |
| Coordinated activity (`r`) | 62.910 | 77.489 | 48.615 | 0.498 | 0.585 | -14.295 [-18.704, -12.184] | -15.415 [-18.704, -12.184] | 24.50% | -29.351 [-53.532, -10.529] |

The point estimates in paired-comparison columns use the averaged three-seed
prediction per sample, while the displayed model MAEs are the registered mean of
the three seed-level metrics. This explains small arithmetic differences between
the displayed MAEs and paired deltas.

## Gate decision

**SELECT M1.** M1 beats B3 with a beneficial chemical-bootstrap confidence
interval excluding zero on exactly two endpoints: active electrodes and
coordinated activity `r`. This satisfies the Phase 3 rule registered before M1
completion.

M1 significantly beats BT+ on all five endpoints. Bursting and firing do not show
a decisive M1-over-B3 difference; network spikes is statistically tied and has a
slightly worse point estimate. Therefore the chemistry/fusion contribution is not
claimed uniformly. Active electrodes improves materially at this gate. The
pre-registered instability concern for percent-control `r` remains a limitation
despite its favorable M1 result and will not be hidden or redefined.
