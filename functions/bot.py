# File: functions/bot.py

import os
import json
import asyncio
import httpx
import re
from pymongo import MongoClient
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- CONFIGURATION ---
MONGO_URI = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = int(os.environ.get('API_ID'))
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')

TARGET_CHANNEL_USERNAME = 'https://t.me/+IXXBlPCAiww5NDU1'

# --- DATABASE HELPER ---
def update_database(title, links):
    client = MongoClient(MONGO_URI)
    db = client.link_database
    collection = db.links
    # Use a case-insensitive regex for the title matching
    collection.update_one(
        {'title': {'$regex': f'^{re.escape(title)}$', '$options': 'i'}},
        {
            '$addToSet': {'links': {'$each': links}},
            '$setOnInsert': {'title': title}
        },
        upsert=True
    )
    client.close()

# --- TELEGRAM HELPER ---
async def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

# --- MAIN HANDLER LOGIC ---
async def main_logic(event):
    body = json.loads(event['body'])
    message = body.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if not text or not chat_id:
        return

    # --- COMMAND ROUTING ---
    if text.startswith('/add '):
        try:
            command_body = text[5:]
            title, links_str = command_body.split('|')
            links = [link.strip() for link in links_str.split(',')]
            title = title.strip()
            if not title or not links:
                raise ValueError("Invalid format")

            update_database(title, links)
            await send_telegram_message(chat_id, f"✅ Success! Added {len(links)} link(s) for '{title}'.")
        except Exception as e:
            await send_telegram_message(chat_id, f"❌ Error: Invalid format. Use: /add Title | Link1, Link2")

    elif text.startswith('/find '):
        try:
            search_query = text[6:].strip()
            if not search_query:
                await send_telegram_message(chat_id, "Please provide a title to find. e.g., /find The Matrix")
                return

            await send_telegram_message(chat_id, f"🔎 Searching for '{search_query}'... This may take a moment.")
            
            found_links = []
            # Connect Telethon client
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                channel = await client.get_entity(TARGET_CHANNEL_USERNAME)
                # Search messages in the channel for the exact title
                async for msg in client.iter_messages(channel, search=search_query, limit=5):
                    if msg.text:
                        urls = re.findall(r'https?://[^\s]+', msg.text)
                        if urls:
                            found_links.extend(urls)
            
            if not found_links:
                await send_telegram_message(chat_id, f"🤷 No links found for '{search_query}' in the source channel.")
                return

            update_database(search_query, found_links)
            await send_telegram_message(chat_id, f"✅ Success! Found and added {len(found_links)} new link(s) for '{search_query}'.")

        except Exception as e:
            await send_telegram_message(chat_id, f"❌ An error occurred during scraping: {e}")

# --- NETLIFY HANDLER ---
def handler(event, context):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_logic(event))
    return {'statusCode': 200, 'body': 'OK'}

