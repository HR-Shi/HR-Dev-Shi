# HR Dashboard Deployment Guide

## Overview
This guide covers deploying the HR Dashboard with:
- **Backend**: FastAPI on Render (Docker)
- **Frontend**: React/Vite on Vercel
- **Database**: Supabase PostgreSQL

## 🚀 Backend Deployment (Render)

### 1. Environment Variables to Set in Render Dashboard

In your Render service settings, add these environment variables:

```bash
# Database
SUPABASE_DATABASE_URL=postgresql://postgres.udaulvygaczcsrgybdqw:6wjSo5aCUjkCLMHZ@aws-0-ap-south-1.pooler.supabase.com:6543/postgres
SUPABASE_URL=https://udaulvygaczcsrgybdqw.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkYXVsdnlnYWN6Y3NyZ3liZHF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4MzMyOTMsImV4cCI6MjA2NTQwOTI5M30.a9_SJERhQL_UAMWmvSrBdrZbDgFnPHaRpLWoOD-P33o
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkYXVsdnlnYWN6Y3NyZ3liZHF3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgzMzI5MywiZXhwIjoyMDY1NDA5MjkzfQ.7mRyHdf6WSa7XGO6pxRU0gsJiMSvWXUfQyUI7xnhAfw

# Application
ENVIRONMENT=production
SECRET_KEY=uEHzXpsFzB-fFA4YDjLBf09W9QHVD__jby8W42eI9UI
FRONTEND_URL=https://hr-dev-shi.vercel.app
BACKEND_URL=https://hr-dev-shi.onrender.com

# AI Service
CEREBRAS_API_KEY=csk-yfykk3992ntf239vynnktnyftt5ppnyp4pcrrp3cdcr6rcpd
```

### 2. Render Configuration

Based on your screenshots, configure:

- **Language**: Docker
- **Branch**: main
- **Region**: Oregon (US West)
- **Root Directory**: `backend`
- **Dockerfile Path**: `./Dockerfile`
- **Build Filters**: 
  - Included Paths: `backend/**`
  - Ignored Paths: `src/**`, `*.md`

### 3. Your Backend URL will be:
```
https://hr-dev-shi.onrender.com
```

---

## 🌐 Frontend Deployment (Vercel)

### 1. Environment Variables to Set in Vercel Dashboard

In your Vercel project settings → Environment Variables:

```bash
VITE_BACKEND_URL=https://hr-dev-shi.onrender.com/api/v1
VITE_SUPABASE_URL=https://udaulvygaczcsrgybdqw.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkYXVsdnlnYWN6Y3NyZ3liZHF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4MzMyOTMsImV4cCI6MjA2NTQwOTI5M30.a9_SJERhQL_UAMWmvSrBdrZbDgFnPHaRpLWoOD-P33o
```

### 2. Vercel Configuration

- **Framework Preset**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 3. Update Backend CORS

Once you know your Vercel URL (e.g., `https://hr-dev-shi.vercel.app`), update the `FRONTEND_URL` environment variable in Render to match it.

---

## 📝 Configuration Files Updated

### `backend/config.py`
- Centralized all settings with your actual values as defaults
- Environment variables override these defaults in production

### `backend/Dockerfile`
- Docker configuration for Render deployment
- Installs dependencies and runs uvicorn

### `render.yaml`
- Infrastructure as code for Render
- Defines Docker service with environment variables

### `vercel.json`
- Vercel configuration for SPA routing
- Removed hardcoded env vars (use Vercel dashboard instead)

---

## 🔧 Local Development

Your local development continues to work unchanged:

```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend  
npm run dev
```

---

## 🚨 Important Notes

1. **Update Frontend URL**: After Vercel deployment, update `FRONTEND_URL` in Render to your actual Vercel URL
2. **Database Schema**: Ensure your Supabase database has the required tables (run migrations if needed)
3. **API Keys**: All sensitive keys are now in the config.py but should be overridden via environment variables in production
4. **Health Check**: Both services include health check endpoints at `/health`

---

## 🔍 Troubleshooting

### Backend Issues
- Check Render logs for Python/Docker errors
- Verify database connection in Render logs
- Ensure all environment variables are set

### Frontend Issues
- Check Vercel build logs
- Verify `VITE_BACKEND_URL` points to your Render service
- Check browser console for CORS errors

### CORS Issues
- Ensure `FRONTEND_URL` in Render matches your Vercel domain exactly
- Check that both HTTP and HTTPS are handled properly

---

## 📋 Deployment Checklist

- [ ] Push code to GitHub
- [ ] Create Render web service
- [ ] Set all Render environment variables
- [ ] Deploy backend and verify health endpoint
- [ ] Create Vercel project
- [ ] Set Vercel environment variables
- [ ] Deploy frontend
- [ ] Update Render `FRONTEND_URL` with actual Vercel URL
- [ ] Test full application flow
- [ ] Verify database connectivity
- [ ] Test API endpoints
- [ ] Check authentication flow 