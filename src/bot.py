import os
import time
import schedule
import argparse
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from oura_client import OuraClient
from ai_summarizer import AISummarizer
from utils.telegram_notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("OuraBot")

def job():
    """Daily job to fetch data and send summary."""
    logger.info("Starting daily summary job...")
    
    # Load credentials
    oura_client_id = os.getenv("OURA_CLIENT_ID")
    oura_client_secret = os.getenv("OURA_CLIENT_SECRET")
    openai_key = os.getenv("OPENAI_API_KEY")
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not all([oura_client_id, oura_client_secret, openai_key, telegram_token, chat_id]):
        logger.error("Missing configuration. Please check .env file.")
        return

    try:
        # Initialize clients
        oura = OuraClient(client_id=oura_client_id, client_secret=oura_client_secret)
        ai = AISummarizer(openai_key)
        telegram = TelegramNotifier(telegram_token, chat_id, verbose=True, logger=logger.info)

        # Get dates (Yesterday's data is usually the most complete for morning summary)
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        start_date = yesterday.isoformat()
        end_date = today.isoformat()
        
        logger.info(f"Fetching data from {start_date} to {end_date}...")

        # Fetch data
        sleep = oura.get_daily_sleep(start_date, end_date)
        activity = oura.get_daily_activity(start_date, end_date)
        readiness = oura.get_daily_readiness(start_date, end_date)
        stress = oura.get_daily_stress(start_date, end_date)
        spo2 = oura.get_daily_spo2(start_date, end_date)
        workouts = oura.get_workouts(start_date, end_date)
        
        # validate we have data
        if not sleep.get('data') and not activity.get('data') and not readiness.get('data'):
             msg = f"No Oura data found for {yesterday}. Sync your ring!"
             logger.warning(msg)
             telegram.send_message(msg)
             return

        # Generate Summary
        logger.info("Generating AI summary...")
        summary = ai.generate_health_summary(
            sleep, 
            activity, 
            readiness,
            stress_data=stress,
            spo2_data=spo2,
            workout_data=workouts
        )
        
        # Send to Telegram
        logger.info("Sending to Telegram...")
        telegram.send_message(summary)
        logger.info("Daily summary sent successfully.")

    except Exception as e:
        logger.error(f"Job failed: {e}", exc_info=True)

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Oura Health Telegram Bot")
    parser.add_argument("--run-now", action="store_true", help="Run the summary job immediately")
    parser.add_argument("--time", type=str, default="08:00", help="Time to run daily job (HH:MM)")
    args = parser.parse_args()

    if args.run_now:
        job()
        return

    logger.info(f"Oura Bot started. Scheduled to run at {args.time} daily.")
    schedule.every().day.at(args.time).do(job)

    # Initialize notifier for polling commands
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    notifier = TelegramNotifier(telegram_token, chat_id, verbose=False, logger=logger.info)

    logger.info("Listening for 'run' command...")

    while True:
        schedule.run_pending()
        
        # Check for commands
        try:
            updates = notifier.get_updates()
            for text in updates:
                if text.strip().lower() == "run":
                    logger.info("Received 'run' command! Generating summary...")
                    notifier.send_message("Processing manual run request...")
                    job()
        except Exception as e:
             logger.error(f"Error checking updates: {e}")

        time.sleep(2)

if __name__ == "__main__":
    main()
