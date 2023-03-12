PYTHON := python3.11
VENV := venv

.PHONY: check
check: check-coding-standards check-pytest

.PHONY: check-coding-standards
check-coding-standards: check-black check-pylint check-isort

.PHONY: check-tests
check-tests: check-pytest

.PHONY: check-black
check-black: $(VENV)
	$(VENV)/bin/python -m black \
	    --check \
	    --diff \
	    --color \
	    --safe \
	    src \
	    tests \
	;

.PHONY: check-pylint
check-pylint: $(VENV)
	$(VENV)/bin/python -m pylint \
	    src \
	    tests \
	;

.PHONY: check-isort
check-isort:
	$(VENV)/bin/python -m isort \
	    --check-only \
	    --diff \
	    src \
	    tests \
	;

.PHONY: check-pytest
check-pytest: $(VENV)
	$(VENV)/bin/python -m pytest .

venv: venv/bin/activate

venv/bin/activate: pyproject.toml
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install -e .[test]
	touch $@

.PHONY: clean
clean:
	rm -rf $(VENV)
