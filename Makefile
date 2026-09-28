PYTHON ?= python

.PHONY: test baselines audit

test:
	$(PYTHON) -m pytest -q

audit:
	$(PYTHON) scripts/audit_epa_nfa.py

baselines:
	$(PYTHON) -m neurochip.train_baselines --config configs/baselines.yaml

