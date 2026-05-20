---

## Azure Deployment Steps

### 1. Create Resource Group

Create a dedicated Azure Resource Group for the project.

Recommended name:

```text
rg-industrial-field-data
```

---

### 2. Deploy PostgreSQL

Create an Azure Database for PostgreSQL Flexible Server.

Recommended database name:

```text
industrial_field_data_db
```

After creation, configure the backend `DATABASE_URL` environment variable with the Azure PostgreSQL connection string.

---

### 3. Deploy Backend API

Deploy the Django REST API using Azure App Service for Linux.

Recommended configuration:

```text
Runtime: Python 3.12
Startup command: sh startup.sh
Root directory: backend
```

Required environment variables:

```text
DJANGO_SECRET_KEY
DJANGO_ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
CSRF_TRUSTED_ORIGINS
DATABASE_URL
```

---

### 4. Deploy Frontend

Deploy the Vue.js frontend using Azure Static Web Apps.

Recommended configuration:

```text
App location: frontend
Output location: dist
Build command: npm run build
```

Required frontend environment variable:

```text
VITE_API_URL=https://<azure-backend-app-name>.azurewebsites.net
```

---

### 5. Validate Deployment

After deployment, validate:

```text
/frontend
/api/docs/
/health/
/engineering-summary/
/upload-csv/
/api/token/
```

---

## Azure Environment Example

### Backend

```env
DJANGO_SECRET_KEY=change-me
DJANGO_ALLOWED_HOSTS=<azure-backend-app-name>.azurewebsites.net
CORS_ALLOWED_ORIGINS=https://<azure-static-web-app-url>
CSRF_TRUSTED_ORIGINS=https://<azure-static-web-app-url>
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Frontend

```env
VITE_API_URL=https://<azure-backend-app-name>.azurewebsites.net
```

---

## Interview Explanation

This project is currently deployed using Render and Vercel for fast public demonstration, but the architecture is designed to be portable to Azure using:

- Azure Static Web Apps for the Vue.js frontend
- Azure App Service for the Django REST API
- Azure Database for PostgreSQL for persistent telemetry storage
- GitHub Actions for CI/CD validation
- Future Azure Databricks integration for scalable PySpark processing