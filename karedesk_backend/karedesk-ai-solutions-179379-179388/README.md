# karedesk-ai-solutions-179379-179388

This repository contains the Karedesk multi-container application.

Containers:
- Backend (Flask): karedesk-ai-solutions-179379-179388/karedesk_backend
- Frontend (React): karedesk-ai-solutions-179379-179389/karedesk_frontend

Backend quick start:
1) Create and configure environment (see .env.example)
   cd karedesk-ai-solutions-179379-179388/karedesk_backend
   cp .env.example .env  # then edit values as needed

2) Run the backend:
   python run.py

3) API docs (Swagger UI powered by flask-smorest):
   http://localhost:5000/docs

4) Regenerate OpenAPI after changing routes:
   cd karedesk-ai-solutions-179379-179388/karedesk_backend
   python generate_openapi.py
   # The spec is written to karedesk_backend/interfaces/openapi.json

Key environment variables (see .env.example):
- API_TITLE, API_VERSION: API metadata for docs
- CORS_ORIGINS: Allowed CORS origins (default http://localhost:3000)
- DATABASE_URL, DB_POOL_SIZE, DB_ECHO: Database connection and behavior
