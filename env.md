# Environment Configuration Guide for HR Dashboard

This document explains how to set up the required environment variables for the HR Dashboard backend to work with Supabase database.

## Required .env File Structure

Create a `.env` file in the `backend/` directory with the following structure:

```env
# Development Environment
ENVIRONMENT=development

# Supabase Database Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres

# Alternative Database URL format (use one of the above)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.your-project-id.supabase.co:5432/postgres

# Security Configuration
SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random
SQL_DEBUG=false

# Frontend Configuration
FRONTEND_URL=http://localhost:3000

# AI Service Configuration (Cerebras)
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

## How to Get Supabase Credentials

### Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in to your account
3. Click "New Project"
4. Choose your organization
5. Fill in project details:
   - **Name**: HR Dashboard (or your preferred name)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to your location
6. Click "Create new project"

### Step 2: Get Your Project Credentials

Once your project is created:

1. **Go to Project Settings**:
   - Click on the gear icon (⚙️) in the left sidebar
   - Or go to Settings → General

2. **Get SUPABASE_URL**:
   - In the "General" tab, find "Reference ID"
   - Your URL format: `https://[your-reference-id].supabase.co`
   - Copy this URL

3. **Get API Keys**:
   - Go to Settings → API
   - Copy the **anon/public** key for `SUPABASE_ANON_KEY`
   - Copy the **service_role** key for `SUPABASE_SERVICE_ROLE_KEY`
   - ⚠️ **Keep service_role key secret!** Never expose it in frontend code

4. **Get Database URL**:
   - Go to Settings → Database
   - Scroll to "Connection info"
   - Copy the connection string or build it using:
     ```
     postgresql://postgres:[YOUR-PASSWORD]@db.[your-reference-id].supabase.co:5432/postgres
     ```
   - Replace `[YOUR-PASSWORD]` with the password you created in Step 1
   - Replace `[your-reference-id]` with your actual project reference ID

### Step 3: Generate SECRET_KEY

For the JWT secret key, generate a secure random string:

**Option 1 - Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**Option 2 - OpenSSL:**
```bash
openssl rand -base64 32
```

**Option 3 - Online Generator:**
Use a secure password generator to create a 32+ character random string.

### Step 4: Get Cerebras API Key

For AI-powered features (action plan recommendations, outlier detection, survey generation):

1. **Go to Cerebras Cloud**:
   - Visit [https://cloud.cerebras.ai](https://cloud.cerebras.ai)
   - Sign up or log in to your account

2. **Create API Key**:
   - Navigate to API Keys section
   - Click "Create API Key"
   - Give it a descriptive name (e.g., "HR Dashboard")
   - Copy the generated API key

3. **Add to .env file**:
   ```env
   CEREBRAS_API_KEY=your_actual_api_key_here
   ```

**Note**: The AI service will provide fallback responses if no API key is provided, but AI-powered features will be limited.

### Step 5: Set Up Database Tables

After setting up your `.env` file, the application will automatically create the required database tables when you start the server for the first time.

## Example .env File (with placeholder values)

```env
# Development Environment
ENVIRONMENT=development

# Supabase Configuration
SUPABASE_URL=https://abcd1234efgh5678.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2QxMjM0ZWZnaDU2NzgiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYyMzg0NjIwNCwiZXhwIjoxOTM5NDIyMjA0fQ.example-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2QxMjM0ZWZnaDU2NzgiLCJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjIzODQ2MjA0LCJleHAiOjE5Mzk0MjIyMDR9.example-service-role-key-here
SUPABASE_DATABASE_URL=postgresql://postgres:your_password_here@db.abcd1234efgh5678.supabase.co:5432/postgres

# Security
SECRET_KEY=your-super-secret-jwt-key-here-make-it-long-and-random-32-plus-characters
SQL_DEBUG=false

# Frontend
FRONTEND_URL=http://localhost:3000

# AI Service (Cerebras)
CEREBRAS_API_KEY=your_cerebras_api_key_here
```

## Troubleshooting

### Common Issues:

1. **"Connection refused" error**:
   - Check if your database URL is correct
   - Verify your database password
   - Ensure your Supabase project is active

2. **"Invalid JWT" errors**:
   - Verify your SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY
   - Check that keys haven't been regenerated in Supabase dashboard

3. **"Access denied" errors**:
   - Check your Row Level Security (RLS) policies in Supabase
   - For development, you might want to temporarily disable RLS

### Verification Steps:

1. **Test Database Connection**:
   ```bash
   cd backend
   python -c "from database import test_db_connection; print('Success!' if test_db_connection() else 'Failed!')"
   ```

2. **Test Server Startup**:
   ```bash
   cd backend
   python main.py
   ```

3. **Test Health Endpoint**:
   ```bash
   curl http://localhost:8000/health
   ```

## Security Notes

- ⚠️ **Never commit your `.env` file to version control**
- 🔐 **Keep your service_role key secret**
- 🛡️ **Use strong, unique passwords**
- 🔄 **Rotate keys periodically in production**

## Production Deployment

For production deployment, set these environment variables in your hosting platform (Heroku, Railway, Vercel, etc.) instead of using a `.env` file.

---

Once you've set up your `.env` file with the correct Supabase credentials, the HR Dashboard backend should connect successfully to your Supabase database! 