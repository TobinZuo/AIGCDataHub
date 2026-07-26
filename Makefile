.PHONY: validate freshness readme readme-check site-data site-data-check test check-links audit-example audit-example-check check

validate:
	python3 scripts/validate_catalog.py
	python3 scripts/validate_models.py

freshness:
	python3 scripts/check_freshness.py

readme:
	python3 scripts/build_readme.py

readme-check:
	python3 scripts/build_readme.py --check

site-data:
	python3 scripts/build_site_data.py

site-data-check:
	python3 scripts/build_site_data.py --check

test:
	python3 -m unittest discover -s tests -v

check-links:
	python3 scripts/check_links.py

audit-example:
	python3 scripts/audit_manifest.py examples/manifests/tiny-multimodal.jsonl --sample-size 8 --json-out examples/reports/tiny-multimodal.json --markdown-out examples/reports/tiny-multimodal.md --fail-on-invalid --min-provenance-coverage 1

audit-example-check:
	python3 scripts/audit_manifest.py examples/manifests/tiny-multimodal.jsonl --sample-size 8 --json-out examples/reports/tiny-multimodal.json --markdown-out examples/reports/tiny-multimodal.md --fail-on-invalid --min-provenance-coverage 1 --check

check: validate freshness readme-check site-data-check audit-example-check test
