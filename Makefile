.PHONY: install test clean format lint help

help:
	@echo "Available commands:"
	@echo "  make install     - Install the package and dependencies using Poetry"
	@echo "  make install-dev - Install development dependencies using Poetry"
	@echo "  make test        - Run tests with coverage"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Run linting checks"
	@echo "  make clean       - Clean build artifacts"
	@echo "  make examples    - Run example scripts"
	@echo "  make build       - Build distribution packages with Poetry"
	@echo "  make shell       - Enter Poetry virtual environment shell"

install:
	poetry install --only main

install-dev:
	poetry install

test:
	poetry run pytest -v --cov=lmdb_sortedset --cov-report=term-missing --cov-report=html

format:
	poetry run black lmdb_sortedset/ tests/ examples/

lint:
	poetry run flake8 lmdb_sortedset/ tests/ examples/
	poetry run mypy lmdb_sortedset/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf data/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

examples:
	poetry run python examples/basic_usage.py

build: clean
	poetry build

publish-test:
	poetry publish --repository testpypi

publish:
	poetry publish

shell:
	poetry shell

lock:
	poetry lock

update:
	poetry update


