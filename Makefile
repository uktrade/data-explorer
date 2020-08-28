TEST ?= .
BLACK_CONFIG ?= --exclude=venv --skip-string-normalization --line-length 100
CHECK ?= --check

.PHONY: run_tests
run_tests:
	DJANGO_SETTINGS_MODULE=explorer.settings.test DEBUG=True pytest -v ${TEST}

.PHONY: run_tests_local
run_tests_local:
	DJANGO_SETTINGS_MODULE=explorer.settings.test DEBUG=True pytest -s ${TEST}

check: flake8 black

format: CHECK=
format: black

black:
	black ${BLACK_CONFIG} ${CHECK} .

flake8:
	flake8 .