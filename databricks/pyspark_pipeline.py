from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, count, max, sum as spark_sum, when

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "machine_data.csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "processed_output"


def main():
    spark = (
        SparkSession.builder
        .appName("IndustrialFieldTelemetryAnalytics")
        .getOrCreate()
    )

    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(INPUT_FILE))
    )

    enriched_df = df.withColumn(
        "risk_level",
        when(col("temperature") >= 90, "Critical")
        .when(col("vibration") >= 5, "Warning")
        .when(col("load_percentage") >= 95, "Warning")
        .otherwise("Healthy"),
    ).withColumn(
        "reliability_score",
        when(col("temperature") >= 90, 35)
        .when(col("vibration") >= 5, 55)
        .when(col("load_percentage") >= 95, 65)
        .otherwise(90),
    )

    load_summary = enriched_df.groupBy(
        "machine_code",
        "machine_name",
        "factory_zone",
    ).agg(
        count("*").alias("records"),
        avg("load_percentage").alias("avg_load"),
        max("load_percentage").alias("max_load"),
        avg("temperature").alias("avg_temperature"),
        max("temperature").alias("max_temperature"),
        spark_sum("energy_consumption").alias("total_energy"),
        avg("reliability_score").alias("avg_reliability_score"),
    )

    anomalies = enriched_df.filter(
        (col("temperature") >= 90)
        | (col("vibration") >= 5)
        | (col("load_percentage") >= 95)
    )

    global_metrics = enriched_df.agg(
        count("*").alias("total_records"),
        avg("load_percentage").alias("global_avg_load"),
        avg("temperature").alias("global_avg_temperature"),
        spark_sum("energy_consumption").alias("global_total_energy"),
        avg("reliability_score").alias("global_reliability_score"),
    )

    print("\n=== RAW TELEMETRY SAMPLE ===")
    df.show(10, truncate=False)

    print("\n=== MACHINE LOAD SUMMARY ===")
    load_summary.show(truncate=False)

    print("\n=== DETECTED ANOMALIES ===")
    anomalies.show(truncate=False)

    print("\n=== GLOBAL METRICS ===")
    global_metrics.show(truncate=False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    load_summary.write.mode("overwrite").option("header", True).csv(
        str(OUTPUT_DIR / "load_summary")
    )

    anomalies.write.mode("overwrite").option("header", True).csv(
        str(OUTPUT_DIR / "anomalies")
    )

    global_metrics.write.mode("overwrite").option("header", True).csv(
        str(OUTPUT_DIR / "global_metrics")
    )

    print("\n=== PYSPARK PIPELINE COMPLETED SUCCESSFULLY ===")

    spark.stop()


if __name__ == "__main__":
    main()