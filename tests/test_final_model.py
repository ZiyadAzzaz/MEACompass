import json
import hashlib
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


def test_final_model_manifest_records_three_models_per_endpoint() -> None:
    manifest = json.loads(
        (ROOT / "schemas" / "final_model_manifest.json").read_text(encoding="utf-8")
    )
    models = [item for item in manifest["artifacts"] if "/m1_" in item["path"] and "residual_baseline" not in item["path"]]
    assert manifest["training_chemicals"] == 136
    assert manifest["seeds"] == [0, 1, 2]
    assert len(models) == 15
    assert all(len(item["sha256"]) == 64 for item in manifest["artifacts"])

    local_artifacts = ROOT / "results" / "final_model"
    if local_artifacts.exists():
        for item in manifest["artifacts"]:
            path = ROOT / item["path"]
            assert path.stat().st_size == item["bytes"]
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]
