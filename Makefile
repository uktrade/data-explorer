TEST ?= .
BLACK_CONFIG ?= --exclude=venv --skip-string-normalization --line-length 100
CHECK ?= --check

.PHONY: run_tests
run_tests:
	DEBUG=False pytest -v ${TEST}

.PHONY: run_tests_local
run_tests_local:
	USE_DOTENV=1 TESTING=1 pytest -s ${TEST}

check: flake8 black

format: CHECK=
format: black

black:
	black ${BLACK_CONFIG} ${CHECK} .

flake8:
	flake8 .