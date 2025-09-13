# MLOG - MongoDB Event Logging & Analytics Service

Sistema desacoplado para registrar eventos de múltiples servicios, generar analíticas, y sincronizar con BigQuery.

## 🧱 Estructura
- Backend: FastAPI + MongoDB (Motor)
- Frontend: React 18 + Vite + TypeScript
- Infraestructura: Docker / GCP Cloud Run + MongoDB Atlas

## 🚀 Instalación local

### Backend
```bash
git clone https://github.com/jorgehaq/mlog
cd mlog
cp .env.example .env.local
# Edita valores si deseas

# Levanta servicios
docker-compose up --build
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.development
npm run dev
```

## 🌐 API Endpoints (ejemplos)
- POST `/events`
- GET `/analytics/summary`
- GET `/analytics/timeline`

### Autenticación
- API Keys: enviar `X-API-Key: <key>` si `API_KEYS` está configurado
- JWT (opcional): enviar `Authorization: Bearer <token>` si `JWT_SECRET` está configurado
- Endpoints protegidos: `/events/*`, `/analytics/*`

### CORS
- Configura dominios permitidos en `CORS_ORIGINS`. Evita `*` en producción.

### Rate limiting
- Límite por IP: `RATE_LIMIT_PER_MIN` (por defecto 60/min). Respuesta 429 al excederlo.

## 🧪 Tests
```bash
pytest tests/
```

## ☁️ Despliegue en GCP (Cloud Run)

### 1. MongoDB Atlas
- Crea un cluster en https://cloud.mongodb.com
- Configura IP whitelist y user/password

### 2. Docker Build & Push
```bash
docker build -t gcr.io/tu-proyecto/mlog-api .
docker push gcr.io/tu-proyecto/mlog-api
```

### 3. Cloud Run Deploy
```bash
gcloud run deploy mlog-api \
  --image gcr.io/tu-proyecto/mlog-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENV=prod,MONGO_URI=<uri_atlas>
```

## 🔁 Sync MongoDB → BigQuery
- Crea una Cloud Function que exporte datos periódicamente
- Usa el SDK de Mongo + BigQuery para mover datos

## ✅ Recomendaciones
- Usa Secret Manager para MONGO_URI en producción
- Usa TanStack Query y Cache en frontend para eficiencia

---

ML0G es un microservicio de observabilidad y análisis reutilizable para ecosistemas multi-servicio.

## 🛠️ DevOps
- Docker multi-stage y usuario no-root en `Dockerfile`.
- Kubernetes manifests de ejemplo con probes en `k8s/deployment.yaml`.
- Secrets mediante env vars y soporte `*_FILE` para inyectar desde volúmenes/secretos.
- Prometheus scraping: `/metrics` y ejemplo en `monitoring/prometheus.yml`.
