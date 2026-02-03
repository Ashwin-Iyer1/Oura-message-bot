# Oura Bot 💍🤖

A Telegram bot that sends you daily AI-generated summaries of your Oura Ring health data.

## Features

- **Daily Health Summaries**: Automatically fetches your sleep, activity, and readiness scores.
- **AI Insights**: Uses OpenAI (GPT-4o) to analyze your data and provide personalized, encouraging tips.
- **Telegram Integration**: Receives daily reports directly in your preferred chat.
- **Sandbox Mode**: Includes a test script to verify API connections using Oura's Sandbox environment.

## Prerequisites

- Python 3.9+
- [Oura API Access Token](https://cloud.ouraring.com/docs/authentication)
- [OpenAI API Key](https://platform.openai.com/)
- [Telegram Bot Token](https://core.telegram.org/bots#how-do-i-create-a-bot)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd oura-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (copy from `.env.example` if available) and add your credentials:
   ```env
   OURA_ACCESS_TOKEN=your_oura_token
   OPENAI_API_KEY=your_openai_key
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_telegram_chat_id
   ```

## Usage

### Run the Bot
The bot includes a scheduler to run daily at a specified time.

**Run constantly (scheduled mode):**
```bash
python src/bot.py --time "08:00"
```
*Defaults to 08:00 if no time is specified.*

**Run immediately (one-off):**
```bash
python src/bot.py --run-now
```

### Run Tests
To verify valid API credentials and simulate the bot workflow using Oura Sandbox data:
```bash
python3 test_sandbox.py
```
This script will:
1. Check OpenAI API connection.
2. Fetch Dummy Data from Oura Sandbox (Sleep, Activity, Readiness).
3. Generate an AI summary.
4. Send the summary to your Telegram chat.

## Project Structure
- `src/bot.py`: Main entry point.
- `src/oura_client.py`: Oura API client.
- `src/ai_summarizer.py`: Logic for generating AI summaries.
- `src/utils/telegram_notifier.py`: Helper for sending Telegram messages.
- `test_sandbox.py`: Verification script.
