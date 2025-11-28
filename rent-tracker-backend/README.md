# Rent Tracker — Backend (FastAPI)

This backend is a ready-to-deploy FastAPI app designed to work with a PostgreSQL database (Supabase recommended).

## Quick non-coder deploy (Supabase + Render)

1. Create a Supabase project (https://supabase.com) and note the Postgres connection string.
2. Create a new GitHub repo named `rent-tracker-backend` and upload these files (extract the zip).
3. In Render.com, create a new Web Service and connect your repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 10000`
4. Add environment variables in Render:
   - `DATABASE_URL` set to your Supabase Postgres URL
   - `SECRET_KEY` (random string)
   - `ALGORITHM` = `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` = `1440`
5. In Supabase SQL editor run the schema SQL file (schema.sql) included in this repo.
6. Deploy. Render will give an API URL — copy it and set it into the frontend deploy step.

If you get stuck, paste Render build logs & Supabase SQL errors and I will help.
