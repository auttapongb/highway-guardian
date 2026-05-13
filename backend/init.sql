-- HWAY GUARDIAN — PostgreSQL + PostGIS Schema
-- Run automatically on first container start

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- AI-detected incidents from edge devices
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    severity VARCHAR(20) DEFAULT 'medium',
    source VARCHAR(20) DEFAULT 'ai_edge',
    vehicle_id VARCHAR(50),
    highway_id VARCHAR(20),
    kilometer FLOAT,
    position GEOMETRY(Point, 4326),
    image_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Citizen reports from LINE OA
CREATE TABLE IF NOT EXISTS citizen_reports (
    id SERIAL PRIMARY KEY,
    issue_type VARCHAR(50) NOT NULL,
    description TEXT,
    position GEOMETRY(Point, 4326),
    photo_url TEXT,
    line_user_id VARCHAR(100),
    highway_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'received',
    ai_confidence FLOAT,
    ai_classification VARCHAR(50),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LINE OA subscribers
CREATE TABLE IF NOT EXISTS line_subscribers (
    line_user_id VARCHAR(100) PRIMARY KEY,
    display_name VARCHAR(200),
    subscribed_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    geo_fence_km FLOAT DEFAULT 5.0
);

-- Indexes for geo-queries
CREATE INDEX IF NOT EXISTS idx_incidents_position ON incidents USING GIST (position);
CREATE INDEX IF NOT EXISTS idx_incidents_type ON incidents (type);
CREATE INDEX IF NOT EXISTS idx_incidents_created ON incidents (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_position ON citizen_reports USING GIST (position);
CREATE INDEX IF NOT EXISTS idx_reports_status ON citizen_reports (status);
CREATE INDEX IF NOT EXISTS idx_reports_created ON citizen_reports (created_at DESC);
