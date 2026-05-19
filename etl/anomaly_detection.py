from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_FILE = BASE_DIR / 'data' / 'processed' / 'clean_machine_data.csv'
ALERTS_FILE = BASE_DIR / 'data' / 'processed' / 'alerts.csv'
RELIABILITY_FILE = BASE_DIR / 'data' / 'processed' / 'reliability_summary.csv'


def severity(row):
    if row['temperature'] > 100 or row['load_percentage'] > 98 or row['vibration'] > 10:
        return 'Critical'
    return 'Warning'


def main():
    print('Starting anomaly and reliability analysis...')
    df = pd.read_csv(PROCESSED_FILE, parse_dates=['recorded_at'])

    alerts = df[df['is_anomaly'].astype(bool)].copy()
    alerts['severity'] = alerts.apply(severity, axis=1)
    alerts['alert_type'] = alerts.apply(
        lambda r: 'Overload' if r['load_percentage'] > 95 else 'High Temperature' if r['temperature'] > 90 else 'High Vibration',
        axis=1,
    )
    alerts['message'] = alerts.apply(
        lambda r: f"{r['machine_name']} anomaly: load={r['load_percentage']:.1f}%, temp={r['temperature']:.1f}, vibration={r['vibration']:.1f}",
        axis=1,
    )
    alerts[['machine_code', 'machine_name', 'factory_zone', 'recorded_at', 'alert_type', 'severity', 'message']].to_csv(ALERTS_FILE, index=False)

    rows = []
    for machine_code, group in df.groupby('machine_code'):
        group = group.sort_values('recorded_at')
        anomalies = int(group['is_anomaly'].sum())
        operating_hours = max((group['recorded_at'].max() - group['recorded_at'].min()).total_seconds() / 3600, 1)
        mtbf = round(operating_hours / anomalies, 2) if anomalies else None
        rows.append({
            'machine_code': machine_code,
            'machine_name': group['machine_name'].iloc[0],
            'records': len(group),
            'anomaly_events': anomalies,
            'estimated_mtbf_hours': mtbf,
            'avg_load': round(group['load_percentage'].mean(), 2),
            'peak_load': round(group['load_percentage'].max(), 2),
            'risk_level': 'High' if anomalies >= 3 else 'Medium' if anomalies else 'Low',
        })
    pd.DataFrame(rows).to_csv(RELIABILITY_FILE, index=False)

    print(f'Alerts generated: {len(alerts)}')
    print(f'Alerts file: {ALERTS_FILE}')
    print(f'Reliability summary: {RELIABILITY_FILE}')


if __name__ == '__main__':
    main()
