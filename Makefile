SHELL := /bin/bash

.PHONY: venv install run front front-dev front-build front-preview test-backend test-frontend e2e

venv:
	python -m venv .venv; source .venv/bin/activate; python -m pip install -U pip

install:
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

front:
	cd frontend && python -m http.server 5173

front-dev:
	cd frontend && npm ci && npm run dev

front-build:
	cd frontend && npm ci && npm run build

front-preview:
	cd frontend && npm run preview

test-backend:
	. .venv/bin/activate; pytest -q tests/

test-frontend:
	cd frontend && npm test

e2e:
	cd frontend && npm run e2e
