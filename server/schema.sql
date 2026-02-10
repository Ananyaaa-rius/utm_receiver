CREATE TABLE IF NOT EXISTS utm_clicks (
    id BIGSERIAL PRIMARY KEY,
    utm_params JSONB NOT NULL,
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
