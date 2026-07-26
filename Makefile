.PHONY: validate freshness discovery discovery-accept readme readme-check dataset-access-index dataset-access-index-check source-platform-index source-platform-index-check model-data-index model-data-index-check site-data site-data-check test check-links audit-example audit-example-check check

PYTHON ?= $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

validate:
	$(PYTHON) scripts/validate_catalog.py
	$(PYTHON) scripts/validate_models.py
	$(PYTHON) scripts/validate_source_platforms.py

freshness:
	$(PYTHON) scripts/check_freshness.py

discovery:
	$(PYTHON) scripts/discover_updates.py --json-out /tmp/aigcdatahub-discovery.json --markdown-out /tmp/aigcdatahub-discovery.md

discovery-accept:
	$(PYTHON) scripts/discover_updates.py --accept-current --json-out /tmp/aigcdatahub-discovery.json --markdown-out /tmp/aigcdatahub-discovery.md

readme:
	$(PYTHON) scripts/build_readme.py

readme-check:
	$(PYTHON) scripts/build_readme.py --check

dataset-access-index:
	$(PYTHON) scripts/build_dataset_access_index.py

dataset-access-index-check:
	$(PYTHON) scripts/build_dataset_access_index.py --check

source-platform-index:
	$(PYTHON) scripts/build_source_platform_index.py

source-platform-index-check:
	$(PYTHON) scripts/build_source_platform_index.py --check

model-data-index:
	$(PYTHON) scripts/build_model_dataset_index.py

model-data-index-check:
	$(PYTHON) scripts/build_model_dataset_index.py --check

site-data:
	$(PYTHON) scripts/build_site_data.py

site-data-check:
	$(PYTHON) scripts/build_site_data.py --check

test:
	$(PYTHON) -m unittest discover -s tests -v

check-links:
	$(PYTHON) scripts/check_links.py

audit-example:
	$(PYTHON) scripts/audit_manifest.py examples/manifests/tiny-multimodal.jsonl --sample-size 8 --json-out examples/reports/tiny-multimodal.json --markdown-out examples/reports/tiny-multimodal.md --fail-on-invalid --min-provenance-coverage 1

audit-example-check:
	$(PYTHON) scripts/audit_manifest.py examples/manifests/tiny-multimodal.jsonl --sample-size 8 --json-out examples/reports/tiny-multimodal.json --markdown-out examples/reports/tiny-multimodal.md --fail-on-invalid --min-provenance-coverage 1 --check

check: validate freshness readme-check dataset-access-index-check source-platform-index-check model-data-index-check site-data-check audit-example-check test
