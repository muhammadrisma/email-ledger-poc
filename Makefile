# Email Ledger POC - Simple Makefile

.PHONY: help install build test run api clean

help:
	@echo "Email Ledger POC - Makefile Commands"
	@echo "======================================="
	@echo "make install   # Install dependencies and package"
	@echo "make build     # Build the package"
	@echo "make test      # Run tests"
	@echo "make run       # Run the email processor once"
	@echo "make api       # Start the API server"
	@echo "make migrate   # Run database migrations"
	@echo "make clean     # Clean build artifacts"

install:
	python install.py

build:
	python build.py

test:
	python scripts/test_package.py

run:
	python -m src.cli.main process

api:
	python -m src.app.api.app

migrate:
	python -c "import sys; sys.path.insert(0, '.'); from src.app.db.migrate import migrate_database; migrate_database()"

clean:
	rm -rf build/ dist/ *.egg-info/ __pycache__/ .pytest_cache/
	find . -type d -name __pycache__ -delete 