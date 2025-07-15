from dagster import job, op, schedule, JobDefinition, ScheduleDefinition
import subprocess
from src.scrape import scrape_telegram_data
from src.load_raw_to_postgres import load_raw_data
from src.detect_objects import process_images

@op
def scrape_telegram_data_op():
    """Operation to scrape Telegram data."""
    try:
        scrape_telegram_data()
    except Exception as e:
        raise Exception(f"Failed to scrape Telegram data: {e}")

@op
def load_raw_to_postgres_op(context):
    """Operation to load raw data into PostgreSQL."""
    try:
        load_raw_data()
    except Exception as e:
        raise Exception(f"Failed to load raw data to PostgreSQL: {e}")

@op
def run_dbt_transformations_op(context):
    """Operation to run dbt transformations."""
    try:
        result = subprocess.run(
            ["dbt", "run", "--project-dir", "telegram_etl"],
            check=True,
            capture_output=True,
            text=True
        )
        context.log.info(result.stdout)
    except subprocess.CalledProcessError as e:
        raise Exception(f"dbt run failed: {e.stderr}")

@op
def run_yolo_enrichment_op(context):
    """Operation to run YOLOv8 object detection."""
    try:
        process_images()
    except Exception as e:
        raise Exception(f"Failed to run YOLOv8 enrichment: {e}")

@job
def telegram_pipeline():
    """Dagster job to orchestrate the Telegram data pipeline."""
    scraped_data = scrape_telegram_data_op()
    loaded_data = load_raw_to_postgres_op(scraped_data)
    transformed_data = run_dbt_transformations_op(loaded_data)
    run_yolo_enrichment_op(transformed_data)

@schedule(cron_schedule="0 0 * * *", job=telegram_pipeline)
def daily_telegram_pipeline_schedule():
    """Daily schedule for the Telegram pipeline."""
    return {}

if __name__ == "__main__":
    telegram_pipeline.execute_in_process()