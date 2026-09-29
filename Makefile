PYTHON ?= python
RESULTS_DIR ?= results
ARTIFACTS_DIR ?= artifacts/reproduce-lite

ifeq ($(OS),Windows_NT)
SHELL := cmd.exe
.SHELLFLAGS := /C
endif

.PHONY: setup fetch-results data train-all reproduce-lite demo static-demo test baselines bt-plus m1 audit

setup:
	"$(PYTHON)" -m pip install -e ".[test,demo]"

fetch-results:
	"$(PYTHON)" -m meacompass.fetch_results --manifest results/results_manifest.json

data:
	"$(PYTHON)" -m meacompass.fetch_data --manifest schemas/epa_downloads_v1.json

train-all:
	"$(PYTHON)" -m meacompass.train_all $(if $(filter 1,$(CONFIRM_LOCKED_REBUILD)),--confirm-locked-rebuild,)

test:
	"$(PYTHON)" -m pytest -q -p no:cacheprovider

reproduce-lite:
	"$(PYTHON)" -m meacompass.reproduce_lite --results-dir $(RESULTS_DIR) --output-dir $(ARTIFACTS_DIR)

demo:
	"$(PYTHON)" -m streamlit run app/streamlit_app.py

static-demo:
	"$(PYTHON)" scripts/build_static_demo.py

audit:
	"$(PYTHON)" scripts/audit_epa_nfa.py

baselines:
	"$(PYTHON)" -m meacompass.train_baselines --config configs/baselines.yaml

bt-plus:
	"$(PYTHON)" -m meacompass.build_bt_plus --config configs/baselines.yaml

m1:
	"$(PYTHON)" -m meacompass.train_m1 --config configs/baselines.yaml
