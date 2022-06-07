POETRY          := $(shell command -v poetry 2> /dev/null)
ADD_ON_VERSION  := $$(grep version ./Splunk_TA_censys/app.manifest | sed 's/[^0-9.]*//g')
ASM_APP_VERSION := $$(grep version ./censys/app.manifest | sed 's/[^0-9.]*//g')

.PHONY: all
all: help

.PHONY: install
install:  ## Install developer dependencies
	poetry install

.PHONY: build-add-on
build-add-on:  ## Build Splunk Add-on
	poetry run slim package Splunk_TA_censys

.PHONY: build-asm-app
build-asm-app:  ## Build Splunk ASM App
	poetry run slim package censys

.PHONY: build
build: build-add-on build-asm-app  ## Build Splunk Add-on and ASM App

.PHONY: appinspect-add-on
appinspect-add-on:  ## Run Splunk AppInspect on Splunk Add-on
	poetry run splunk-appinspect inspect Splunk_TA_censys-$(ADD_ON_VERSION).tar.gz --included-tags cloud

.PHONY: appinspect-asm-app
appinspect-asm-app:  ## Run Splunk AppInspect on Splunk ASM App
	poetry run splunk-appinspect inspect censys-$(ASM_APP_VERSION).tar.gz --included-tags cloud

.PHONY: appinspect
appinspect: appinspect-add-on appinspect-asm-app  ## Run Splunk AppInspect

.PHONY: test-add-on
test-add-on:  ## Run Splunk Add-on Pytest
	poetry run pytest -v --tb=long --splunk-type=docker --splunk-app=Splunk_TA_censys/ --splunk-data-generator=Splunk_TA_censys/default/ --cim-report=CIM.md

.PHONY: test-asm-app
test-asm-app:
	@echo "Coming soon..."

.PHONY: tests
tests: test-add-on ## Run tests

.PHONY: lint
lint: ## Run linters
	poetry run isort .
	poetry run pyupgrade Splunk_TA_censys/bin/*.py --py37

.PHONY: link-asm-app
link-asm-app:  ## Link Splunk ASM App
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	ln -s $$(pwd)/censys/ ${SPLUNK_HOME}/etc/apps/censys

.PHONY: link-add-on
link-add-on:  ## Link Splunk Add-on
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	ln -s $$(pwd)/Splunk_TA_censys/ ${SPLUNK_HOME}/etc/apps/Splunk_TA_censys

.PHONY: link
link: link-asm-app link-add-on  ## Link Splunk Add-on and Splunk ASM App

.PHONY: splunk-restart
splunk-restart:  ## Restart local Splunk
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	${SPLUNK_HOME}/bin/splunk restart

# via https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:  ## Show make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
