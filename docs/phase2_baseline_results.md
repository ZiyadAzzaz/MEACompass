# Phase 2 registered baseline results

Run date: 2026-09-28  
Frozen protocol: commit `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`

These are chemical-disjoint outer-test results aggregated over five folds and
three seeds. `Delta MAE` is model MAE minus the inner-selected best trivial
baseline (BT); negative values are beneficial. Confidence intervals use the
pre-registered 1,000-draw chemical-level bootstrap.

| Model | Endpoint | N | Chemicals | MAE y12 | Spearman y12 | Spearman delta | Delta MAE vs BT [95% CI] | Relative gain |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| B0 | Bursts/min | 4,064 | 136 | 32.739 | 0.236 | 0.671 | -13.026 [-17.506, -8.643] | 28.46% |
| B0 | Mean firing rate | 4,112 | 136 | 44.995 | 0.240 | 0.529 | -3.114 [-9.431, 3.142] | 6.47% |
| B0 | Active electrodes | 4,112 | 136 | 38.078 | 0.232 | 0.583 | 6.210 [-4.031, 17.695] | -19.49% |
| B0 | Network spikes | 3,488 | 125 | 48.259 | 0.196 | 0.462 | -9.410 [-13.672, -2.762] | 16.25% |
| B0 | Coordinated activity (`r`) | 4,112 | 136 | 86.105 | 0.236 | 0.562 | 23.194 [3.605, 47.494] | -36.87% |
| B3 | Bursts/min | 4,064 | 136 | 26.704 | 0.483 | 0.761 | -19.061 [-22.648, -16.155] | 41.65% |
| B3 | Mean firing rate | 4,112 | 136 | 40.519 | 0.485 | 0.583 | -7.591 [-12.977, -2.790] | 15.78% |
| B3 | Active electrodes | 4,112 | 136 | 28.930 | 0.418 | 0.699 | -2.938 [-13.226, 7.933] | 9.22% |
| B3 | Network spikes | 3,488 | 125 | 39.728 | 0.460 | 0.610 | -17.941 [-20.830, -12.868] | 31.05% |
| B3 | Coordinated activity (`r`) | 4,112 | 136 | 77.489 | 0.160 | 0.635 | 14.579 [-5.901, 39.492] | -23.17% |
| B4 | Bursts/min | 4,064 | 136 | 31.330 | 0.308 | 0.697 | -14.435 [-19.098, -10.333] | 31.54% |
| B4 | Mean firing rate | 4,112 | 136 | 45.628 | 0.303 | 0.551 | -2.482 [-9.211, 3.812] | 5.16% |
| B4 | Active electrodes | 4,112 | 136 | 36.730 | 0.271 | 0.642 | 4.861 [-8.068, 20.346] | -15.25% |
| B4 | Network spikes | 3,488 | 125 | 47.376 | 0.280 | 0.489 | -10.293 [-14.464, -4.088] | 17.79% |
| B4 | Coordinated activity (`r`) | 4,112 | 136 | 77.638 | 0.170 | 0.634 | 14.728 [-13.620, 49.213] | -23.41% |

## Gate decision

Gate B2 is **STRONG** on exactly three of five endpoints: bursts/min, mean firing
rate, and network spikes. Each has at least 5% relative MAE gain, a beneficial
confidence interval excluding zero, and delta Spearman at least 0.20.

Active electrodes has a positive point estimate but does not clear the confidence
interval requirement. Coordinated activity fails in MAE despite positive rank
correlation and is not presented as a success.

## Reproducibility note

The prediction checkpoints and summary are complete. A shared tuning-log file was
overwritten during parallel B4 execution, so the original aggregate tuning log is
incomplete. The runner now writes task-local tuning checkpoints to prevent this
race. Reconstructing the missing historic tuning rows requires deterministic
re-tuning; no held-out prediction or reported metric is missing or changed.
