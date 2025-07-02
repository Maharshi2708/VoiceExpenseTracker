# Voice ChatBot Expense Tracker

## Features
- Voice command input via Telegram
- Extracts amount, category, sub-category, and description using OpenAI
- Stores data in Airtable
- Displays a dashboard with visual analytics

## Setup
1. Clone this repo
2. Rename `config/config.py.example` to `config/config.py` and fill in your API keys
3. Run `pip install -r requirements.txt`
4. Run the Telegram bot: `python main.py`
5. Launch dashboard: `cd dashboard && python app.py`