import json
from pathlib import Path

import yaml

from meacompass.final_model import derive_final_hyperparameters


ROOT = Path(__file__).resolve().parents[1]


def test_final_hyperparameters_are_deterministic_and_complete() -> None:
    records = json.loads((ROOT / "results" / "m1_tuning.json").read_text(encoding="utf-8"))
    config = yaml.safe_load((ROOT / "configs" / "baselines.yaml").read_text(encoding="utf-8"))
    first = derive_final_hyperparameters(records, config)
    second = derive_final_hyperparameters(list(reversed(records)), config)

    assert first == second
    assert first["source_records"] == 75
    assert set(first["endpoints"]) == set(config["primary_endpoints"])
    for endpoint, setting in first["endpoints"].items():
        assert len(setting["source_seed_fold_pairs"]) == 15, endpoint
        assert setting["variant"] in {"direct", "bt_residual"}
        assert setting["bt_model"] in {"B0", "B1", "B1b", "B2"}
        assert setting["parameters"]["n_estimators"] >= 1


def test_final_model_rule_does_not_reference_external_outcomes() -> None:
    source = (ROOT / "meacompass" / "final_model.py").read_text(encoding="utf-8")
    assert "data/external/f3b" not in source
    assert "refinement" not in source.lower()
