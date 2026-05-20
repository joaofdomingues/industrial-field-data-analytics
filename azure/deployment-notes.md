# Azure Deployment Notes

This project is prepared for deployment in Microsoft Azure using a cloud-native architecture.

---

## Recommended Azure Architecture

Vue.js Frontend
       ↓
Azure Static Web Apps
       ↓
Django REST API
       ↓
Azure App Service
       ↓
Azure Database for PostgreSQL

---

## Recommended Azure Services

### Frontend
- Azure Static Web Apps

### Backend
- Azure App Service for Linux
- Python 3.12
- Gunicorn

### Database
- Azure Database for PostgreSQL Flexible Server

### CI/CD
- GitHub Actions

---

## Required Environment Variables

### Backend
- DJANGO_SECRET_KEY
- DATABASE_URL
- DJANGO_ALLOWED_HOSTS
- CORS_ALLOWED_ORIGINS
- CSRF_TRUSTED_ORIGINS

### Frontend
- VITE_API_URL

---

## Production Considerations

- HTTPS enabled
- PostgreSQL SSL enabled
- JWT authentication enabled
- Swagger/OpenAPI documentation available
- CI/CD pipeline validation enabled
- Docker-based backend deployment supported

---

## Future Azure Enhancements

- Azure Blob Storage for CSV uploads
- Azure Monitor
- Azure Application Insights
- Azure Container Registry
- Azure Databricks
- PySpark telemetry processing
- Predictive maintenance models