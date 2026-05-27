SHELL := /bin/bash

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PLACE_DIR := $(ROOT_DIR)/place
PY_DIR := $(PLACE_DIR)/Constraints_Extraction
CPP_DIR := $(PLACE_DIR)/SubgraphMatching-master
VENV_DIR := $(ROOT_DIR)/.venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

BUILD_ARGS := $(filter-out build,$(MAKECMDGOALS))

.PHONY: build all SubgraphMatching-master Constraints_Extraction build-all build-python build-cpp shell setup run clean

build:
ifeq ($(BUILD_ARGS),)
	@$(MAKE) build-all
else
	@:
endif

all: build-all

setup: build-all shell

run:
	@"$(PYTHON)" "$(PY_DIR)/spice_annotation.py" "$(PY_DIR)/circuit.json"

SubgraphMatching-master: build-cpp

Constraints_Extraction: build-python

build-all: build-cpp build-python

build-cpp:
	@echo "[1/2] Build C++ matcher"
	@if [ ! -d "$(CPP_DIR)" ]; then \
		echo "ERROR: C++ directory not found: $(CPP_DIR)"; \
		exit 1; \
	fi
	@mkdir -p "$(CPP_DIR)/build"
	@cd "$(CPP_DIR)/build" && cmake .. && $(MAKE)

build-python:
	@echo "[2/2] Prepare Python environment"
	@if [ ! -d "$(VENV_DIR)" ]; then \
		python3 -m venv "$(VENV_DIR)"; \
	elif ! grep -q "VIRTUAL_ENV=.*$(VENV_DIR)" "$(VENV_DIR)/bin/activate" 2>/dev/null; then \
		echo "Detected stale venv path, recreating $(VENV_DIR)"; \
		rm -rf "$(VENV_DIR)"; \
		python3 -m venv "$(VENV_DIR)"; \
	fi
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install -r "$(ROOT_DIR)/requirements.txt"
	@echo "Python venv ready: $(VENV_DIR)"
	@echo "Enter it with: make shell"

shell:
	@bash --noprofile --norc -c 'source "$(VENV_DIR)/bin/activate" && cd "$(ROOT_DIR)" && exec bash --noprofile --norc'

clean:
	@echo "No default clean action. Remove .venv or place/SubgraphMatching-master/build manually if needed."
