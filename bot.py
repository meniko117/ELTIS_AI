import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from pydub import AudioSegment

# Replace 'YOUR_TOKEN' with the token you received from BotFather
TOKEN = '7351062708:AAH9Am_S4yt8Bs795q5XA_QkR3dlSZWCzgI'
DOWNLOAD_PATH = './downloads/'

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Send me a voice message, and I will save it!')

async def save_voice(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    file_id = update.message.voice.file_id
    file = await context.bot.get_file(file_id)
    
    # Use user ID to uniquely identify the user
    user_id = user.id

    # Generate file paths
    ogg_file_path = os.path.join(DOWNLOAD_PATH, f'{user_id}.ogg')
    mp3_file_path = os.path.join(DOWNLOAD_PATH, f'{user_id}.mp3')

    # Download the OGG file
    await file.download_to_drive(ogg_file_path)
    
    # Convert OGG to MP3
    audio = AudioSegment.from_ogg(ogg_file_path)
    audio.export(mp3_file_path, format="mp3")

    # Optionally, you can delete the original OGG file
    os.remove(ogg_file_path)

    # Send a textual reply to the user
    response_text = f'Your voice message has been saved as {mp3_file_path}.'
    await update.message.reply_text(response_text)

async def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, save_voice))

    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())