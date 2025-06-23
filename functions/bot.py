# File: functions/bot.py (DEBUG VERSION)

import os
import json
import asyncio
import httpx
import re
from flask import Flask, request, jsonify
from pymongo import MongoClient
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# --- CONFIGURATION ---
MONGO_URI = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_ID = int(os.environ.get('API_ID')) if os.environ.get('API_ID') else None
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')
TARGET_CHANNEL_USERNAME = 'https://t.me/+IXXBlPCAiww5NDU1'

app = Flask(__name__)

# --- TELEGRAM HELPER ---
async def send_telegram_message(chat_id, text):
    print(f"DEBUG: Attempting to send message to {chat_id}: '{text}'")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
        print("DEBUG: Message sent successfully.")
    except Exception as e:
        print(f"DEBUG: FAILED TO SEND TELEGRAM MESSAGE: {e}")

# --- WEBHOOK ROUTE FOR THE BOT ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    print("\n--- DEBUG: WEBHOOK TRIGGERED ---")
    try:
        body = request.get_json()
        print(f"DEBUG: Received body: {json.dumps(body)}")
        
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')

        if not text or not chat_id:
            print("DEBUG: No text or chat_id found. Exiting.")
            return "OK", 200

        print(f"DEBUG: Processing command: {text}")
        if text.startswith('/find '):
            search_query = text[6:].strip()
            if not search_query:
                await send_telegram_message(chat_id, "Please provide a title to find.")
                return "OK", 200

            await send_telegram_message(chat_id, f"🔎 Searching for '{search_query}'...")
            
            print("DEBUG: Starting scraper logic...")
            found_links = []
            
            print("DEBUG: Initializing TelegramClient...")
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                print("DEBUG: Telethon client connected.")
                print(f"DEBUG: Getting entity for channel: {TARGET_CHANNEL_USERNAME}")
                channel = await client.get_entity(TARGET_CHANNEL_USERNAME)
                print("DEBUG: Channel entity found. Searching messages...")
                
                async for msg in client.iter_messages(channel, search=search_query, limit=5):
                    print(f"DEBUG: Found a message to process.")
                    if msg.text:
                        urls = re.findall(r'https?://[^\s]+', msg.text)
                        if urls:
                            print(f"DEBUG: Extracted links: {urls}")
                            found_links.extend(urls)
            
            print(f"DEBUG: Scraping finished. Found {len(found_links)} links.")
            if not found_links:
                await send_telegram_message(chat_id, f"🤷 No links found for '{search_query}'.")
                return "OK", 200

            print("DEBUG: Connecting to database to update...")
            db_client = MongoClient(MONGO_URI)
            db = db_client.link_database
            collection = db.links
            collection.update_one(
                {'title': {'$regex': f'^{re.escape(search_query)}$', '$options': 'i'}},
                {'$addToSet': {'links': {'$each': found_links}}, '$setOnInsert': {'title': search_query}},
                upsert=True
            )
            db_client.close()
            print("DEBUG: Database updated.")
            
            await send_telegram_message(chat_id, f"✅ Success! Found and added {len(found_links)} link(s) for '{search_query}'.")

    except Exception as e:
        print(f"--- FATAL ERROR IN WEBHOOK ---\n{e}\n------------------------------")
        if chat_id:
            await send_telegram_message(chat_id, f"❌ A fatal error occurred on the server.")

    return "OK", 200

# Other routes are removed for simplicity of this debug file.
@app.route('/')
def index():
    return "Bot backend is running! (DEBUG MODE)", 200
