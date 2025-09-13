SHELL := /bin/bash

.PHONY: venv install run front

venv:
	python -m venv .venv; source .venv/bin/activate; python -m pip install -U pip

install:
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

front:
	cd frontend && python -m http.server 5173
