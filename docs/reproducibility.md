# Reproducibility record

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

The clean-clone verification record is appended only after execution. It must
use a new directory and environment, validate the committed bundle, run all tests,
regenerate the five result-only outputs, and execute the Streamlit app test without
copying files from the working tree.
