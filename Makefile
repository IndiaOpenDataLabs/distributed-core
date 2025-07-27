# Makefile for IndicCultureHub/scripture-assistant

SHELL    := /usr/bin/env bash
PYTHON   := python3
VENV_DIR := .venv

#––– ANSI colour definitions –––
ESC    := $(shell printf "\033")
CSI    := $(ESC)[
RESET  := $(CSI)0m
BOLD   := $(CSI)1m
GREEN  := $(CSI)0;32m
YELLOW := $(CSI)0;33m
MAGENTA := $(CSI)0;35m
CYAN   := $(CSI)0;36m

.PHONY: help venv install lint format test clean build docker-build docker-compose-up docker-compose-logs docker-compose-stop docker-compose-down docker-clean-images

help:
	@printf "$(BOLD)$(CYAN)Available targets:$(RESET)\n\n"

	@printf "$(MAGENTA)Local Development:$(RESET)\n"
	@for td in \
		venv:"Create a virtual environment in $(VENV_DIR) using uv" \
		install:"Install project and development dependencies using uv" \
		sync:"Sync the virtual environment with all groups using uv" \
		check-env:"Check if a virtual environment is active" \
		serve:"Run the FastAPI application using Gunicorn" \
		; do \
	  name=$${td%%:*}; desc=$${td#*:}; \
	  printf "  $(BOLD)%s$(RESET) — %s\n" "$$name" "$$desc"; \
		done

	@printf "\n$(MAGENTA)Code Quality:$(RESET)\n"
	@for td in \
		lint:"Run linters (ruff, flake8, pylint) on the codebase" \
		format:"Format code using black and isort" \
		clean:"Remove Python cache and build artifacts" \
		; do \
	  name=$${td%%:*}; desc=$${td#*:}; \
	  printf "  $(BOLD)%s$(RESET) — %s\n" "$$name" "$$desc"; \
		done

	@printf "\n$(MAGENTA)Docker Commands:$(RESET)\n"
	@for td in \
		docker-build:"Build the application Docker image using buildx" \
		docker-compose-up:"Start all services (app and Redis) in detached mode" \
		docker-compose-logs:"Follow logs for all services" \
		docker-compose-stop:"Stop all running services" \
		docker-compose-down:"Stop and remove all services, networks, and volumes" \
		docker-clean-images:"Remove application Docker images and prune dangling images" \
		; do \
	  name=$${td%%:*}; desc=$${td#*:}; \
	  printf "  $(BOLD)%s$(RESET) — %s\n" "$$name" "$$desc"; \
		done

	@printf "\n$(MAGENTA)Publishing:$(RESET)\n"
	@for td in \
		build:"Build distribution packages (wheel and sdist)" \
		publish-test:"Upload to TestPyPI" \
		publish-pypi:"Upload to PyPI" \
		; do \
	  name=$${td%%:*}; desc=$${td#*:}; \
	  printf "  $(BOLD)%s$(RESET) — %s\n" "$$name" "$$desc"; \
		done

	@printf "\n$(MAGENTA)Other:$(RESET)\n"
	@printf "  $(BOLD)help$(RESET) — Show this help message\n"

check-env:
	@# warn if no venv is active
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		printf "$(YELLOW)⚠️  Warning: Virtual environment is not active. Activate with: $(RESET)$(BOLD)$(CYAN)source $(VENV_DIR)/bin/activate$(RESET)$(YELLOW) before starting application.$(RESET)\n"; \
	fi

venv:
	@if [ ! -d "$(VENV_DIR)" ]; then \
	  uv venv $(VENV_DIR) --python $(PYTHON); \
	elif [ "$$VIRTUAL_ENV" = "$$(pwd)/$(VENV_DIR)" ]; then \
	  printf "$(GREEN)Virtual environment at %s is ready and already activated!$(RESET)\n" "$(VENV_DIR)"; \
	else \
	  printf "$(YELLOW)Virtual environment already exists at %s. To activate, run:$(RESET) $(BOLD)$(CYAN)source %s/bin/activate$(RESET)\n" \
	    "$(VENV_DIR)" "$(VENV_DIR)"; \
	fi

sync: venv
	@printf "$(CYAN)🔄 Syncing environment…$(RESET)\n"
	@uv sync --all-groups

install: sync check-env
	@printf "$(GREEN)Project is ready! Virtual environment at $(VENV_DIR) is populated.$(RESET)\n"

lint:
	@printf "$(CYAN)Running linters…$(RESET)\n"
	@uv run --no-sync ruff check .
	@uv run --no-sync ruff format . --check # Checks formatting without modifying files
	@uv run --no-sync pylint .
	@printf "$(GREEN)Linters finished successfully!$(RESET)\n"

format:
	@printf "$(CYAN)Applying auto-formatting and fixes…$(RESET)\n"
	@uv run --no-sync ruff format . # This replaces black and isort
	@uv run --no-sync ruff check . --fix # This replaces autoflake (for unused imports/variables)
	@printf "$(GREEN)Auto-formatting and fixes applied!$(RESET)\n"

# test: venv
# 	@printf "$(CYAN)Running tests…$(RESET)\n"
# 	@uv run pytest tests

# build: venv
# 	@printf "$(CYAN)Building project…$(RESET)\n"
# 	@uv run python -m build

clean:
	@read -p "$(YELLOW)⚠️  This will delete your virtual environment at $(RESET)$(BOLD)$(CYAN)$(VENV_DIR)$(RESET)$(YELLOW) plus all $(RESET)$(BOLD)$(CYAN)build/test/docs artifacts$(RESET)$(YELLOW). Continue? [y/N] $(RESET)" ans; \
	if [ "$ans" != "y" ]; then \
	  echo "Aborted."; exit 0; \
	fi; \
	printf "$(YELLOW)Cleaning up project…$(RESET)\n"; \
	rm -rf \
	  $(VENV_DIR) \
	  build/ \
	  dist/ \
	  *.egg-info/ \
	  pip-wheel-metadata/ \
	  .pytest_cache/ \
	  .mypy_cache/ \
	  .ruff_cache/ \
	  .coverage/ \
	  htmlcov/ \
	  docs/_build/ \
	  site/; \
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type f -name "*.pyc" -delete 2>/dev/null; \
	find . -type f \( -name "*.swp" -o -name "*.swo" -o -name ".DS_Store" \) -delete 2>/dev/null

build: venv
	@printf "$(CYAN)Building distribution packages…$(RESET)\n"
	@uv run python -m build
	@printf "$(GREEN)Distribution packages built in dist/$(RESET)\n"

publish-test: build
	@read -p "$(YELLOW)⚠️  Are you sure you want to upload to TestPyPI? [y/N] $(RESET)" ans; \
	if [ "$ans" != "y" ]; then \
	  echo "Aborted."; exit 0; \
	fi; \
	@printf "$(CYAN)Uploading to TestPyPI…$(RESET)\n"
	@uv run twine upload --repository testpypi dist/*
	@printf "$(GREEN)Uploaded to TestPyPI!$(RESET)\n"

publish-pypi: build
	@read -p "$(YELLOW)⚠️  Are you sure you want to upload to PyPI? This is a public release! [y/N] $(RESET)" ans; \
	if [ "$ans" != "y" ]; then \
	  echo "Aborted."; exit 0; \
	fi; \
	@printf "$(CYAN)Uploading to PyPI…$(RESET)\n"
	@uv run twine upload dist/*
	@printf "$(GREEN)Uploaded to PyPI!$(RESET)\n"

serve: install

	@printf "$(YELLOW)Starting development server…$(RESET)\n"
	@. $(VENV_DIR)/bin/activate && \
	gunicorn -c run_gunicorn.py app.main:app

docker-build:
	@printf "$(YELLOW)Building Docker image for the application with buildx...$(RESET)\n"
	docker buildx build --no-cache --progress=plain --load -f Containerfile -t scripture-assistant .

docker-compose-up:
	@printf "$(YELLOW)Starting Docker Compose services...$(RESET)\n"
	docker-compose up -d

docker-compose-logs:
	@printf "$(YELLOW)Fetching Docker Compose logs...$(RESET)\n"
	@docker-compose logs --follow

docker-compose-stop:
	@printf "$(YELLOW)Stopping Docker Compose services...$(RESET)\n"
	@docker-compose stop

docker-compose-down:
	@printf "$(YELLOW)Stopping and removing Docker Compose services...$(RESET)\n"
	@docker-compose down --volumes

docker-clean-images:
	@printf "$(YELLOW)Removing application Docker images and pruning dangling images...$(RESET)\n"
	docker rmi scripture-assistant 2>/dev/null || true
	docker image prune -f