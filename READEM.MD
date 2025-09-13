{
  "project_name": "MLOG - MongoDB Event Logging & Analytics Service",
  "description": "Microservicio para registrar eventos de múltiples servicios con MongoDB y exponer analíticas en tiempo real. Sincronizable con BigQuery para análisis históricos.",
  "backend": {
    "framework": "FastAPI",
    "language": "Python 3.11+",
    "database": "MongoDB (Motor async driver)",
    "architecture": "Repository + Service Layer",
    "api_endpoints": [
      { "method": "POST", "path": "/events", "description": "Registrar un evento" },
      { "method": "GET", "path": "/events/{service}", "description": "Obtener eventos por servicio" },
      { "method": "GET", "path": "/analytics/summary", "description": "Resumen de métricas por servicio" },
      { "method": "GET", "path": "/analytics/timeline", "description": "Datos en series de tiempo" },
      { "method": "GET", "path": "/health", "description": "Chequeo de estado MongoDB" }
    ],
    "models": ["EventCreate", "EventResponse", "AnalyticsSummary"],
    "mongodb_collections": ["audit_logs", "user_actions", "system_events"],
    "aggregation_pipeline_example": {
      "match": { "service": "axi", "timestamp": { "$gte": "start_date" } },
      "group": { "_id": "$action", "count": { "$sum": 1 } },
      "sort": { "count": -1 }
    },
    "folders": [
      "app/api/v1", "app/models", "app/schemas", "app/services", "app/core", "tests", "scripts"
    ],
    "docker": {
      "services": ["fastapi_app", "mongodb"],
      "docker_compose": true,
      "env_variables": ["MONGO_URI", "ENV", "LOG_LEVEL"],
      "production": {
        "cloud_run": true,
        "mongodb_atlas": true,
        "secrets_handling": "Environment Variables / Secret Manager"
      }
    }
  },
  "frontend": {
    "framework": "React 18",
    "language": "TypeScript",
    "build_tool": "Vite",
    "styling": "Tailwind CSS",
    "data_fetching": "TanStack Query",
    "charting": "Chart.js",
    "pages": ["Dashboard", "Analytics", "Events"],
    "components": ["EventsTable", "MetricsCard", "TimelineChart", "ServiceFilter"],
    "structure": [
      "src/components/ui", "src/components/forms", "src/pages", "src/services", "src/hooks", "src/types", "src/utils"
    ]
  },
  "integration": {
    "event_sources": ["AXI", "MINT", "AIDE", "GRASP", "ECHO", "ADTECH"],
    "data_flow": "Services → POST /events → MongoDB → Analytics API → React Dashboard",
    "bigquery_sync": {
      "method": "Scheduled Cloud Function",
      "data_transformation": true,
      "destination": "BigQuery table per collection",
      "frequency": "Daily or hourly"
    }
  },
  "testing": {
    "unit_tests": true,
    "integration_tests": true,
    "load_tests": true,
    "tools": ["pytest", "httpx", "mongomock"]
  },
  "naming": {
    "preferred": "MLOG",
    "alternatives": ["DOCLOG", "AUDIT-M", "EVLOG"],
    "domain": "mlog.yourdomain.com",
    "repository": "mlog-service",
    "container": "mlog-api"
  }
}