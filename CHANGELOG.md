# Changelog

All notable changes to this project will be documented in this file.

## [v0.8.0] - 2025-09-14

- Added: Frontend EventForm para crear eventos (`frontend/src/components/EventForm.tsx`).
- Added: Dashboard con gráficos (Bar y Line) usando Chart.js (`frontend/src/components/Dashboard.tsx`).
- Added: Pruebas E2E con Playwright (`frontend/playwright.config.ts`, `frontend/e2e/basic.spec.ts`).
- Added: Targets de Makefile para frontend y tests (`front-dev`, `front-build`, `front-preview`, `test-backend`, `test-frontend`, `e2e`).
- Changed: Analytics usan una capa de repositorio (`app/repositories/audit_logs.py`), refactor en `app/api/v1/analytics.py`).
- Docs: README con ejemplos curl y variables de entorno.
- Housekeeping: Eliminación completa de `instructions.json` y `.mailmap` del historial y añadido a `.gitignore`.
- Branches: Limpieza de ramas de backup y sincronización `main` = `dev`.

[v0.8.0]: https://github.com/jorgehaq/mlog/releases/tag/v0.8.0
