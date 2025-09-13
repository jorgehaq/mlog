Contribución y flujo de ramas

Ramas principales
- `main`: rama estable, lista para producción.
- `dev`: integración de cambios en curso; base para features.

Ramas de trabajo
- `feature/<slug>`: nuevas funcionalidades.
- `fix/<slug>`: correcciones de bugs.
- `chore/<slug>`: tareas de mantenimiento.

Reglas
- Crear ramas desde `dev`.
- Abrir PR de `feature/*` → `dev`.
- Integrar `dev` → `main` con PR y tags de release cuando se haga un corte.

Convenciones de commits (sugerido)
- `feat: ...`, `fix: ...`, `chore: ...`, `docs: ...`, `refactor: ...`, `test: ...`.

Configuración local
- Asegúrate de configurar tu identidad Git:
  - `git config user.name "Tu Nombre"`
  - `git config user.email "tu@email"`

