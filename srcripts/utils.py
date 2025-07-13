import os, json, logging
from datetime import datetime

def save_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def download_image(client, message):
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    img_dir = f"data/raw/images/{date_str}/"
    os.makedirs(img_dir, exist_ok=True)
    file_path = os.path.join(img_dir, f"{message.id}.jpg")
    client.download_media(message, file_path)
    return file_path

def log_message(msg):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "scraping.log")
    with open(log_file, "a") as f:
        f.write(f"{datetime.utcnow().isoformat()} - {msg}\n")
