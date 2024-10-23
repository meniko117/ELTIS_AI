from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import query_LLM_from_telegram
import csv
from datetime import datetime
import pandas as pd
# this library python-telegram-bot should be isntalled useing pip
from dotenv import load_dotenv
import os


# Load the environment variables from the .env file
load_dotenv(dotenv_path='.env.txt')  # Specify the path if not named .env
# Access the API keys
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# CSV file to log conversations
LOG_FILE = 'conversation_log.xlsx'

# Function to log conversation to CSV

def log_conversation(user_id, chat_id, question, answer):
    # Create a DataFrame for the new log entry
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    question = question.replace('\n', ' ')
    answer = answer.replace('\n', ' ')
    
    new_entry = pd.DataFrame({
        'date': [date],
        'user_id': [str(user_id)],
        'chat_id': [str(chat_id)],
        'question': [question],
        'answer': [answer]
    })

    # Check if the Excel file exists
    try:
        # Try to read the existing file
        existing_data = pd.read_excel(LOG_FILE)
        # Append the new entry to the existing data
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
    except FileNotFoundError:
        # If the file does not exist, use the new entry as the initial data
        updated_data = new_entry

    # Write the updated data back to the Excel file
    updated_data.to_excel(LOG_FILE, index=False)

# Function to handle the /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hi! Send me any message, and I will query the LLM for you.')

# Function to query LLM and send response immediately
async def query_llm(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    await update.message.reply_text("Обрабатываем Ваш запрос, подождите, пожалуйста...")
    
    try:
        # Call the query_llm function from query_LLM_from_telegram.py
        llm_response = query_LLM_from_telegram.query_llm(user_message)
        
        #TODO! uncomment or comment this part to send the LLM reply 
        # Send the response to the user immediately
        await context.bot.send_message(
            chat_id=chat_id,
            text=llm_response
        )

        # Log the conversation
        log_conversation(user_id, chat_id, user_message, llm_response)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    # Initialize the bot with your token
    bot_token = TELEGRAM_TOKEN
    app = ApplicationBuilder().token(bot_token).build()

    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query_llm))

    # Start polling for messages
    app.run_polling()

if __name__ == '__main__':
    main()