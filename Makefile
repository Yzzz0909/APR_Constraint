SHELL := /bin/bash

ROOT_DIR := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PLACE_DIR := $(ROOT_DIR)/place
PY_DIR := $(PLACE_DIR)/Constraints_Extraction
CPP_DIR := $(PLACE_DIR)/SubgraphMatching-master
VENV_DIR := $(ROOT_DIR)/.venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

BUILD_ARGS := $(filter-out build,$(MAKECMDGOALS))

.PHONY: build all SubgraphMatching-master Constraints_Extraction build-all build-python build-cpp clean

build:
ifeq ($(BUILD_ARGS),)
	@$(MAKE) build-all
else
	@:
endif

all: build-all

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
	fi
	@$(PYTHON) -m pip install --upgrade pip
	@$(PIP) install -r "$(ROOT_DIR)/requirements.txt"
	@echo "Python venv ready: $(VENV_DIR)"
	@echo "Activate with: source .venv/bin/activate"

clean:
	@echo "No default clean action. Remove .venv or place/SubgraphMatching-master/build manually if needed."