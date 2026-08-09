# Convenience targets. `make help` lists them. Uses uv when available.
.DEFAULT_GOAL := help
.PHONY: help setup dev test lint fmt build clean docker publish-test publish

PY ?= python

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

setup: ## Create a venv and install the package with dev extras (uv)
	uv venv && uv pip install -e ".[dev]"

dev: ## Editable install with dev extras into the active environment (pip)
	$(PY) -m pip install -e ".[dev]"

test: ## Run the test suite
	pytest

lint: ## Lint with ruff
	ruff check .

fmt: ## Auto-fix lint + format with ruff
	ruff check --fix . && ruff format .

build: ## Build sdist + wheel into dist/
	uv build || $(PY) -m build

clean: ## Remove build artifacts and caches
	rm -rf dist build *.egg-info src/*.egg-info .pytest_cache .ruff_cache

docker: ## Build the Docker image
	docker build -t mytool:latest .

publish-test: build ## Upload to TestPyPI
	twine upload --repository testpypi dist/*

publish: build ## Upload to PyPI
	twine upload dist/*
