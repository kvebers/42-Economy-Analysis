ifeq ($(OS),Windows_NT)
    PYTHON = venv/Scripts/python.exe
    PIP = venv/Scripts/pip.exe
    RUN_TARGET = run_windows
else
    PYTHON = venv/bin/python3
    PIP = venv/bin/pip
    RUN_TARGET = run_unix
endif

all: setup run

setup:
	python -m venv venv
	$(PIP) install -r requirements.txt

generate_readme_unix:
	$(PYTHON) create_analysis_and_documentation.py

pull_data_unix:
	$(PYTHON) pull_data.py

run_unix: pull_data_unix generate_readme_unix

generate_readme_windows:
	$(PYTHON) create_analysis_and_documentation.py

pull_data_windows:
	$(PYTHON) pull_data.py

run_windows: pull_data_windows generate_readme_windows

run: $(RUN_TARGET)
