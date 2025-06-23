# File: bot.py (HYPER-DEBUG VERSION)

import os
import json
import asyncio
import httpx
import re
from flask import Flask, request, jsonify
from pymongo import MongoClient
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
import traceback # Import traceback to get detailed errors

# --- CONFIGURATION ---
MONGO_URI = os.environ.get('MONGO_URI')
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
# Add default=0 to prevent error if variable is missing, we'll check later
API_ID = int(os.environ.get('API_ID', 0)) 
API_HASH = os.environ.get('API_HASH')
SESSION_STRING = os.environ.get('SESSION_STRING')

TARGET_CHANNEL_USERNAME = 'https://t.me/+IXXBlPCAiww5NDU1'

app = Flask(__name__)

# --- TELEGRAM HELPER ---
# This function will now be our eyes and ears
async def send_telegram_message(chat_id, text):
    # Truncate long messages for safety
    if len(text) > 4000:
        text = text[:4000] + "... (truncated)"
        
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": str(chat_id), "text": str(text)}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        # If this fails, we log it to Render, as we can't send a message about it
        print(f"CRITICAL: FAILED TO SEND TELEGRAM MESSAGE: {e}")


# --- WEBHOOK ROUTE FOR THE BOT ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    chat_id = None
    try:
        body = request.get_json()
        message = body.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')

        if not text or not chat_id:
            return "OK", 200

        if text.startswith('/find '):
            await send_telegram_message(chat_id, "DEBUG: `/find` command received. Starting process...")
            
            search_query = text[6:].strip()
            if not search_query:
                await send_telegram_message(chat_id, "DEBUG: No search query provided. Exiting.")
                return "OK", 200

            # Check for missing credentials BEFORE trying to use them
            if not all([API_ID, API_HASH, SESSION_STRING, MONGO_URI]):
                 await send_telegram_message(chat_id, "❌ FATAL ERROR: One or more environment variables (API_ID, API_HASH, SESSION_STRING, MONGO_URI) are missing in the Render settings.")
                 return "OK", 200

            await send_telegram_message(chat_id, "DEBUG: Step 1: Initializing Telethon Client...")
            
            async with TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH) as client:
                await send_telegram_message(chat_id, "DEBUG: Step 2: Telethon Client connected successfully.")

                await send_telegram_message(chat_id, f"DEBUG: Step 3: Getting channel entity for '{TARGET_CHANNEL_USERNAME}'...")
                channel = await client.get_entity(TARGET_CHANNEL_USERNAME)
                await send_telegram_message(chat_id, "DEBUG: Step 4: Channel entity found. Searching messages...")

                found_links = []
                async for msg in client.iter_messages(channel, search=search_query, limit=5):
                    if msg.text:
                        urls = re.findall(r'https?://[^\s]+', msg.text)
                        if urls:
                            found_links.extend(urls)
                
                await send_telegram_message(chat_id, f"DEBUG: Step 5: Search complete. Found {len(found_links)} links.")

                if not found_links:
                    await send_telegram_message(chat_id, f"🤷 No links found for '{search_query}' in the source channel.")
                    return "OK", 200

                await send_telegram_message(chat_id, "DEBUG: Step 6: Connecting to database...")
                db_client = MongoClient(MONGO_URI)
                db = db_client.link_database
                collection = db.links
                await send_telegram_message(chat_id, "DEBUG: Step 7: Database connected. Updating records...")
                
                collection.update_one(
                    {'title': {'$regex': f'^{re.escape(search_query)}$', '$options': 'i'}},
                    {'$addToSet': {'links': {'$each': found_links}}, '$setOnInsert': {'title': search_query}},
                    upsert=True
                )
                db_client.close()
                await send_telegram_message(chat_id, "DEBUG: Step 8: Database update complete.")

                await send_telegram_message(chat_id, f"✅ Success! Found and added {len(found_links)} new link(s) for '{search_query}'. Your website is updated.")

    except Exception as e:
        # This will catch ANY error and send it to you on Telegram
        error_details = traceback.format_exc()
        await send_telegram_message(chat_id, f"❌ A fatal error occurred!\n\nDetails:\n{error_details}")

    return "OK", 200

@app.route('/')
def index():
    return "Bot backend is running in HYPER-DEBUG MODE.", 200
