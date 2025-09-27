.PHONY: help install test lint format clean build run-gui run-cli dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync

install-pip: ## Install dependencies with pip
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

test-coverage: ## Run tests with coverage
	pytest tests/ --cov=src/report_automation --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code with black
	black src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +

build: ## Build package
	python -m build

run-gui: ## Run GUI application
	python scripts/run_gui.py

run-cli: ## Run CLI application
	python scripts/run_cli.py

dev: ## Install development dependencies
	uv sync --extra dev

dev-pip: ## Install development dependencies with pip
	pip install -r requirements.txt
	pip install -e ".[dev]"

setup-dev: ## Setup development environment
	@echo "Setting up development environment..."
	@echo "Installing dependencies..."
	uv sync --extra dev
	@echo "Creating pre-commit hook..."
	@echo "#!/bin/bash" > .git/hooks/pre-commit
	@echo "echo 'Running tests and linting...'" >> .git/hooks/pre-commit
	@echo "make test" >> .git/hooks/pre-commit
	@echo "make lint" >> .git/hooks/pre-commit
	@echo "make format-check" >> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "Development environment setup complete!"

demo: ## Run demo report generation
	@echo "Running demo report generation..."
	python scripts/run_cli.py

check: ## Run all checks (test, lint, format)
	make test
	make lint
	make format-check

release-check: ## Check if ready for release
	@echo "Checking if ready for release..."
	@echo "Running all checks..."
	make check
	@echo "Building package..."
	make build
	@echo "Release check complete!"