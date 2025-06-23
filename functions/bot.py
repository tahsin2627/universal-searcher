# File: netlify/functions/bot.py (New Render-Ready Version)

import os
import json
import asyncio
import httpx
import re
from flask import Flask, request
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

# Create the Flask web server
app = Flask(__name__)


# --- DATABASE HELPER ---
def update_database(title, links):
    client = MongoClient(MONGO_URI)
    db = client.link_database
    collection = db.links
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

# --- WEBHOOK ROUTE ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    body = request.get_json()
    message = body.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')

    if not text or not chat_id:
        return "OK", 200

    # --- COMMAND ROUTING ---
    if text.startswith('/add '):
        # ... (add logic remains the same)
        try:
            command_body = text[5:]
            title, links_str = command_body.split('|')
            links = [link.strip() for link in links_str.split(',')]
            title = title.strip()
            if not title or not links: raise ValueError("Invalid format")
            update_database(title, links)
            await send_telegram_message(chat_id, f"✅ Success! Added {len(links)} link(s) for '{title}'.")
        except Exception:
            await send_telegram_message(chat_id, f"❌ Error: Invalid format. Use: /add Title | Link1, Link2")

    elif text.startswith('/find '):
        # ... (find logic remains the same)
        try:
            search_query = text[6:].strip()
            if not search_query:
                await send_telegram_message(chat_id, "Please provide a title to find. e.g., /find The Matrix")
                return "OK", 200

            await send_telegram_message(chat_id, f"🔎 Searching for '{search_query}'... This may take a moment.")
            
            found_links = []
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                channel = await client.get_entity(TARGET_CHANNEL_USERNAME)
                async for msg in client.iter_messages(channel, search=search_query, limit=5):
                    if msg.text:
                        urls = re.findall(r'https?://[^\s]+', msg.text)
                        if urls: found_links.extend(urls)
            
            if not found_links:
                await send_telegram_message(chat_id, f"🤷 No links found for '{search_query}'.")
                return "OK", 200

            update_database(search_query, found_links)
            await send_telegram_message(chat_id, f"✅ Success! Found and added {len(found_links)} link(s) for '{search_query}'.")

        except Exception as e:
            await send_telegram_message(chat_id, f"❌ An error occurred during scraping: {e}")
    
    return "OK", 200

# --- A simple root route to check if the server is up ---
@app.route('/')
def index():
    return "Bot backend is running!", 200
