POETRY          := $(shell command -v poetry 2> /dev/null)
ADD_ON_VERSION  := $$(grep version ./Splunk_TA_censys/app.manifest | sed 's/[^0-9.]*//g')
ASM_APP_VERSION := $$(grep version ./censys_asm_app/app.manifest | sed 's/[^0-9.]*//g')

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
	poetry run slim package censys_asm_app

.PHONY: build
build: build-add-on build-asm-app

.PHONY: appinspect-add-on
appinspect-add-on:  ## Run Splunk AppInspect
	poetry run splunk-appinspect inspect Splunk_TA_censys-$(ADD_ON_VERSION).tar.gz --included-tags cloud

.PHONY: appinspect-asm-app
appinspect-asm-app:  ## Run Splunk AppInspect
	poetry run splunk-appinspect inspect censys_asm_app-$(ASM_APP_VERSION).tar.gz --included-tags cloud

.PHONY: appinspect
appinspect: appinspect-add-on appinspect-asm-app

# via https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:  ## Show make help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'