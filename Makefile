.PHONY: install run project build package-install lint publish

install:
	uv sync

run:
	uv run database

project:
	uv run database

build:
	uv build

package-install:
	uv pip install --reinstall dist/*.whl

lint:
	uv run ruff check .

publish:
	uv publish --dry-run