.PHONY: env vizier gaia lamost xmatch simbad final all clean test

PY := python

env:
	$(PY) scripts/00_check_env.py

vizier:
	$(PY) scripts/01_fetch_vizier_hivel_catalogs.py

gaia: vizier
	$(PY) scripts/02_fetch_gaia_dr3_fields.py

lamost:
	$(PY) scripts/03_fetch_lamost_catalogs.py

xmatch: gaia lamost
	$(PY) scripts/04_crossmatch_lamost_gaia.py

simbad: xmatch
	$(PY) scripts/05_fetch_simbad_validation.py

final: simbad
	$(PY) scripts/06_build_final_dataset.py

all: env final

test:
	pytest -q

clean:
	rm -rf cache/* logs/*.log data/interim/* data/processed/*
