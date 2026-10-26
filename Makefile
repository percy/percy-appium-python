VENV=.venv/bin
REQUIREMENTS=$(wildcard requirements.txt development.txt)
MARKER=.initialized-with-makefile
VENVDEPS=$(REQUIREMENTS setup.py)

$(VENV):
	python -m venv .venv
	$(VENV)/python -m pip install --upgrade pip setuptools wheel

$(VENV)/$(MARKER): $(VENVDEPS) | $(VENV)
	$(VENV)/pip install $(foreach path,$(REQUIREMENTS),-r $(path))
	touch $(VENV)/$(MARKER)

.PHONY: venv lint test clean build release

venv: $(VENV)/$(MARKER)

lint: venv
	$(VENV)/pylint percy/* tests/*

test: venv
	$(VENV)/python -m unittest discover

clean:
	rm -rf $$(cat .gitignore)

build: venv
	$(VENV)/python setup.py sdist bdist_wheel

release: build
	TWINE_USERNAME=__token__ TWINE_PASSWORD="$$PYPI_TOKEN" $(VENV)/twine upload dist/*

coverage: venv
	$(VENV)/coverage run -m unittest discover
	$(VENV)/coverage report
