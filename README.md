# Shipping a Data Product: From Raw Telegram Data to an Analytical API
## Overview
This project implements a robust, scalable data pipeline to collect, process, enrich, and analyze data from public Telegram channels related to Ethiopian medical businesses (CheMed123, lobelia4cosmetics, tikvahpharma, tenamareja). The pipeline extracts messages and images, stores them in a partitioned data lake, loads them into a PostgreSQL database, transforms them into a star schema using dbt, enriches images with YOLOv8 object detection, serves analytical insights via a FastAPI application, and orchestrates the workflow with Dagster. The project leverages modern data engineering practices, including containerization with Docker, version control with Git, and secure environment management.

# Objectives

**Extract**: Scrape messages and images from Telegram channels using the Telethon library.
**Store**: Organize raw data in a partitioned data lake and load it into a PostgreSQL database.
**Transform**: Use dbt to create a star schema optimized for analytics.
**Enrich**: Apply YOLOv8 for object detection on images to identify products.
**Serve**: Provide analytical endpoints via a FastAPI application.
**Orchestrate**: Schedule and monitor the pipeline using Dagster.

## Project Structure
project_root/
├── .gitignore                      # Excludes sensitive files (.env, data/raw/, logs/, *.jpg, *.png)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration for the application
├── docker-compose.yml              # Orchestrates app and database services
├── .env                            # Environment variables (not tracked in Git)
├── src/                            # Source code
│   ├── api/                        # FastAPI application 
│   │   ├── main.py                 # FastAPI app and endpoints
│   │   ├── database.py             # SQLAlchemy database connection
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── crud.py                 # Query logic for endpoints
│   ├── pipeline.py                 # Dagster pipeline definition 
│   ├── config.py                   # Environment variable loading
│   ├── scraper.py                  # Telegram data scraping 
│   ├── load_raw_data.py            # Raw data loading to PostgreSQL 
│   ├── object_detection.py          # YOLOv8 object detection 
│   └── __init__.py
├── data/                           # Data lake
│   ├── raw/
│   │   ├── telegram_messages/      # Partitioned JSON message files
│   │   │   ├── YYYY-MM-DD/
│   │   │   │   ├── lobelia4cosmetics.json
│   │   │   │   ├── tikvahpharma.json
│   │   ├── telegram_media/         # Partitioned image files
│   │   │   ├── YYYY-MM-DD/
│   │   │   │   ├── lobelia4cosmetics/
│   │   │   │   │   ├── message_id.jpg
│   │   │   │   ├── tikvahpharma/
│   │   │   │   │   ├── message_id.jpg
├── telegram_etl/                   # dbt project 
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── stg_telegram_messages.sql
│   │   ├── dim_channels.sql
│   │   ├── dim_dates.sql
│   │   ├── fct_messages.sql
│   │   ├── fct_image_detections.sql
│   ├── tests/
│   ├── target/
│   ├── dbt_packages/
│   ├── logs/
│   │   ├── dbt.log
├── scraping.log                    # Scraping logs 
├── object_detection.log            # Object detection logs

## Prerequisites

Docker: For containerization.
Docker Compose: For orchestrating services.
Python 3.11: For local development (optional).
Telegram API Credentials: Obtain API_ID and API_HASH from my.telegram.org.
PostgreSQL: Managed via Docker (no local installation required).

## Setup Instructions

Clone the Repository:
git clone <repository-url>
cd <repository-directory>


Create .env File:Create a .env file in the project root with the following variables:
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_NAME=telegram_db
DB_HOST=db
DB_PORT=5432
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash


Install Dependencies:Dependencies are listed in requirements.txt:
python-dotenv==1.0.1
psycopg2-binary==2.9.9
telethon==1.40.0
dbt-core==1.4.1
dbt-postgres==1.4.1
ultralytics==8.3.4
fastapi==0.115.2
uvicorn==0.32.0
sqlalchemy==2.0.36
dagster==1.8.7
dagster-webserver==1.8.7


Build and Run Docker Containers:
docker-compose build
docker-compose up -d


Run dbt Models (if needed):
docker-compose exec app dbt run --project-dir telegram_etl


Access Services:

Dagster UI: http://localhost:3000 (Task 5)
FastAPI: http://localhost:8000 



## Usage
 ### Project Setup & Environment Management

Initializes a Git repository with .gitignore to exclude sensitive files.
Uses Docker to create a reproducible Python 3.11 environment with PostgreSQL.
Manages credentials securely via .env and python-dotenv.

### Data Scraping and Collection

Script: src/scraper.py
Functionality: Scrapes up to 100 messages per channel (CheMed123, lobelia4cosmetics, tikvahpharma, tenamareja) using Telethon. Stores messages as JSON in data/raw/telegram_messages/YYYY-MM-DD/channel_name.json and images in data/raw/telegram_media/YYYY-MM-DD/channel_name/message_id.jpg.
Logs: Outputs to scraping.log.

### Data Modeling and Transformation

Directory: telegram_etl/
Functionality: Uses dbt to transform raw data into a star schema:
Staging: stg_telegram_messages.sql cleans raw_telegram_messages.
Data Mart:
fct_messages.sql: Fact table with message_id, channel_name, message_timestamp, message_length, has_image, message_date_key.
dim_channels.sql: Dimension table with unique channel names.
dim_dates.sql: Dimension table with date attributes (day, month, year, quarter, day_name).


Tests: Ensures message_id and channel_name are unique and not null.
Documentation: Generate via dbt docs generate.



### Data Enrichment with Object Detection

Script: src/object_detection.py
Functionality: Applies YOLOv8 (yolov8n.pt) to images in data/raw/telegram_media/, storing results in image_detections (message_id, channel_name, image_path, detected_object_class, confidence_score). Transformed into fct_image_detections.sql via dbt.
Logs: Outputs to object_detection.log.

### Analytical API with FastAPI

Directory: src/api/
Endpoints:
GET /api/reports/top-products?limit=10: Returns top detected objects (products).
GET /api/channels/{channel_name}/activity: Returns daily message counts for a channel.
GET /api/search/messages?query=paracetamol: Searches messages by keyword.


Access: http://localhost:8000/docs for Swagger UI.
Validation: Uses Pydantic schemas for response structure.

### Pipeline Orchestration with Dagster

Script: src/pipeline.py
Functionality: Defines a Dagster job (telegram_pipeline) with ops:
scrape_telegram_data_op: Runs scraper.py.
load_raw_to_postgres_op: Runs load_raw_data.py.
run_dbt_transformations_op: Runs dbt run.
run_yolo_enrichment_op: Runs object_detection.py.


Schedule: Runs daily at midnight (0 0 * * *).
UI: Monitor at http://localhost:3000.

