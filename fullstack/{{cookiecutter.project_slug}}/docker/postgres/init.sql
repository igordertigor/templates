-- Initialize databases for shared PostgreSQL instance
-- This script runs only when the database is first created

-- Create the Authentik database
-- The main application database ({{ cookiecutter.project_slug }}) is created automatically by POSTGRES_DB
CREATE DATABASE authentik OWNER postgres;
