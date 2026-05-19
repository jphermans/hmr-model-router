#!/usr/bin/env python3
"""
EXAMPLE: Telegram Bot with Cost Tracking Integration
Replace this code in your actual bot to activate cost tracking
"""

import sys
from pathlib import Path

# Add cost tracker to path
sys.path.insert(0, str(Path.home() / ".hermes" / "scripts"))

# Import the cost tracker
from telegram_cost_tracker import append_cost_to_telegram_response

# Your existing bot code
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === YOUR EXISTING BOT CODE ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send start message."""
    response = "🤖 Welcome to the Hermes Agent! I'm ready to help.\n\nSend me any question!"
    
    # === ADD COST TRACKING ===
    response = append_cost_to_telegram_response(response, "qwen/qwen3.5-flash-02-23")
    
    await update.message.reply_text(response)


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get weather information."""
    query = update.message.text
    
    # Your existing weather logic
    weather_response = fetch_weather_data(query)
    
    # === ADD COST TRACKING ===
    response = append_cost_to_telegram_response(weather_response, "qwen/qwen3.5-flash-02-23")
    
    await update.message.reply_text(response)


def fetch_weather_data(query: str) -> str:
    """Simulate weather API call - replace with your actual logic"""
    return "🌤️  Brussels weather: Cloudy, 18°C, 60% humidity. Wind: 15 km/h NW."


# === MAIN ENTRY POINT ===

def main():
    # Create application
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, weather))

    # Run bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("✅ Bot started with cost tracking enabled!")


if __name__ == '__main__':
    main()
