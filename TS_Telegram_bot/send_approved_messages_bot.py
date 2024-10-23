# This script sends messages to users from the conversation log. 
# It enables the admin to edit messages before sending them.
import pandas as pd
import asyncio
from telegram import Bot
from dotenv import load_dotenv
import os


# Load the environment variables from the .env file
load_dotenv(dotenv_path='.env.txt')  # Specify the path if not named .env
# Access the API keys
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Your Telegram Bot Token
BOT_TOKEN = TELEGRAM_TOKEN

# Path to your CSV file
XLSX_FILE = 'conversation_log.xlsx'

# Define the expected column names as a semicolon-separated string
expected_columns_str = 'user_id;chat_id;answer;send_flag'
# Convert the string to a list using the semicolon as a separator
expected_columns = expected_columns_str.split(';')

async def send_messages():
    bot = Bot(token=BOT_TOKEN)

    # Read the CSV file using pandas
    df = pd.read_excel(XLSX_FILE)
    df_columns = df.columns.to_list()

    # Check if all expected columns are present
    missing_columns = [col for col in expected_columns if col not in df_columns]
    if missing_columns:
        print(f"Error: Missing columns in XLSX: {missing_columns}")
        return

    # Filter rows where send_flag is "1"
    rows_to_send = df[df['send_flag'] == 1]

    for index, row in rows_to_send.iterrows():
        user_id = row['user_id']
        chat_id = row['chat_id']
        answer = row['answer']
        
        try:
            await bot.send_message(chat_id=chat_id, text=answer)
            print(f"Message sent to user {user_id} in chat {chat_id}")

            # Update the send_flag to '0' after sending
            #df.at[index, 'send_flag'] = '0'
        except Exception as e:
            print(f"Failed to send message to user {user_id} in chat {chat_id}: {str(e)}")

    # Write the updated DataFrame back to the CSV file
    # df.to_csv(CSV_FILE, index=False, encoding='WINDOWS-1251')
    # print("CSV file updated with new send_flag values.")

if __name__ == '__main__':
    asyncio.run(send_messages())