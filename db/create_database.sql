-- Database: ticket_analyze_db

-- DROP DATABASE IF EXISTS ticket_analyze_db;

CREATE DATABASE ticket_analyze_db
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_India.1252'
    LC_CTYPE = 'English_India.1252'
    LOCALE_PROVIDER = 'libc'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    IS_TEMPLATE = False;

-- Create tables
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE analysis_runs (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT
);

CREATE TABLE ticket_analysis (
    id SERIAL PRIMARY KEY,
    analysis_run_id INT REFERENCES analysis_runs(id),
    ticket_id INT REFERENCES tickets(id),
    category TEXT,
    priority TEXT,
    notes TEXT
);
