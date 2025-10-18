CREATE DATABASE parking_db;
CREATE USER parking_user WITH ENCRYPTED PASSWORD 'parkingbackend';
GRANT ALL PRIVILEGES ON DATABASE parking_db TO parking_user;

\c parking_db
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Grant privileges on public schema
GRANT ALL PRIVILEGES ON SCHEMA public TO parking_user;

-- Optional: allow creating tables by default
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO parking_user;
