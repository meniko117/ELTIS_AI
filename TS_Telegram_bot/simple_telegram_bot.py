from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio
import query_LLM_from_telegram
import csv
from datetime import datetime
import pandas as pd

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
    await update.message.reply_text('Hi! Send me any message, and I will respond with "Hello!".')

# Function to simulate a progress bar and respond with "Hello!"
async def query_llm(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Send initial progress message
    progress_message = await context.bot.send_message(chat_id=chat_id, text="Progress: [                    ] 0%")

    async def update_progress():
        for i in range(1, 11):
            progress_bar = '[' + '🟢' * i + ' ' * (10 - i) + ']'
            progress_text = f"Progress: {progress_bar} {i * 10}%"
            await progress_message.edit_text(progress_text)
            await asyncio.sleep(0.5)  # Simulate some processing time

    try:
        # Run both the progress update and LLM query concurrently
        llm_response, _ = await asyncio.gather(
            query_LLM_from_telegram.query_llm(user_message),
            update_progress()
        )

        # Send the response to the user
        await context.bot.send_message(chat_id=chat_id, text=llm_response)

        # Log the conversation
        log_conversation(update.effective_user.id, chat_id, user_message, llm_response)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

def main():
    # Initialize the bot with your token
    bot_token = '7351062708:AAH9Am_S4yt8Bs795q5XA_QkR3dlSZWCzgI'
    app = ApplicationBuilder().token(bot_token).build()

    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, query_llm))

    # Start polling for messages
    app.run_polling()

if __name__ == '__main__':
    main()
