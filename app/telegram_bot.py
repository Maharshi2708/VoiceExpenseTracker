import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import aiohttp
import openai
import os
from config.config import OPENAI_API_KEY, TELEGRAM_BOT_TOKEN
from tempfile import NamedTemporaryFile 
from .expense_parser import parse_expense_message, is_expense_message
from .airtable_manager import store_expense

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "👋 Hello! I'm your Expense Tracker Bot.\n\n"
        "I can help you keep track of your expenses. Just send me a message like:\n"
        "- 'Spent 500 on food'\n"
        "- '₹200 for groceries'\n"
        "- '50 rupees on coffee'\n\n"
        "You can also include a subcategory like:\n"
        "- '₹300 on food subcategory lunch'\n\n"
        "Let's start tracking your expenses!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "💰 *Expense Tracker Bot Help* 💰\n\n"
        "*How to record expenses:*\n"
        "- Simply send a message describing your expense\n"
        "- Include the amount (with or without ₹ symbol)\n"
        "- Optionally add a category (e.g., 'for food')\n"
        "- Optionally add a subcategory (e.g., 'subcategory lunch')\n\n"
        "*Examples:*\n"
        "• Spent ₹500 on food\n"
        "• 200 rupees for groceries subcategory vegetables\n"
        "• Paid 50 for coffee\n\n"
        "*Commands:*\n"
        "/start - Restart the bot\n"
        "/help - Show this help message"
    )
    await update.message.reply_text(help_message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    
    if is_expense_message(message_text):
        logger.info(f"Received expense message: {message_text}")
        
        expense_data = parse_expense_message(message_text)
        
        if store_expense(expense_data):
            response = (
                f"✅ Expense recorded successfully!\n\n"
                f"Amount: ₹{expense_data['amount']}\n"
                f"Category: {expense_data['category']}"
            )
            
            if expense_data['sub_category']:
                response += f"\nSubcategory: {expense_data['sub_category']}"
                
            await update.message.reply_text(response)
        else:
            await update.message.reply_text(
                "❌ Sorry, I couldn't save your expense. Please try again later."
            )
    else:
        await update.message.reply_text(
            "I didn't recognize that as an expense. Please include an amount, like '₹500 for food' or '200 on groceries'."
        )

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages: download, transcribe, and store as expense."""
    try:
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)

        async with aiohttp.ClientSession() as session:
            async with session.get(file.file_path) as resp:
                if resp.status == 200:
                    with NamedTemporaryFile(delete=False, suffix=".ogg") as temp_audio:
                        temp_audio.write(await resp.read())
                        temp_audio_path = temp_audio.name

        with open(temp_audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        os.remove(temp_audio_path)  

        transcribed_text = transcript.text
        logger.info(f"Transcribed voice: {transcribed_text}")

        if is_expense_message(transcribed_text):
            expense_data = parse_expense_message(transcribed_text)
            if store_expense(expense_data):
                response = (
                    f"✅ Voice expense recorded!\n\n"
                    f"Amount: ₹{expense_data['amount']}\n"
                    f"Category: {expense_data['category']}"
                )
                if expense_data['sub_category']:
                    response += f"\nSubcategory: {expense_data['sub_category']}"
                await update.message.reply_text(response)
            else:
                await update.message.reply_text("❌ Couldn't store the expense. Try again.")
        else:
            await update.message.reply_text(
                "I transcribed your voice but couldn't recognize an expense. Please try again."
            )

    except Exception as e:
        logger.error(f"Voice transcription failed: {e}")
        await update.message.reply_text("❌ Failed to process your voice message.")

def main():
    """Start the bot."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

 
    logger.info("Bot started!")
    application.run_polling()

if __name__ == '__main__':
    main()
