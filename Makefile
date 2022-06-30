POETRY          := $(shell command -v poetry 2> /dev/null)
ADD_ON_VERSION  := $$(grep version ./packages/Splunk_TA_censys/app.manifest | sed 's/[^0-9.]*//g')
APP_VERSION     := $$(grep version ./packages/censys/src/main/resources/splunk/app.manifest | sed 's/[^0-9.]*//g')
APPINSPECT_ARGS := --included-tags cloud --included-tags future --included-tags custom_workflow_actions --included-tags inputs_conf --included-tags splunk_9_0

.PHONY: all
all: help

.PHONY: install
install:  ## Install developer dependencies
	poetry install
	yarn install

.PHONY: build-add-on
build-add-on:  ## Build Splunk Add-on
	poetry run slim package ./packages/Splunk_TA_censys

.PHONY: build-app
build-app:  ## Build Splunk App
	yarn workspace @splunk/censys run build:prod
	poetry run slim package ./packages/censys/censys

.PHONY: build
build: build-add-on build-app  ## Build Splunk Add-on and App

.PHONY: docs
docs:  ## Generate documentation
	cd docs && make html

.PHONY: appinspect-add-on
appinspect-add-on:  ## Run Splunk AppInspect on Splunk Add-on
	poetry run splunk-appinspect inspect Splunk_TA_censys-$(ADD_ON_VERSION).tar.gz $(APPINSPECT_ARGS)

.PHONY: appinspect-app
appinspect-app:  ## Run Splunk AppInspect on Splunk App
	poetry run splunk-appinspect inspect censys-$(APP_VERSION).tar.gz $(APPINSPECT_ARGS)

.PHONY: appinspect
appinspect: appinspect-add-on appinspect-app  ## Run Splunk AppInspect

.PHONY: test-add-on
test-add-on:  ## Run Splunk Add-on Pytest
	poetry run pytest

.PHONY: test-app
test-app:
	yarn run test

.PHONY: tests
tests: test-add-on test-app  ## Run tests

.PHONY: lint
lint: ## Run linters
	poetry run isort .
	poetry run pyupgrade packages/Splunk_TA_censys/bin/*.py --py37

.PHONY: link-app
link-app:  ## Link Splunk App
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	yarn workspace @splunk/censys run link:app

.PHONY: link-add-on
link-add-on:  ## Link Splunk Add-on
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	ln -s $$(pwd)/packages/Splunk_TA_censys/ ${SPLUNK_HOME}/etc/apps/Splunk_TA_censys

.PHONY: link
link: link-app link-add-on  ## Link Splunk Add-on and Splunk App

.PHONY: splunk-restart
splunk-restart:  ## Restart local Splunk
	@if [ -z ${SPLUNK_HOME} ]; then echo "SPLUNK_HOME is not set. Please set it and re-run this command."; exit 1; fi
	${SPLUNK_HOME}/bin/splunk restart

# via https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:  ## Show make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
