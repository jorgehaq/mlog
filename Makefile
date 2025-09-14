SHELL := /bin/bash

.PHONY: \
  venv install run front-dev test-backend test-frontend e2e \
  local-db-up local-db-down \
  dev-up dev-down dev-logs dev-test-backend dev-test-frontend dev-e2e \
  staging-build staging-up staging-down staging-logs staging-e2e

# === Local ===
venv:
	python -m venv .venv; source .venv/bin/activate; python -m pip install -U pip

install:
	. .venv/bin/activate; pip install -r requirements.txt

run:
	. .venv/bin/activate; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

front-dev:
	cd frontend && npm ci && npm run dev

test-backend:
	. .venv/bin/activate; pytest -q tests/

test-frontend:
	cd frontend && npm test

e2e:
	cd frontend && npm run e2e

# Run Playwright E2E locally against a manually started preview server
e2e-local:
	cd frontend && npm ci && npm run build
	# start preview in background and wait for it
	cd frontend && (nohup sh -lc "npm run preview -- --port 4173 --host 0.0.0.0 > .preview.log 2>&1 & echo $$! > .preview.pid")
	# wait until preview responds
	set -e; for i in $$(seq 1 30); do \
	  if curl -sf http://localhost:4173 >/dev/null 2>&1; then break; fi; \
	  sleep 1; \
	done
	cd frontend && E2E_BASE_URL=http://localhost:4173 npx playwright test || (code=$$?; kill $$(cat .preview.pid) || true; exit $$code)
	cd frontend && kill $$(cat .preview.pid) || true

local-db-up:
	docker compose up -d mongo redis

local-db-down:
	docker compose stop mongo redis

# === Docker Dev (hot-reload) ===
dev-up:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.override.yml down -v

dev-logs:
	docker compose -f docker-compose.yml -f docker-compose.override.yml logs -f mlog-api

dev-test-backend:
	docker compose run --rm mlog-api bash -lc "pip install -q -r requirements-dev.txt && /home/appuser/.local/bin/pytest -q tests/"

dev-test-frontend:
	docker compose run --rm frontend npm test --silent

UID := $(shell id -u)
GID := $(shell id -g)

dev-e2e:
	docker run --rm -t \
	  -u $(UID):$(GID) \
	  --network host \
	  -v "$$PWD/frontend:/work" \
	  -v "$$PWD/.npm-cache:/root/.npm" \
	  -w /work \
	  mcr.microsoft.com/playwright:v1.55.0-jammy bash -lc "npm ci && npm run e2e"

  # Debug E2E: evita reinstalar deps; arranca preview si hace falta; modo no headless
dev-e2e-debug:
	docker run --rm -it \
	  -u $(UID):$(GID) \
	  -e DEBUG=pw:webserver \
	  -e PWDEBUG=1 \
	  -e PLAYWRIGHT_HEADLESS=0 \
	  -v "$$PWD/frontend:/work" \
	  -w /work \
	  mcr.microsoft.com/playwright:v1.55.0-jammy bash -c '\
	    if [ ! -d node_modules ]; then npm ci; fi; \
	    E2E_BASE_URL="$${E2E_BASE_URL:-http://localhost:4173}" npx playwright test --project=chromium --trace on'

dev-e2e-shell:
	docker run --rm -it -u $(UID):$(GID) -v "$$PWD/frontend:/work" -w /work mcr.microsoft.com/playwright:v1.55.0-jammy bash

# === Staging (pre-release) ===
staging-build:
	docker run --rm -t \
	  -u $(UID):$(GID) \
	  -v "$$PWD/frontend:/work" \
	  -v "$$PWD/.npm-cache:/tmp/.npm" \
	  -e npm_config_cache="/tmp/.npm" \
	  -w /work \
	  node:20-alpine sh -c "npm ci && npm run build"

staging-up:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d --build

staging-down:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml down -v

staging-logs:
	docker compose -f docker-compose.yml -f docker-compose.staging.yml logs -f mlog-api

staging-e2e:
	E2E_BASE_URL=http://localhost:8080 docker run --rm -t \
	  -u $(UID):$(GID) \
	  -v "$$PWD/frontend:/work" \
	  -v "$$PWD/.npm-cache:/tmp/.npm" \
	  -e npm_config_cache="/tmp/.npm" \
	  -w /work -p 4173:4173 \
	  mcr.microsoft.com/playwright:v1.55.0-jammy bash -lc "npm ci && npm run e2e"
