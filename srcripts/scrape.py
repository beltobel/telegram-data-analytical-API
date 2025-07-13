import os
import json
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from telethon.errors import SessionPasswordNeededError
from dotenv import load_dotenv
from scripts.utils import save_json, download_image, log_message

# Load credentials from .env
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
SESSION_NAME = os.getenv("SESSION_NAME")

# ✅ Updated channel list
CHANNELS = [
    "https://t.me/CheMed123",
    "https://t.me/lobelia4cosmetics",
    "https://t.me/tikvahpharma",
    "https://t.me/tenamereja",
]

DATE_FORMAT = "%Y-%m-%d"

def authenticate_client():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    client.connect()
    
    if not client.is_user_authorized():
        try:
            client.send_code_request(PHONE)
            code = input("Enter the code sent to your Telegram: ")
            client.sign_in(PHONE, code)
        except SessionPasswordNeededError:
            password = input("Two-step verification enabled. Enter your password: ")
            client.sign_in(password=password)
    
    return client

def scrape_channel(client, channel):
    today = datetime.utcnow().strftime(DATE_FORMAT)
    save_dir = f"data/raw/telegram_messages/{today}/"
    os.makedirs(save_dir, exist_ok=True)

    file_name = channel.split("/")[-1] + ".json"
    file_path = os.path.join(save_dir, file_name)

    messages = []

    for message in client.iter_messages(channel, limit=100):  # Adjust limit as needed
        msg_dict = message.to_dict()

        if message.media and isinstance(message.media, MessageMediaPhoto):
            image_path = download_image(client, message)
            msg_dict["downloaded_image_path"] = image_path

        messages.append(msg_dict)

    save_json(messages, file_path)
    log_message(f"Scraped {len(messages)} messages from {channel} -> {file_path}")

def main():
    client = authenticate_client()
    for channel in CHANNELS:
        try:
            scrape_channel(client, channel)
        except Exception as e:
            log_message(f"Error scraping {channel}: {str(e)}")

    client.disconnect()

if __name__ == "__main__":
    main()
