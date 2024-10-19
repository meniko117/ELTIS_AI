from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, CallbackQueryHandler
import query_LLM_from_telegram
import csv
from datetime import datetime
import json

# CSV file to log conversations
LOG_FILE = 'conversation_log.csv'

# Your Telegram ID for approval
# bot to get ID @getidsbot
ADMIN_ID = 393343171   # or use your username '@meniko117' 9703399

# Conversation states
WAITING_ADMIN_APPROVAL, EDITING_RESPONSE = range(2)

# Dictionary to store pending messages
pending_messages = {}

# Function to log conversation to CSV
def log_conversation(user_id, chat_id, question, answer):
    with open(LOG_FILE, 'a', newline='', encoding='WINDOWS-1251') as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(['date', 'user_id', 'chat_id', 'question', 'answer'])
        
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        question = question.replace('\n', ' ')
        answer = answer.replace('\n', ' ')
        
        writer.writerow([date, str(user_id), str(chat_id), question, answer])

# Function to handle the /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Hi! Send me any message, and I will query the LLM for you.')

# Function to query LLM and request admin approval
async def query_llm(update: Update, context: CallbackContext):
    user_message = update.message.text
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    await update.message.reply_text("Processing your query, please wait...")
    
    try:
        # Call the query_llm function from query_LLM_from_telegram.py
        llm_response = query_LLM_from_telegram.query_llm(user_message)
        
        message_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        pending_messages[message_id] = {
            'user_message': user_message,
            'llm_response': llm_response,
            'chat_id': chat_id,
            'user_id': user_id
        }
        
        keyboard = [
            [InlineKeyboardButton("Approve", callback_data=f"approve_{message_id}"),
             InlineKeyboardButton("Reject", callback_data=f"reject_{message_id}"),
             InlineKeyboardButton("Edit", callback_data=f"edit_{message_id}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"User {user_id} asked: {user_message}\n\nProposed reply:\n{llm_response}",
            reply_markup=reply_markup
        )
        
        return WAITING_ADMIN_APPROVAL

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")
        return ConversationHandler.END

# Function to handle admin's response
async def handle_admin_response(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    action, message_id = query.data.split('_', 1)
    pending_msg = pending_messages.get(message_id)
    
    if not pending_msg:
        await query.edit_message_text("This message is no longer pending.")
        return ConversationHandler.END
    
    if action == 'approve':
        final_response = pending_msg['llm_response']
        await send_final_response(context, pending_msg, final_response)
    elif action == 'reject':
        final_response = "Sorry, I couldn't provide a satisfactory answer at this time."
        await send_final_response(context, pending_msg, final_response)
    elif action == 'edit':
        await query.edit_message_text(
            f"Please provide the edited response for user {pending_msg['user_id']}:\n\nOriginal question: {pending_msg['user_message']}\n\nCurrent response: {pending_msg['llm_response']}"
        )
        context.user_data['editing_message_id'] = message_id
        return EDITING_RESPONSE
    
    return ConversationHandler.END

async def edit_response(update: Update, context: CallbackContext):
    message_id = context.user_data.get('editing_message_id')
    if not message_id or message_id not in pending_messages:
        await update.message.reply_text("No message to edit.")
        return ConversationHandler.END
    
    edited_response = update.message.text
    pending_msg = pending_messages[message_id]
    await send_final_response(context, pending_msg, edited_response)
    
    del context.user_data['editing_message_id']
    return ConversationHandler.END

async def send_final_response(context, pending_msg, final_response):
    await context.bot.send_message(
        chat_id=pending_msg['chat_id'],
        text=final_response
    )
    log_conversation(pending_msg['user_id'], pending_msg['chat_id'], pending_msg['user_message'], final_response)
    del pending_messages[list(pending_messages.keys())[list(pending_messages.values()).index(pending_msg)]]
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Response sent to user {pending_msg['user_id']}."
    )

def main():
    # Initialize the bot with your token
    bot_token = '7351062708:AAH9Am_S4yt8Bs795q5XA_QkR3dlSZWCzgI'
    app = ApplicationBuilder().token(bot_token).build()

    # Create conversation handler
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, query_llm)],
        states={
            WAITING_ADMIN_APPROVAL: [CallbackQueryHandler(handle_admin_response)],
            EDITING_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_response)]
        },
        fallbacks=[]
    )

    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)

    # Start polling for messages
    app.run_polling()

if __name__ == '__main__':
    main()
