CREATE OR REPLACE VIEW vw_machine_load_profiles AS
SELECT
    m.machine_code,
    m.machine_name,
    m.factory_zone,
    date_trunc('hour', s.recorded_at) AS recorded_hour,
    AVG(s.load_percentage) AS avg_load,
    MAX(s.load_percentage) AS peak_load,
    SUM(s.energy_consumption) AS total_energy,
    AVG(s.temperature) AS avg_temperature,
    AVG(s.vibration) AS avg_vibration
FROM sensor_data s
JOIN machines m ON s.machine_id = m.id
GROUP BY m.machine_code, m.machine_name, m.factory_zone, date_trunc('hour', s.recorded_at);

CREATE OR REPLACE VIEW vw_data_quality_issues AS
SELECT
    m.machine_code,
    m.machine_name,
    s.recorded_at,
    CASE
        WHEN s.temperature > 90 THEN 'High temperature'
        WHEN s.vibration > 5 THEN 'High vibration'
        WHEN s.load_percentage > 95 THEN 'Machine overload'
        WHEN s.energy_consumption > 200 THEN 'High energy consumption'
    END AS issue,
    CASE
        WHEN s.temperature > 90 OR s.load_percentage > 95 THEN 'Critical'
        WHEN s.vibration > 5 OR s.energy_consumption > 200 THEN 'Warning'
    END AS severity
FROM sensor_data s
JOIN machines m ON s.machine_id = m.id
WHERE s.temperature > 90 OR s.vibration > 5 OR s.load_percentage > 95 OR s.energy_consumption > 200;

CREATE OR REPLACE VIEW vw_reliability_summary AS
SELECT
    m.machine_code,
    m.machine_name,
    COUNT(*) AS records,
    SUM(CASE WHEN s.temperature > 90 OR s.vibration > 8 OR s.load_percentage > 95 THEN 1 ELSE 0 END) AS anomaly_events,
    AVG(s.load_percentage) AS avg_load,
    MAX(s.load_percentage) AS peak_load
FROM sensor_data s
JOIN machines m ON s.machine_id = m.id
GROUP BY m.machine_code, m.machine_name;
