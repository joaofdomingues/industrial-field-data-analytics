-- PostgreSQL schema for the Industrial Field Data Analytics Platform

CREATE TABLE IF NOT EXISTS machines (
    id BIGSERIAL PRIMARY KEY,
    machine_code VARCHAR(20) UNIQUE NOT NULL,
    machine_name VARCHAR(100) NOT NULL,
    factory_zone VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS sensor_data (
    id BIGSERIAL PRIMARY KEY,
    machine_id BIGINT NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    temperature NUMERIC(5,2) NOT NULL,
    vibration NUMERIC(5,2) NOT NULL,
    energy_consumption NUMERIC(10,2) NOT NULL,
    load_percentage NUMERIC(5,2) NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    CONSTRAINT chk_load_percentage CHECK (load_percentage BETWEEN 0 AND 100),
    CONSTRAINT chk_energy_positive CHECK (energy_consumption >= 0),
    CONSTRAINT chk_vibration_positive CHECK (vibration >= 0)
);

CREATE TABLE IF NOT EXISTS alerts (
    id BIGSERIAL PRIMARY KEY,
    machine_id BIGINT NOT NULL REFERENCES machines(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sensor_data_machine_time ON sensor_data(machine_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_data_recorded_at ON sensor_data(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
