# -*- coding: utf-8 -*-
"""
Редактор Spyder

Это временный скриптовый файл.
"""

# https://www.convertcsv.com/csv-viewer-editor.htm
# https://www.assemblyai.com/dashboard/login (m_smirnov@yahoo.com)
# https://convertio.co/ru/webm-mp3/
 
import anthropic
import json
import pandas as pd
import os
import glob

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key= "the key",
)


###################################################
# read data saved data from Bitrix
###################################################


def get_last_saved_csv_file(folder_path, file_type):
    # file_type,e.g. '*.csv'
    
    # Create a pattern to match all CSV files in the specified folder
    pattern = os.path.join(folder_path, file_type)
    
    # Get a list of all CSV files in the directory
    csv_files = glob.glob(pattern)
    
    # If there are no CSV files, return None
    if not csv_files:
        return None
    
    # Find the CSV file with the most recent modification time
    latest_csv_file = max(csv_files, key=os.path.getmtime)
    
    return latest_csv_file

# Example usage
folder_path = 'C:\\Users\\134\\Documents\\ЭЛТИС\\Битрикс\\'

last_saved_file = get_last_saved_csv_file(folder_path, '*.csv')
# Read Bitrix data

df_bitrix = pd.read_csv(last_saved_file).to_csv(index=False)


###################################################
# read data from EMAIL
###################################################


folder_path = 'C:\\Users\\134\\Documents\\ЭЛТИС\\Почта\\'

last_saved_file = get_last_saved_csv_file(folder_path, '*.json')

# Read HTML file as text EMAIL
with open(last_saved_file, 'r', encoding='utf-8') as file:
    email_inbox_content = file.read()

text_to_send_email = f'''Analyse the JSON data below. 
It represents the emails from the INBOX folder. Make a summary in Russian what tasks were discussed. 
Based on the summary create a csv table 'Name of the task', 'Author of the task', 'date of task creation', 
'Person in charge', 'Current status'. Please, also add 'date' and 'from' columns 
(which are the email fields that mainly correspond the tasks summary). {email_inbox_content}'''    



###################################################  
# Read chat Telegram
###################################################


folder_path = 'C:\\Users\\134\\Documents\\ЭЛТИС\\Чаты Телеграм\\'
last_saved_file = get_last_saved_csv_file(folder_path, '*.txt')

with open(last_saved_file, 'r', encoding='utf-8') as file:
     telegram_chat_content = file.read() 

text_to_send_telegram = f'''Analyze the history of Telegram messages of sales department and the replies from consultants: 
    Мartina Rouge and Екатерина Генералова. Make a numbered list of all topics that were discussed and make a guess if the topic (task) was closed. 
    The result present in csv table with columns: topic name, topic starter (author), date, 
    persentage estimate (guess) if the topic is closed where 100% represents the closed topic. The summary should be in Russian. {telegram_chat_content}'''
		     


###################################################
# Read online meeting
###################################################

folder_path = 'C:\\Users\\134\\Documents\\ЭЛТИС\\Онлайн совещания\\'
last_saved_file = get_last_saved_csv_file(folder_path, '*.txt')

with open(last_saved_file, 'r', encoding='utf-8') as file:
     online_meeting_content = file.read()      
     
text_to_send_meeting = f'''Analyze the online meeting transcipt. Give the summary of all discussed tasks,giving also the number of the task which was outspoken.
Give name of the person in charge. Expected date of task completion. The output summary should be in Russian language and csv format. 
Also, provide the relevant detaild textual summary of the same information split csv table and textual summary by "##############################" {online_meeting_content}'''
		


