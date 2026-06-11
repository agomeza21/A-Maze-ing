PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt
PACKAGE_DIR = mazegen/

install:
	pip install build flake8 mypy
	$(PYTHON) -m build

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__ $(PACKAGE_DIR)__pycache__ .mypy_cache dist build *.egg-info

lint:
	flake8 $(MAIN) $(PACKAGE_DIR)
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs $(MAIN) $(PACKAGE_DIR)

lint-strict:
	flake8 $(MAIN) $(PACKAGE_DIR)
	mypy --strict $(MAIN) $(PACKAGE_DIR)

.PHONY: install run debug clean lint lint-strict