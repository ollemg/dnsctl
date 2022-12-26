.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/pip').exists(): print('.venv/bin/')")
USING_POETRY=$(shell grep "tool.poetry" pyproject.toml && echo "yes")
GIT_VERSION=$(shell git rev-parse --abbrev-ref HEAD)
#cnf ?= .env
#include $(cnf)
#export $(shell sed 's/=.*//' $(cnf))


all: release deploy

.PHONY: help
help:		## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "** Sem target é executado requirements e deploy **"
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@if [ "$(USING_POETRY)" ]; then poetry env info && exit; fi
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@if [ "$(USING_POETRY)" ]; then poetry install && exit; fi
	@echo "Don't forget to run 'make virtualenv' if you got errors."
	$(ENV_PREFIX)pip install -e .[test]


.PHONY: lint
lint:             ## Run pep8
	$(ENV_PREFIX)blue dnsctl/
	$(ENV_PREFIX)isort dnsctl/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v
	$(ENV_PREFIX)bandit ./dnsctl
	$(ENV_PREFIX)pip-audit

