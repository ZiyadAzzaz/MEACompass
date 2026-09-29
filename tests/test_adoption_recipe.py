from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def test_mea_input_schema_has_required_contract() -> None:
    schema = yaml.safe_load((ROOT / "schemas" / "mea_input_v1.yaml").read_text(encoding="utf-8"))
    required = schema["required_columns"]

    assert {"chemical_id", "dose", "plate", "well", "DIV"}.issubset(required)
    assert {"burst.per.min", "meanfiringrate", "nAE", "ns.n", "r"}.issubset(required)
    assert schema["required_divs"] == {"primary_inputs": [5, 7], "target": 12}
    assert schema["normalization"]["method"] == "same_plate_same_div_zero_dose_percent_control"
    assert schema["deployment_boundary"]["frozen_epa_model_direct_deployment"] == "prohibited"


def test_adoption_recipe_keeps_local_validation_boundary() -> None:
    recipe = " ".join(
        (ROOT / "docs" / "adoption_recipe.md").read_text(encoding="utf-8").lower().split()
    )
    readme = " ".join((ROOT / "README.md").read_text(encoding="utf-8").lower().split())

    for text in (recipe, readme):
        assert "not evidence that the frozen epa model can be deployed directly" in text
        assert "local" in text
        assert "prospective" in text
    assert "chemical-disjoint" in recipe
    assert "outer-test labels are evaluation only" in recipe
    assert "not an autonomous" in recipe
