PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

install:
	pip install build flake8 mypy
	python3 -m build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ mazegen/__pycache__ .mypy_cache dist build *.egg-info

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(MAIN) mazegen/

lint-strict:
	flake8 .
	mypy --strict $(MAIN) mazegen/

.PHONY: install run debug clean lint lint-strict