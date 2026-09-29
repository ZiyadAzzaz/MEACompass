# Reproducibility record

## Final public-clone compliance run — 2026-09-29

A new shallow clone from `https://github.com/ZiyadAzzaz/MEACompass` completed:

```bash
make setup
make fetch-results
make test
make reproduce-lite
make demo
```

The result manifest verified eight committed artifacts (8.37 MiB) without a
download. Tests reported **77 passed and 5 skipped**. The skips are expected when
the optional official EPA raw data are absent: one time-causality test and four
split/data tests. `reproduce-lite` regenerated figures without retraining. The
Streamlit server and health endpoint returned HTTP 200 before manual shutdown.

This result-only path requires no paid API, proprietary hardware, private data,
or original workstation. Package installation requires ordinary access to public
Python package channels on a fresh machine.

## Two supported paths

### Result-only path

This is the submission and reviewer path. It requires no raw EPA data and never
re-trains a model.

```bash
make setup
make fetch-results
make test
make reproduce-lite
make demo
```

`make fetch-results` verifies seven committed artifacts against
`results/results_manifest.json`. Their combined size is 8.34 MiB; the largest is
`results/demo_predictions.csv` at 5.54 MiB. Every file is below the 50 MiB
repository threshold. `reproduce-lite` fails explicitly if any required artifact
is absent and does not import a training module.

### Full rebuild path

```bash
make data
make train-all CONFIRM_LOCKED_REBUILD=1
```

`make data` downloads the four public files in the EPA catalog for DOI
10.23719/1503191. URLs, byte sizes, and SHA-256 hashes are frozen in
`schemas/epa_downloads_v1.json`. Existing files with a bad checksum are never
overwritten automatically. Archive extraction rejects path traversal and refuses
to merge into a non-empty incomplete dataset directory.

`make train-all` enumerates the complete locked sequence: treatment mapping,
free PubChem structure resolution, B0–B4, BT+, M1, Gate S controls and audit,
BT++, CV+ calibration, selective risk, time ablations, potency appendix,
interpretability, and publication artifacts. The command is explicitly guarded
because it writes ignored checkpoints and regenerates result files. It is not
called by setup, tests, reproduction, or the demo.

## Recorded compute scope

The locked run used Windows, an Intel64 Family 6 Model 140 CPU with 4 physical / 8
logical cores, 15.8 GiB RAM, and an NVIDIA RTX 3050 Laptop GPU with 4 GiB VRAM.
The XGBoost pipeline was CPU-bound (`n_jobs: 4`); the GPU was not required.

Available per-task logs record 25,251.2 seconds (7.01 aggregate task-hours) for
the 75 M1 outer-fold tuning/prediction jobs and 1,281.0 seconds (0.36 aggregate
task-hours) for the retained baseline tuning records. These are sums of logged
task runtimes, not a measured end-to-end wall clock, because multiple workers ran
in parallel. No unlogged wall time is invented.

## Fresh-clone verification

Final verification was executed on 2026-09-29 from commit `093d08e` in a new
local clone at `repro_checks/meacompass-f2-20260929-c`. No files were copied from
the working tree. A distinct `.venv-system` environment used Python 3.11.16 with
the existing `ais` environment as its read-only system-package base; this was an
isolation and packaging check, not a cold dependency-download benchmark.

| Step | Result | Elapsed |
|---|---:|---:|
| Local clone | clean commit `093d08e` | 0.93 s |
| Venv creation | distinct prefix resolved | 0.10 s |
| `make setup` | editable package installed | 6.07 s |
| `make fetch-results` | 7/7 hashes verified, 8.34 MiB | 0.19 s |
| `make test` | 56/56 passed | 3.57 s |
| `make reproduce-lite` | 5/5 artifacts regenerated | 1.39 s |
| `make demo` smoke test | HTTP 200, 7,260-byte page | 0.04 s response |

The five regenerated artifacts were `main_results.csv`, `risk_coverage.png`,
`time_ablation.png`, `dose_strata.png`, and `calibration.png`. `git status
--porcelain` was empty after setup and reproduction. The Streamlit process was
stopped immediately after the HTTP check.

The check exposed and fixed a Windows portability issue: Python executable paths
were unquoted and GNU Make selected its MSYS shell. All Python invocations are now
quoted, and the Makefile selects `cmd.exe` only on Windows while retaining the
default POSIX shell elsewhere.
