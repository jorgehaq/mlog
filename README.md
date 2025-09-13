Proyecto: mlog

Este repo incluye un backend en Python (FastAPI) y un frontend estático simple para probar la API.

Se empieza por el backend y luego el frontend.

Requisitos
- Python 3.10+
- Opcional: Make (para usar atajos), pero puedes ejecutar comandos equivalentes en bash/PowerShell

Backend (FastAPI)
1) Crear entorno virtual
   - Linux/Mac: `python -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `python -m venv .venv; . .venv/Scripts/Activate.ps1`

2) Instalar dependencias
   - `pip install -U pip
      && pip install -r requirements.txt`

3) Variables de entorno
   - Copia `.env.example` a `.env` si deseas cambiar valores (opcional).

4) Ejecutar el servidor
   - `uvicorn app.main:app --reload --port 8000`
   - Endpoints:
     - `GET http://localhost:8000/` -> mensaje de bienvenida
     - `GET http://localhost:8000/health` -> estado del API y MongoDB
     - `POST http://localhost:8000/events` -> crear evento `{ service, action, payload?, timestamp? }`
     - `GET http://localhost:8000/events/{service}` -> listar eventos por servicio
     - `GET http://localhost:8000/analytics/summary` -> conteo por acción y total
     - `GET http://localhost:8000/analytics/timeline` -> puntos por minuto

Frontend (estático)
1) Servir el frontend de forma simple sin dependencias:
   - `cd frontend`
   - `python -m http.server 5173` (o el puerto que prefieras)
   - Abre `http://localhost:5173` en tu navegador

2) El frontend realiza peticiones al backend en `http://localhost:8000`.

Comandos Make (opcionales)
- `make venv`      -> crea y activa entorno virtual (en shells POSIX)
- `make install`   -> instala dependencias
- `make run`       -> ejecuta backend en http://localhost:8000
- `make front`     -> sirve frontend en http://localhost:5173

Estructura
- `app/`           -> código del backend FastAPI
- `frontend/`      -> HTML/JS estático de ejemplo
- `requirements.txt` -> dependencias del backend
- `.env.example`   -> variables de entorno de ejemplo

Git y flujo de ramas
- Ramas: `main` (producción), `dev` (integración), `feature/<slug>`.
- Crear features desde `dev` y abrir PR hacia `dev`.
- Promocionar `dev` a `main` con PR cuando corresponda una release.
- Comandos iniciales sugeridos:
  - `git checkout -b dev` (si no existe)
  - `git checkout -b feature/<slug>`
  - `git push -u origin <rama>` (si ya configuraste remoto)
