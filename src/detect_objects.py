import os
import psycopg2
from psycopg2 import extras
from ultralytics import YOLO
from config import Config
import logging

# Set up logging
logging.basicConfig(filename='object_detection.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load YOLOv8 model
model = YOLO('yolov8n.pt')  # Pre-trained YOLOv8 nano model

def process_images():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        port=Config.DB_PORT
    )
    cur = conn.cursor()

    # Create table if not exists
    cur.execute("""
    CREATE TABLE IF NOT EXISTS image_detections (
        message_id bigint,
        channel_name text,
        image_path text,
        detected_object_class text,
        confidence_score float
    )
    """)
    conn.commit()

    # Directory containing images
    media_dir = 'data/raw/telegram_media'

    # List to store detection results
    detections = []

    # Scan for images
    for root, dirs, files in os.walk(media_dir):
        for file in files:
            if file.endswith('.jpg') or file.endswith('.png'):
                image_path = os.path.join(root, file)
                try:
                    # Extract channel_name and message_id from path
                    parts = image_path.split(os.sep)
                    channel_name = parts[-2]
                    message_id = int(os.path.splitext(parts[-1])[0])

                    logging.info(f'Processing image: {image_path}')

                    # Run YOLOv8 inference
                    results = model(image_path)

                    # Process detection results
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls)
                            class_name = model.names[class_id]
                            confidence = float(box.conf)
                            detections.append((
                                message_id,
                                channel_name,
                                image_path,
                                class_name,
                                confidence
                            ))

                    logging.info(f'Detected {len(result.boxes)} objects in {image_path}')

                except Exception as e:
                    logging.error(f'Error processing image {image_path}: {e}')
                    continue

    # Insert detections into PostgreSQL
    try:
        extras.execute_values(cur,
            """INSERT INTO image_detections (message_id, channel_name, image_path, detected_object_class, confidence_score)
               VALUES %s""",
            detections
        )
        conn.commit()
        logging.info(f'Inserted {len(detections)} detections into image_detections table')
    except Exception as e:
        logging.error(f'Error inserting detections: {e}')
        conn.rollback()

    # Close cursor and connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    process_images()