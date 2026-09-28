# Decision log

## 2026-09-28 — Gates N0/N1: data feasibility

- Evidence: 136 unique CAS RNs, 4,344 per-well trajectories, DIV5/7/9/12,
  96.5% complete trajectories, 95.6% PubChem SMILES resolution.
- Decision: make NeuroChip the primary project, while keeping CellTwin-X as the
  measured fallback until Gate L1.
- Claim constraint: EPA NFA is a rat cortical neural MEA assay, not OoC data.
- Full evidence: `docs/neurochip_data_audit.md`.

## 2026-09-28 — Phase 2 protocol corrections

- Primary split: canonical-CAS-disjoint, with all aliases and biological
  replicates grouped together.
- Control definition: same-plate, same-DIV median across all dose-zero wells.
  Dose-zero rows are stored under compound labels; no literal DMSO group exists.
- Constant prediction metrics: undefined Spearman values remain missing and are
  never replaced by zero.
- Primary category remains Model & Algorithm unless the final implementation
  demonstrates a genuinely complete research workflow.

