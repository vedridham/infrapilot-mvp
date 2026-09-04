CREATE TABLE deployments (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    version VARCHAR(100) NOT NULL,
    change_summary TEXT NOT NULL,
    deployed_at TIMESTAMPTZ NOT NULL,
    telemetry_source VARCHAR(30) NOT NULL DEFAULT 'synthetic'
);

CREATE TABLE telemetry_samples (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    recorded_at TIMESTAMPTZ NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    api_latency_ms NUMERIC(10, 2) NOT NULL CHECK (api_latency_ms >= 0),
    db_query_latency_ms NUMERIC(10, 2) NOT NULL CHECK (db_query_latency_ms >= 0),
    api_error_rate NUMERIC(5, 2) NOT NULL CHECK (api_error_rate BETWEEN 0 AND 100),
    db_cpu_percent NUMERIC(5, 2) NOT NULL CHECK (db_cpu_percent BETWEEN 0 AND 100),
    telemetry_source VARCHAR(30) NOT NULL DEFAULT 'synthetic'
);

CREATE TABLE incidents (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    status VARCHAR(30) NOT NULL CHECK (status IN ('open', 'investigating', 'resolved')),
    severity VARCHAR(30) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    endpoint VARCHAR(255) NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    p95_latency_ms NUMERIC(10, 2) NOT NULL,
    threshold_ms NUMERIC(10, 2) NOT NULL,
    error_rate NUMERIC(5, 2) NOT NULL,
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    incident_id BIGINT NOT NULL REFERENCES incidents(id),
    action VARCHAR(100) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);