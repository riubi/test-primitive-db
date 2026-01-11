install:
	python3 -m poetry install

project:
	python3 -m poetry run project

build:
	python3 -m poetry build

publish:
	python3 -m poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	python3 -m poetry run ruff check .
