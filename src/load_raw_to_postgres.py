import os
import json
import psycopg2
from dotenv import load_dotenv
from glob import glob
from datetime import datetime

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = "db" 
DB_PORT = 5432

RAW_TABLE = "raw_telegram_messages"

def connect_db():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )

def create_table_if_not_exists(cur):
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {RAW_TABLE} (
            id BIGINT PRIMARY KEY,
            channel TEXT,
            message TEXT,
            date TIMESTAMP,
            sender_id BIGINT,
            downloaded_image_path TEXT
        );
    """)

def insert_messages(cur, messages, channel_name):
    for msg in messages:
        cur.execute(f"""
            INSERT INTO {RAW_TABLE} (id, channel, message, date, sender_id, downloaded_image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, (
            msg.get("id"),
            channel_name,
            msg.get("message"),
            msg.get("date"),
            msg.get("sender_id", {}).get("user_id") if isinstance(msg.get("sender_id"), dict) else msg.get("sender_id"),
            msg.get("downloaded_image_path")
        ))

def load_all_files():
    conn = connect_db()
    cur = conn.cursor()
    create_table_if_not_exists(cur)

    for file_path in glob("data/raw/telegram_messages/*/*.json"):
        channel = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                print(f"Warning: {file_path} is empty.")
                continue
            try:
                messages = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in {file_path}: {e}")
                continue
            insert_messages(cur, messages, channel)
            print(f"Loaded {len(messages)} from {channel}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    load_all_files()
