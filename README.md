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
