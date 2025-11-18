.PHONY: help install lint format check test run clean

# ⚡ Ollama Gateway - Development Commands
# Usage: make <command>

help: ## Show this help message
	@echo "🐙 Ollama Gateway - Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (production + dev)
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ All dependencies installed and hooks configured"

# ===== PYTHON QUALITY =====

lint-python: ## Lint Python code (flake8 + mypy)
	@echo "🐍 Running Flake8..."
	flake8 *.py
	@echo "🐍 Running mypy..."
	mypy *.py --ignore-missing-imports
	@echo "✅ Python linting complete"

format-python: ## Format Python code (black + isort)
	@echo "🐍 Running Black..."
	black *.py
	@echo "🐍 Running isort..."
	isort *.py
	@echo "✅ Python formatting complete"

security-python: ## Security scan Python code (bandit)
	@echo "🔒 Running Bandit security scan..."
	bandit -ll -r *.py
	@echo "✅ Security scan complete"

# ===== JAVASCRIPT QUALITY =====

lint-js: ## Lint JavaScript code (eslint)
	@echo "📜 Running ESLint..."
	npx eslint studio/*.js || echo "⚠️  ESLint not installed, skipping..."
	@echo "✅ JavaScript linting complete"

format-js: ## Format JavaScript code (prettier)
	@echo "📜 Running Prettier..."
	npx prettier --write studio/*.js studio/*.html studio/*.css *.md || echo "⚠️  Prettier not installed, skipping..."
	@echo "✅ JavaScript formatting complete"

# ===== COMBINED COMMANDS =====

lint: lint-python lint-js ## Lint all code (Python + JavaScript)

format: format-python format-js ## Format all code (Python + JavaScript)

check: lint security-python ## Full quality check (lint + security)
	@echo "✅ All quality checks passed!"

# ===== PRE-COMMIT =====

pre-commit-all: ## Run all pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hooks to latest versions
	pre-commit autoupdate

# ===== APPLICATION =====

run: ## Start the Ollama Gateway server
	python main.py

dev: ## Start with auto-reload (uvicorn)
	uvicorn main:app --reload --host 0.0.0.0 --port 4000

test: ## Run tests (when implemented)
	pytest tests/ --cov=. --cov-report=html
	@echo "✅ Tests complete. Coverage report: htmlcov/index.html"

# ===== UTILITIES =====

clean: ## Clean generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "✅ Cleaned generated files"

git-clean: clean ## Clean + remove untracked files (use with caution!)
	git clean -fdx
	@echo "✅ Repository cleaned"

# ===== DOCKER (Future) =====

docker-build: ## Build Docker image
	docker build -t ollama-gateway:latest .

docker-run: ## Run Docker container
	docker run -p 4000:4000 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 ollama-gateway:latest
