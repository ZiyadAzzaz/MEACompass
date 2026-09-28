PYTHON ?= python

.PHONY: test baselines m1 audit

test:
	$(PYTHON) -m pytest -q

audit:
	$(PYTHON) scripts/audit_epa_nfa.py

baselines:
	$(PYTHON) -m neurochip.train_baselines --config configs/baselines.yaml

m1:
	$(PYTHON) -m neurochip.train_m1 --config configs/baselines.yaml
