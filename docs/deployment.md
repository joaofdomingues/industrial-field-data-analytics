# Deployment Guide: GitHub + Azure Basic

This project is prepared for a realistic interview-grade deployment:

- Backend: Django REST API deployed as an Azure App Service container.
- Database: Azure Database for PostgreSQL Flexible Server.
- Frontend: Vue dashboard deployed to Azure Static Web Apps.
- CI/CD: GitHub Actions for tests, build and Azure deployment.

## 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial interview-ready field data analytics platform"
git branch -M main
git remote add origin https://github.com/<your-user>/industrial-field-data-analytics.git
git push -u origin main
```

## 2. Create Azure resources

Install and login:

```bash
az login
az group create --name rg-industrial-field-data --location westeurope
```

Create PostgreSQL:

```bash
az postgres flexible-server create \
  --resource-group rg-industrial-field-data \
  --name pg-industrial-field-data-<unique> \
  --location westeurope \
  --admin-user industrialadmin \
  --admin-password "ChangeThisPassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16
```

Create container registry:

```bash
az acr create \
  --resource-group rg-industrial-field-data \
  --name acrindustrialfielddata<unique> \
  --sku Basic
```

Create Linux App Service for the backend container:

```bash
az appservice plan create \
  --resource-group rg-industrial-field-data \
  --name asp-industrial-field-data \
  --is-linux \
  --sku B1

az webapp create \
  --resource-group rg-industrial-field-data \
  --plan asp-industrial-field-data \
  --name app-industrial-field-data-api-<unique> \
  --deployment-container-image-name nginx
```

Create Static Web App for frontend using the Azure Portal, then copy the deployment token into GitHub secrets.

## 3. Required GitHub secrets

Backend workflow secrets:

- `ACR_LOGIN_SERVER`
- `ACR_USERNAME`
- `ACR_PASSWORD`
- `AZURE_WEBAPP_NAME`
- `AZURE_WEBAPP_PUBLISH_PROFILE`

Frontend workflow secrets:

- `AZURE_STATIC_WEB_APPS_API_TOKEN`
- `VITE_API_URL` e.g. `https://app-industrial-field-data-api-<unique>.azurewebsites.net`

## 4. Backend App Service environment variables

Set these in Azure App Service > Configuration:

```env
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<strong-secret>
DJANGO_ALLOWED_HOSTS=app-industrial-field-data-api-<unique>.azurewebsites.net
CORS_ALLOWED_ORIGINS=https://<your-static-web-app>.azurestaticapps.net
CSRF_TRUSTED_ORIGINS=https://<your-static-web-app>.azurestaticapps.net
DB_ENGINE=postgres
POSTGRES_DB=postgres
POSTGRES_USER=industrialadmin
POSTGRES_PASSWORD=<your-password>
POSTGRES_HOST=pg-industrial-field-data-<unique>.postgres.database.azure.com
POSTGRES_PORT=5432
DB_SSL_REQUIRE=1
```

## 5. Validation URLs

Backend:

```text
https://<backend-app>.azurewebsites.net/health/
https://<backend-app>.azurewebsites.net/engineering-summary/
https://<backend-app>.azurewebsites.net/load-profiles/
```

Frontend:

```text
https://<static-web-app>.azurestaticapps.net
```

## 6. Interview explanation

Use this wording:

> I prepared a real deployment path using GitHub Actions, Azure App Service for the Django API, Azure Database for PostgreSQL, and Azure Static Web Apps for the Vue frontend. The local version runs with Docker Compose, while the Azure version separates frontend, API and database in a production-like architecture.

Be precise: this is an Azure-ready deployment configuration. Only call it a live deployment after you actually run these commands in your Azure subscription.
