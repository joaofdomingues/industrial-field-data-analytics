from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / 'data' / 'raw' / 'machine_data.csv'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
CLEAN_FILE = PROCESSED_DIR / 'clean_machine_data.csv'
LOAD_PROFILE_FILE = PROCESSED_DIR / 'load_profiles_by_machine_hour.csv'
QUALITY_FILE = PROCESSED_DIR / 'data_quality_report.csv'


def build_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    checks = []
    for idx, row in df.iterrows():
        if row['temperature'] > 90:
            checks.append((idx, row['machine_code'], 'temperature', row['temperature'], 90, 'Critical'))
        if row['vibration'] > 5:
            checks.append((idx, row['machine_code'], 'vibration', row['vibration'], 5, 'Warning'))
        if row['load_percentage'] > 95:
            checks.append((idx, row['machine_code'], 'load_percentage', row['load_percentage'], 95, 'Critical'))
        if row['energy_consumption'] > 200:
            checks.append((idx, row['machine_code'], 'energy_consumption', row['energy_consumption'], 200, 'Warning'))
    return pd.DataFrame(checks, columns=['row_id', 'machine_code', 'metric', 'value', 'threshold', 'severity'])


def main():
    print('Starting industrial field-data ETL...')
    df = pd.read_csv(RAW_FILE, parse_dates=['recorded_at'])
    before = len(df)

    required = ['machine_code', 'machine_name', 'factory_zone', 'temperature', 'vibration', 'energy_consumption', 'load_percentage', 'recorded_at']
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f'Missing required columns: {missing}')

    df = df.drop_duplicates()
    df = df.dropna(subset=required)
    df = df[df['temperature'].between(-20, 130)]
    df = df[df['vibration'].between(0, 30)]
    df = df[df['energy_consumption'].between(0, 1000)]
    df = df[df['load_percentage'].between(0, 100)]

    df['load_zscore'] = df.groupby('machine_code')['load_percentage'].transform(lambda s: (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) else 0)
    df['energy_rolling_avg'] = df.groupby('machine_code')['energy_consumption'].transform(lambda s: s.rolling(3, min_periods=1).mean())
    df['is_high_temperature'] = df['temperature'] > 90
    df['is_high_vibration'] = df['vibration'] > 8
    df['is_overload'] = df['load_percentage'] > 95
    df['is_anomaly'] = df['is_high_temperature'] | df['is_high_vibration'] | df['is_overload'] | (df['load_zscore'].abs() > 2)

    profiles = (
        df.assign(recorded_hour=df['recorded_at'].dt.floor('h'))
        .groupby(['machine_code', 'machine_name', 'factory_zone', 'recorded_hour'], as_index=False)
        .agg(
            avg_load=('load_percentage', 'mean'),
            peak_load=('load_percentage', 'max'),
            avg_temperature=('temperature', 'mean'),
            avg_vibration=('vibration', 'mean'),
            total_energy=('energy_consumption', 'sum'),
            anomaly_events=('is_anomaly', 'sum'),
        )
    )

    quality = build_quality_report(df)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
    profiles.to_csv(LOAD_PROFILE_FILE, index=False)
    quality.to_csv(QUALITY_FILE, index=False)

    print(f'Rows loaded: {before}')
    print(f'Rows after cleaning: {len(df)}')
    print(f'Clean data: {CLEAN_FILE}')
    print(f'Load profiles: {LOAD_PROFILE_FILE}')
    print(f'Data quality report: {QUALITY_FILE}')
    print('ETL completed successfully.')


if __name__ == '__main__':
    main()
