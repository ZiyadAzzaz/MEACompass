PYTHON ?= python
RESULTS_DIR ?= results
ARTIFACTS_DIR ?= artifacts/reproduce-lite

.PHONY: setup reproduce-lite demo test baselines bt-plus m1 audit

setup:
	$(PYTHON) -m pip install -e ".[test,demo]"

test:
	$(PYTHON) -m pytest -q -p no:cacheprovider

reproduce-lite:
	$(PYTHON) -m neurochip.reproduce_lite --results-dir $(RESULTS_DIR) --output-dir $(ARTIFACTS_DIR)

demo:
	$(PYTHON) -m streamlit run app/streamlit_app.py

audit:
	$(PYTHON) scripts/audit_epa_nfa.py

baselines:
	$(PYTHON) -m neurochip.train_baselines --config configs/baselines.yaml

bt-plus:
	$(PYTHON) -m neurochip.build_bt_plus --config configs/baselines.yaml

m1:
	$(PYTHON) -m neurochip.train_m1 --config configs/baselines.yaml
