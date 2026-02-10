<<<<<<< HEAD
# utm_receiver
=======
# UTM Receiver

A minimal FastAPI service that logs UTM parameters to a PostgreSQL database.

## What it does
- Captures UTM parameters from HTTP requests
- Stores click data including IP, user agent, and referrer
- Provides a simple web interface to confirm tracking

## Local Development
1. Set DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn server.src.main:app --reload
   ```

4. Visit `http://localhost:8000/track?utm_source=test&utm_medium=email` to test

## Deployment
This service is compatible with Render.com and similar platforms.

Start with:
```bash
uvicorn server.src.main:app
```
>>>>>>> ad8f87a (UTM Receiver MVP - logging + frontend)
