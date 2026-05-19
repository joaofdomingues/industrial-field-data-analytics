# Industrial Field Data Analytics Platform

A full-stack industrial analytics platform built with Vue.js and Django REST Framework for monitoring and analyzing industrial field telemetry, load profiles, energy consumption, and reliability metrics.

---

# Live Demo

- Frontend: https://industrial-field-data-analytics.vercel.app
- Backend API: https://industrial-field-data-analytics.onrender.com
- GitHub Repository: https://github.com/joaofdomingues/industrial-field-data-analytics

---

# Overview

This platform simulates a modern industrial engineering analytics environment where field telemetry data is processed, analyzed, and visualized through an interactive dashboard.

The application focuses on:

- Load profile visualization
- Energy monitoring
- Reliability metrics
- Field telemetry analysis
- Anomaly detection
- Data processing workflows
- Engineering-focused dashboards

---

# Tech Stack

## Frontend
- Vue.js
- Vite
- ApexCharts
- JavaScript
- CSS

## Backend
- Python
- Django
- Django REST Framework
- Gunicorn
- WhiteNoise

## Data & Analytics
- Pandas
- ETL Processing
- Time-Series Analytics
- Reliability Metrics
- Anomaly Detection

## DevOps & Deployment
- Docker
- GitHub
- Render
- Vercel

---

# Features

## Industrial Dashboard
- Real-time KPI visualization
- Machine monitoring
- Energy analytics
- Load profile charts
- Reliability indicators

## Data Processing
- ETL pipeline
- CSV ingestion
- Data normalization
- Aggregated analytics

## Reliability Analytics
- Machine risk scoring
- Operational reliability metrics
- Alert generation
- Anomaly detection

## API Endpoints

- `/health/`
- `/engineering-summary/`
- `/load-profiles/`
- `/machines/`
- `/alerts/`

---

# Architecture

```text
Field Data CSV
       ↓
Python ETL Pipeline
       ↓
Django REST API
       ↓
SQLite / PostgreSQL-ready
       ↓
Vue.js Analytics Dashboard
       ↓
Render + Vercel Deployment
```

---

# Deployment

## Frontend

Deployed on Vercel:

https://industrial-field-data-analytics.vercel.app

## Backend

Deployed on Render:

https://industrial-field-data-analytics.onrender.com

---

# Local Development

## Backend

```bash
cd backend
python -m venv .venv

# Linux / WSL
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate
python manage.py import_machine_data --reset
python manage.py runserver
```

## Frontend

```bash
cd frontend

npm install
npm run dev
```

---

# Future Improvements

- JWT Authentication
- PostgreSQL Production Database
- Azure Deployment
- Azure Databricks Integration
- Predictive Maintenance Models
- Machine Learning Anomaly Detection
- Real-Time Streaming Data
- Advanced Engineering Analytics
- Automated Testing Pipeline

---

# Project Goal

The goal of this project is to demonstrate a modern data-driven full-stack architecture aligned with industrial engineering analytics environments.

The platform was designed to simulate how engineering teams can process and visualize field telemetry data to improve operational monitoring and decision-making.

---

# Author

João Domingues

GitHub:
https://github.com/joaofdomingues