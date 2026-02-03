import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

OURA_ACCESS_TOKEN = os.getenv("OURA_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test_openai():
    print("\n--- Testing OpenAI API ---")
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env")
        return

    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Just list models to verify auth
        models = client.models.list()
        print(f"✅ OpenAI API Connection Successful. Retrieved {len(list(models))} models.")
    except Exception as e:
        print(f"❌ OpenAI API Failed: {e}")

def test_oura_sandbox():
    print("\n--- Testing Oura Sandbox API ---")
    if not OURA_ACCESS_TOKEN:
        print("❌ OURA_ACCESS_TOKEN not found in .env")
        return

    # Using the Sandbox Tag endpoint from openapi-1.27.json
    # Endpoint: /v2/sandbox/usercollection/tag
    url = "https://api.ouraring.com/v2/sandbox/usercollection/tag"
    
    # Required parameters (or at least start_date/end_date are common)
    # The spec says they are optional but usually good to provide.
    # Let's try without first to see if it defaults or if we need them.
    # Actually, sandbox usually needs specific dates to return dummy data or just works.
    params = {
        "start_date": "2021-11-01", 
        "end_date": "2021-12-01"
    }
    
    headers = {
        "Authorization": f"Bearer {OURA_ACCESS_TOKEN}"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            print("✅ Oura Sandbox API Connection Successful.")
            # print(f"Response snippet: {str(data)[:200]}...")
        else:
            print(f"❌ Oura Sandbox API Failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Oura Sandbox API Request Failed: {e}")

def test_telegram():
    print("\n--- Testing Telegram Bot ---")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
        return

    message = "Hello from Oura Bot Sandbox Test!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Telegram Message Sent Successfully.")
        else:
            print(f"❌ Telegram Failed with status {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Telegram Request Failed: {e}")

if __name__ == "__main__":
    print("Starting Sandbox Verification...")
    test_openai()
    test_oura_sandbox()
    test_telegram()
    print("\nDone.")
