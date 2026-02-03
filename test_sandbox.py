import os
import sys
import requests
import json
from dotenv import load_dotenv
from openai import OpenAI

# Add src to path to import AISummarizer
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from ai_summarizer import AISummarizer

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
        models = client.models.list()
        print(f"✅ OpenAI API Connection Successful. Retrieved {len(list(models))} models.")
    except Exception as e:
        print(f"❌ OpenAI API Failed: {e}")

def fetch_sandbox_data(endpoint, params, headers):
    url = f"https://api.ouraring.com/v2/sandbox/usercollection/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            print(f"✅ Fetched Sandbox {endpoint}.")
            return response.json()
        else:
            print(f"❌ Failed to fetch {endpoint}: {response.status_code}")
            return {}
    except Exception as e:
        print(f"❌ Request failed for {endpoint}: {e}")
        return {}

def test_oura_sandbox_and_ai():
    print("\n--- Testing Oura Sandbox API & AI Summarizer ---")
    if not OURA_ACCESS_TOKEN:
        print("❌ OURA_ACCESS_TOKEN not found in .env")
        return

    # specific dates for sandbox data to ensure we get results
    params = {
        "start_date": "2021-11-01", 
        "end_date": "2021-12-01"
    }
    
    headers = {
        "Authorization": f"Bearer {OURA_ACCESS_TOKEN}"
    }

    # Fetch data
    sleep_data = fetch_sandbox_data("daily_sleep", params, headers)
    activity_data = fetch_sandbox_data("daily_activity", params, headers)
    readiness_data = fetch_sandbox_data("daily_readiness", params, headers)
    stress_data = fetch_sandbox_data("daily_stress", params, headers)
    spo2_data = fetch_sandbox_data("daily_spo2", params, headers)
    workout_data = fetch_sandbox_data("workout", params, headers)

    if not (sleep_data and activity_data and readiness_data):
        print("❌ Could not fetch all required data for summary.")
        return

    # Generate Summary
    print("\n--- Generating AI Summary ---")
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY missing, skipping AI summary.")
        return

    summarizer = AISummarizer(api_key=OPENAI_API_KEY)
    summary = summarizer.generate_health_summary(
        sleep_data, 
        activity_data, 
        readiness_data, 
        stress_data=stress_data, 
        spo2_data=spo2_data, 
        workout_data=workout_data
    )
    
    print("✅ Summary Generated:")
    print(summary)
    
    # Send to Telegram
    test_telegram(summary)

def test_telegram(message_text):
    print("\n--- Testing Telegram Bot ---")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not found in .env")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text.replace("<br>", "\n"),
        "parse_mode": "HTML"
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
    print("Starting Sandbox AI Bot Verification...")
    test_openai()
    test_oura_sandbox_and_ai()
    print("\nDone.")
