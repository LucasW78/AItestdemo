-- Database initialization script for AItestdemo
-- This script creates the initial database schema and sets up necessary extensions

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types if needed
CREATE TYPE IF NOT EXISTS processing_status AS ENUM (
    'uploaded',
    'processing',
    'completed',
    'failed'
);

CREATE TYPE IF NOT EXISTS test_case_status AS ENUM (
    'draft',
    'approved',
    'deprecated'
);

CREATE TYPE IF NOT EXISTS test_case_priority AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE IF NOT EXISTS mind_map_status AS ENUM (
    'active',
    'archived'
);

-- Create indexes for better performance
-- These will be created after tables are created by SQLAlchemy

-- You can add initial data here if needed
-- For example:
-- INSERT INTO users (id, username, email, created_at)
-- VALUES (uuid_generate_v4(), 'admin', 'admin@aitestdemo.com', NOW());

-- Set timezone
SET timezone = 'UTC';

-- Create search configuration for full-text search
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS chinese (COPY = simple);
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS english (COPY = simple);

COMMIT;