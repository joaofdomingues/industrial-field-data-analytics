"""
Optional Azure Databricks / PySpark version of the load-profile transformation.
This is intentionally kept simple so it can be discussed in interview even when
Databricks is not available locally.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, date_trunc, max as spark_max, sum as spark_sum, when

spark = SparkSession.builder.appName('industrial-load-profile-etl').getOrCreate()

raw_path = 'dbfs:/mnt/field-data/machine_data.csv'
output_path = 'dbfs:/mnt/field-data/processed/load_profiles'

df = spark.read.option('header', True).option('inferSchema', True).csv(raw_path)

clean = (
    df.dropna()
    .filter(col('load_percentage').between(0, 100))
    .filter(col('energy_consumption') >= 0)
    .withColumn(
        'is_anomaly',
        when((col('temperature') > 90) | (col('vibration') > 8) | (col('load_percentage') > 95), 1).otherwise(0),
    )
)

profiles = (
    clean.withColumn('recorded_hour', date_trunc('hour', col('recorded_at')))
    .groupBy('machine_code', 'machine_name', 'factory_zone', 'recorded_hour')
    .agg(
        avg('load_percentage').alias('avg_load'),
        spark_max('load_percentage').alias('peak_load'),
        spark_sum('energy_consumption').alias('total_energy'),
        avg('temperature').alias('avg_temperature'),
        avg('vibration').alias('avg_vibration'),
        spark_sum('is_anomaly').alias('anomaly_events'),
    )
)

profiles.write.mode('overwrite').parquet(output_path)
