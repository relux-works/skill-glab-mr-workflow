.PHONY: install skill test

install:
	@test -n "$(REPO)" || { echo "REPO=/abs/path/to/repo is required" >&2; exit 1; }
	python3 scripts/setup_main.py "$(REPO)" $(if $(LOCALE),--locale "$(LOCALE)")

skill:
	@python3 scripts/bootstrap_runtime.py --quiet

test:
	@python3 -m unittest -q tests.test_gmr_main tests.test_setup_support
