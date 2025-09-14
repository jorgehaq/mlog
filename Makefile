SHELL := /bin/bash

.PHONY: venv install run front front-dev front-build front-preview test-backend test-frontend e2e compose-up compose-up-dev compose-down compose-logs compose-test-backend compose-test-frontend compose-e2e

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

# --- Docker/Compose helpers ---
compose-up:
	docker compose -f docker-compose.yml up -d --build

compose-up-dev:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

compose-down:
	docker compose -f docker-compose.yml -f docker-compose.override.yml down -v

compose-logs:
	docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f mlog-api

# Run backend tests inside the mlog-api service container
compose-test-backend:
	docker compose run --rm mlog-api bash -lc "pip install -q -r requirements-dev.txt && pytest -q tests/"

# Run frontend unit tests inside the frontend container
compose-test-frontend:
	docker compose run --rm frontend npm test --silent

# Run Playwright E2E in container using official image
compose-e2e:
	docker run --rm -t -v "$$PWD/frontend:/work" -w /work -p 4173:4173 mcr.microsoft.com/playwright:v1.47.2-jammy bash -lc "npm ci && npx playwright install --with-deps && npm run e2e"