text_to_send_overall = f''' There are 4 datasets:

Content from Bitrix: {df_bitrix}
Content from the email inbox: {email_inbox_content}
Content from the Telegram chat: {telegram_chat_content}
Content from an online meeting: {online_meeting_content}

Summary of Dataset #2 (Email Inbox):
Analyze the emails from the INBOX folder and summarize in Russian what tasks were discussed.
After the summary is completed, add the line "#################################".
Based on the summary, create a CSV table with the following columns in Russian:
'Name of the task'
'Author of the task'
'Date of task creation'
'Person in charge'
'Current status'
'Email subject' (where the task was first mentioned)
'Email date'
'From' (email sender)

Summary of Dataset #3 (Telegram Chat):
Analyze the history of Telegram messages from the sales department and the replies from consultants, specifically Martina Rouge and Екатерина Генералова among others.
Create a numbered list in Russian of all topics that were discussed and make a guess if the topic (task) was closed.
Present the result in a CSV table with the following columns:
'Topic name'
'Topic starter (author)'
'Date'
'Percentage estimate (guess) if the topic is closed' (where 100% represents the closed topic)

Summary of Dataset #4 (Online Meeting Transcript):
Analyze the transcript of the online meeting.
Summarize in Russian all discussed tasks.
Include in the summary:
The name of the person in charge
The expected date of task completion
Present the output in both a textual summary and a CSV table.

Mapping and Full Join of All Datasets:
Dataset #1 (Bitrix) is the ultimate truth for task tracking.
Perform a logical full join of Dataset #1 with Datasets #2, #3, and #4 based on the meaning of the task names.
Determine if Dataset #1 includes all tasks from Datasets #2, #3, and #4 or if any tasks are missing.
Present the final result in a CSV table containing all columns from all 4 datasets, with additional columns indicating the probability of 
a match for each dataset (where 100% is a perfect match).'''


def send_message(text_to_send):
    message = client.messages.create(
        model="claude-3-opus-20240229",  # You can switch to "claude-3-5-sonnet-20240620" if needed
        max_tokens=4096,  # Adjust tokens as required
        messages=[
            {"role": "user", "content": text_to_send}
        ]
    )
    return message.content

# get summaries from all resources
claude_reply_email = send_message(text_to_send_email)
claude_reply_telegram = send_message(text_to_send_telegram)
claude_reply_meeting = send_message(text_to_send_meeting)
		
# message = client.messages.create(
#     model=  "claude-3-opus-20240229", #"claude-3-5-sonnet-20240620",
#     #claude-3-5-sonnet-20240620 
#     max_tokens=4096, #1024
#     messages=[
#         {"role": "user", "content": text_to_send}
#     ]
# )
# print(message.content)



#############################################################################
# send attached files to Claude
import os
from pathlib import Path

def send_message(text_to_send, pdf_files=None):
    files = None
    if pdf_files:
        files = {}
        for pdf_file in pdf_files:
            file_path = Path(pdf_file)
            if file_path.is_file():
                with open(pdf_file, "rb") as f:
                    files[file_path.name] = f.read()

    message = client.messages.create(
        model="claude-3-opus-20240229",  # You can switch to "claude-3-5-sonnet-20240620" if needed
        max_tokens=4096,  # Adjust tokens as required
        messages=[
            {"role": "user", "content": text_to_send}
        ],
        files=files
    )
    return message.content

# Sample file
#"C:\Users\134\saved_pages\ELTIS_site\download\audiotrubki-dva-stojaka.pdf"

text_prompt = "Here is my textual prompt..."
pdf_files = ["path/to/file1.pdf", "path/to/file2.pdf"]
response = send_message(text_prompt, pdf_files)
print(response)


#######################################################################################

import nest_asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

# Apply nest_asyncio to allow running event loops in Jupyter or similar environments
nest_asyncio.apply()


api_id = api_id
api_hash = api_hash
channel_username = 'putnik1lv'

# Use StringSession for an in-memory session
session = StringSession()

client = TelegramClient(session, api_id, api_hash)

async def main():
    async with client:
        messages = await client.get_messages(channel_username, limit=10)
        for message in messages:
            print(message.text) 

client.loop.run_until_complete(main())



