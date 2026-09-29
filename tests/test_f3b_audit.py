import pandas as pd

from meacompass.data import PRIMARY_ENDPOINTS
from meacompass.f3b_audit import NETWORK_METRICS, _metric_record


def test_absent_required_feature_fails_closed() -> None:
    overlap = pd.DataFrame({"cv.time_old": [1.0, 2.0]})
    record = _metric_record(overlap, "cv.time")
    assert record["status"] == "NOT_COMPARABLE"
    assert record["available_refinement"] is False


def test_frozen_contract_covers_all_endpoints_and_inputs() -> None:
    assert set(PRIMARY_ENDPOINTS).issubset(NETWORK_METRICS)
    assert {"cv.time", "cv.network"}.issubset(NETWORK_METRICS)
