.PHONY: bootstrap check lint format test

bootstrap:
	./scripts/bootstrap.sh

check: lint
	uv run mypy .

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

test:
	uv run python -m unittest discover -s test -t .