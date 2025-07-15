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
project_root/ <br>
├── .gitignore                      # Excludes sensitive files (.env, data/raw/, logs/, <br> *.jpg, *.png) <br>
├── requirements.txt                # Python dependencies <br>
├── Dockerfile                      # Docker configuration for the application <br>
├── docker-compose.yml              # Orchestrates app and database services <br>
├── .env                            # Environment variables (not tracked in Git) <br>
├── src/                            # Source code <br>
│   ├── api/                        # FastAPI application  <br>
│   │   ├── main.py                 # FastAPI app and endpoints <br>
│   │   ├── database.py             # SQLAlchemy database connection <br>
│   │   ├── models.py               # SQLAlchemy models <br>
│   │   ├── schemas.py              # Pydantic schemas <br>
│   │   ├── crud.py                 # Query logic for endpoints <br>
│   ├── pipeline.py                 # Dagster pipeline definition  <br>
│   ├── config.py                   # Environment variable loading <br>
│   ├── scraper.py                  # Telegram data scraping  <br>
│   ├── load_raw_data.py            # Raw data loading to PostgreSQL  <br>
│   ├── object_detection.py          # YOLOv8 object detection  <br>
│   └── __init__.py
├── data/                           # Data lake <br>
│   ├── raw/
│   │   ├── telegram_messages/      # Partitioned JSON message files <br>
│   │   │   ├── YYYY-MM-DD/ <br>
│   │   │   │   ├── lobelia4cosmetics.json <br>
│   │   │   │   ├── tikvahpharma.json <br>
│   │   ├── telegram_media/         # Partitioned image files <br>
│   │   │   ├── YYYY-MM-DD/ <br>
│   │   │   │   ├── lobelia4cosmetics/ <br>
│   │   │   │   │   ├── message_id.jpg <br>
│   │   │   │   ├── tikvahpharma/ <br>
│   │   │   │   │   ├── message_id.jpg <br>
├── telegram_etl/                   # dbt project  <br>
│   ├── dbt_project.yml <br>
│   ├── profiles.yml <br>
│   ├── models/ <br>
│   │   ├── stg_telegram_messages.sql <br>
│   │   ├── dim_channels.sql <br>
│   │   ├── dim_dates.sql <br>
│   │   ├── fct_messages.sql <br>
│   │   ├── fct_image_detections.sql <br>
│   ├── tests/ <br>
│   ├── target/ <br>
│   ├── dbt_packages/ <br>
│   ├── logs/ <br>
│   │   ├── dbt.log <br>
├── scraping.log                    # Scraping logs  <br>
├── object_detection.log            # Object detection logs <br>

## Prerequisites

Docker: For containerization. <br>
Docker Compose: For orchestrating services. <br>
Python 3.11: For local development (optional). <br>
Telegram API Credentials: Obtain API_ID and API_HASH from my.telegram.org. <br>
PostgreSQL: Managed via Docker (no local installation required). <br>

## Setup Instructions

Clone the Repository: <br>
git clone <repository-url> <br>
cd <repository-directory> <br>


Create .env File:Create a .env file in the project root with the following variables: <br>
DB_USER=your_postgres_user <br>
DB_PASSWORD=your_postgres_password <br>
DB_NAME=telegram_db <br>
DB_HOST=db <br>
DB_PORT=5432 <br>
API_ID=your_telegram_api_id <br>
API_HASH=your_telegram_api_hash <br>


Install Dependencies:Dependencies are listed in requirements.txt: <br>
python-dotenv==1.0.1 <br>
psycopg2-binary==2.9.9 <br>
telethon==1.40.0 <br>
dbt-core==1.4.1 <br>
dbt-postgres==1.4.1 <br>
ultralytics==8.3.4 <br>
fastapi==0.115.2 <br>
uvicorn==0.32.0 <br>
sqlalchemy==2.0.36 <br>
dagster==1.8.7 <br>
dagster-webserver==1.8.7 <br>


Build and Run Docker Containers: <br>
docker-compose build <br>
docker-compose up -d <br>


Run dbt Models (if needed): <br>
docker-compose exec app dbt run --project-dir telegram_etl <br>


Access Services: <br>

Dagster UI: http://localhost:3000 (Task 5) <br>
FastAPI: http://localhost:8000  <br>



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

Directory: telegram_etl/ <br>
Functionality: Uses dbt to transform raw data into a star schema: <br>
Staging: stg_telegram_messages.sql cleans raw_telegram_messages. <br>
Data Mart: <br>
fct_messages.sql: Fact table with message_id, channel_name, message_timestamp,  <br>message_length, has_image, message_date_key. <br>
dim_channels.sql: Dimension table with unique channel names. <br>
dim_dates.sql: Dimension table with date attributes (day, month, year, quarter, day_name). <br>


Tests: Ensures message_id and channel_name are unique and not null.
Documentation: Generate via dbt docs generate.



### Data Enrichment with Object Detection

Script: src/object_detection.py
Functionality: Applies YOLOv8 (yolov8n.pt) to images in data/raw/telegram_media/, storing results in image_detections (message_id, channel_name, image_path, detected_object_class, confidence_score). Transformed into fct_image_detections.sql via dbt.
Logs: Outputs to object_detection.log.

### Analytical API with FastAPI

Directory: src/api/ <br>
Endpoints: <br>
GET /api/reports/top-products?limit=10: Returns top detected objects (products). <br>
GET /api/channels/{channel_name}/activity: Returns daily message counts for a channel. <br>
GET /api/search/messages?query=paracetamol: Searches messages by keyword. <br>


Access: http://localhost:8000/docs for Swagger UI. <br>
Validation: Uses Pydantic schemas for response structure. <br>

### Pipeline Orchestration with Dagster

Script: src/pipeline.py <br>
Functionality: Defines a Dagster job (telegram_pipeline) with ops: <br>
scrape_telegram_data_op: Runs scraper.py. <br>
load_raw_to_postgres_op: Runs load_raw_data.py. <br>
run_dbt_transformations_op: Runs dbt run. <br>
run_yolo_enrichment_op: Runs object_detection.py. <br>


Schedule: Runs daily at midnight (0 0 * * *). <br>
UI: Monitor at http://localhost:3000. <br>

