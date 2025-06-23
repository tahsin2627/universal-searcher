# File: functions/logger.py

import json

def handler(event, context):
    print("--- LOGGER FUNCTION WAS TRIGGERED! THE CONNECTION IS WORKING! ---")
    
    print("--- RECEIVED DATA ---")
    print(json.dumps(event, indent=2))
    print("--------------------")
    
    # Acknowledge the request
    return {'statusCode': 200, 'body': 'Log recorded.'}

