install: install-deps install-deps-dev ## install dependencies
install-deps: ## install dependencies
	pip install -r requirements.txt

install-deps-dev: ## install dependencies for development
	pip install -r requirements-dev.txt


check: check-format
check-format: check-black check-isort
check-lint:
	@echo "-------- Checking style with flake8 --------"
	flake8 --show-source .
check-black:
	@echo "-------- Checking code with black --------"
	black --check .
check-isort:
	@echo "-------- Sorting imports with isort --------"
	isort --check-only --diff . --profile black


format: format-black format-isort ## format code with black and isort
format-black:
	@echo "-------- Formatting code with black --------"
	black .
format-isort:
	@echo "-------- Sorting imports with isort --------"
	isort . --profile black


install-playwright:
	playwright install --with-deps chromium
test: ## test deployments are working
	pytest --numprocesses auto .
