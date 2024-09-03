
from telethon.sync import TelegramClient
import asyncio

api_id = '9703399'
api_hash = 'caa5096f6383a10c1bdcee34912e3499'
channel_username = 'putnik1lv'


client = TelegramClient('session_name', api_id, api_hash)


async def main():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        messages = await client.get_messages(channel_username, limit=10)
        for message in messages:
            print(message.text)

# Use this if you're in a Jupyter notebook
import nest_asyncio
nest_asyncio.apply()

# Run the main function
asyncio.run(main())