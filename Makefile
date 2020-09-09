TEST ?= .
BLACK_CONFIG ?= --exclude=venv --skip-string-normalization --line-length 100
CHECK ?= --check

.PHONY: run_tests
run_tests:
	DJANGO_SETTINGS_MODULE=explorer.settings.test DEBUG=True pytest --ignore explorer/tests/functional -v ${TEST}

.PHONY: run_tests_local
run_tests_local:
	DJANGO_SETTINGS_MODULE=explorer.settings.test DEBUG=True pytest --ignore explorer/tests/functional -s ${TEST}

.PHONY: docker-build
docker-build:
	docker-compose -f docker-compose-test.yml -p data-explorer-test build

.PHONY: docker-test
docker-test: docker-build
	docker-compose -f docker-compose-test.yml -p data-explorer-test run explorer pytest ${TEST}

check: flake8 black

format: CHECK=
format: black

black:
	black ${BLACK_CONFIG} ${CHECK} .

flake8:
	flake8 .
