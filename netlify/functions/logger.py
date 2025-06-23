# File: netlify/functions/logger.py

import json

def handler(event, context):
    # This is the most important line
    print("--- LOGGER FUNCTION WAS TRIGGERED! THE CONNECTION IS WORKING! ---")
    
    # We can also print the data we received from Telegram
    print("--- RECEIVED DATA ---")
    print(json.dumps(event, indent=2))
    print("--------------------")
    
    # Acknowledge the request
    return {'statusCode': 200, 'body': 'Log recorded.'}

