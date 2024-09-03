import nest_asyncio
nest_asyncio.apply()

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from pydub import AudioSegment
import requests
import time
import anthropic
import graphviz

# API tokens (replace with your actual tokens)
TELEGRAM_TOKEN = 'token'
ASSEMBLYAI_API_KEY = "api_key"
CLAUDE_API_KEY = "claude_api"
DOWNLOAD_PATH = './downloads/'

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_PATH):
    os.makedirs(DOWNLOAD_PATH)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(
        'Отправьте мне голосовое сообщение, и я сохраню его, расшифрую и получу ответ от Claude AI!'
    )


# Updated save_voice function
async def save_voice(update: Update, context: CallbackContext) -> None:
    try:
        user = update.message.from_user
        file_id = update.message.voice.file_id
        file = await context.bot.get_file(file_id)
        
        user_id = user.id

        ogg_file_path = os.path.join(DOWNLOAD_PATH, f'{user_id}.ogg')
        mp3_file_path = os.path.join(DOWNLOAD_PATH, f'{user_id}.mp3')

        await file.download_to_drive(ogg_file_path)
        
        audio = AudioSegment.from_ogg(ogg_file_path)
        audio.export(mp3_file_path, format="mp3")

        os.remove(ogg_file_path)

        transcript = transcribe_audio(mp3_file_path)

        print(f"Transcript received: {transcript}")

        if not transcript.strip():
            await update.message.reply_text("Транскрипция не удалась или вернула пустой текст. Попробуйте еще раз.")
            return

        # Get response from Claude AI
        response_text = get_claude_response('''Инструкция для ответа: если тебя спросят как подключать аудиотрубки.
                                            Для этих  случаев {2 стояка, до 25 этажных коммутаторов (всего)
                                                  Защита от переполюсовки + сокращение количества 
                                                жил в стояке и количества контактов.
                                                  Подключение абонентов с использованием 
                                                этажного коммутатора  ELTIS KMF-4.1 или KMF-6.1"}
                                                
                                                Верни graphviz code ниже c комментарием: "Это схема верна, если коммутаторов меньше или равно 25: 
                                            
                                            '// Doorphone System\ndigraph {\n\trankdir=TB size="12,8"\n\tdp [label="Блок вызова\nELTIS DP" fillcolor=black fontcolor=white shape=box style=filled]\n\tps [label="БП ELTIS\nPS2..." fillcolor=green fontcolor=white shape=box style=filled]\n\tcomm0 [label="Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)" fillcolor=blue fontcolor=white shape=box style=filled]\n\thandset00 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset01 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset02 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset03 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\tcomm1 [label="Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)" fillcolor=blue fontcolor=white shape=box style=filled]\n\thandset10 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset11 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset12 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset13 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\tdp -> ps [color=green]\n\tdp -> comm0 [label=3 color=blue]\n\tdp -> comm1 [label=3 color=blue]\n\tcomm0 -> handset00 [color=lightblue]\n\tcomm0 -> handset01 [color=lightblue]\n\tcomm0 -> handset02 [color=lightblue]\n\tcomm0 -> handset03 [color=lightblue]\n\tcomm1 -> handset10 [color=lightblue]\n\tcomm1 -> handset11 [color=lightblue]\n\tcomm1 -> handset12 [color=lightblue]\n\tcomm1 -> handset13 [color=lightblue]\n}\n'
                                            
                                            
                                            А для этих случаев {2 стояка, до 50 этажных коммутаторов на стояк
                                                          Защита от переполюсовки + сокращение количества 
                                                        жил в стояке и количества контактов.
                                                          Подключение абонентов с использованием 
                                                        этажного коммутатора  ELTIS KMF-4.1 или KMF-6.1 
                                                        и усилителя UD-SA-1}
                                            
                                            Верни graphviz code ниже c комментарием: "Это схема верна, если коммутаторов больше 25. Напиши в ответе, что требуется также усилитель
                                            
                                            '// Doorphone System\ndigraph {\n\trankdir=TB size="12,8"\n\tdp [label="Блок вызова\nELTIS DP" fillcolor=black fontcolor=white shape=box style=filled]\n\tps [label="БП ELTIS\nPS2..." fillcolor=green fontcolor=white shape=box style=filled]\n\tamp [label="Усилитель\nELTIS UD-SA-1" fillcolor=blue fontcolor=white shape=box style=filled]\n\tcomm0 [label="Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)" fillcolor=blue fontcolor=white shape=box style=filled]\n\thandset00 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset01 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset02 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset03 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\tcomm1 [label="Коммутатор\nELTIS KMF-4.1\n(или KMF- 6.1)" fillcolor=blue fontcolor=white shape=box style=filled]\n\thandset10 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset11 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset12 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\thandset13 [label="Абонентская\nаудиотрубка" fillcolor=orange shape=box style=filled]\n\tdp -> ps [color=green]\n\tdp -> amp [label=3 color=blue]\n\tamp -> comm0 [color=blue]\n\tamp -> comm1 [color=blue]\n\tps -> amp [label=2 color=green]\n\tcomm0 -> handset00 [color=lightblue]\n\tcomm0 -> handset01 [color=lightblue]\n\tcomm0 -> handset02 [color=lightblue]\n\tcomm0 -> handset03 [color=lightblue]\n\tcomm1 -> handset10 [color=lightblue]\n\tcomm1 -> handset11 [color=lightblue]\n\tcomm1 -> handset12 [color=lightblue]\n\tcomm1 -> handset13 [color=lightblue]\n}\n'
                                             
                                              Если в запросе будет четко указано сколько стояков и сколько абонентских аудиотрубок, то нарисуй их все.
                                              Если не указано, нарисуй 2 стояка и по 4 трубки на стояк.  
                                              Схемы должны быть нарисованы, используя код python Graphviz, строго внутри curly brackets {}.
                                            
                                            . Добавь, что схему 
                                                подключения абонентских устройств можно посмотреть по ссылке 
                                                https://www.eltis.com/download/audiotrubki-varianty-kommutacii-abonentov.pdf 
                                                Эта ссылка должна быть кликабельна, пользователь должен попадать на сайт.''' + transcript)
         
        # response_text = get_claude_response('''Инструкция для ответа: если тебя спросят как подключать аудиотрубки.
        #                                       Для этих  случаев {2 стояка, до 25 этажных коммутаторов (всего)
        #                                            Защита от переполюсовки + сокращение количества 
        #                                           жил в стояке и количества контактов.
        #                                            Подключение абонентов с использованием 
        #                                           этажного коммутатора  ELTIS KMF-4.1 или KMF-6.1"}
                                                  
                                            
                                              
        #                                       А для этих случаев {2 стояка, до 50 этажных коммутаторов на стояк
        #                                                    Защита от переполюсовки + сокращение количества 
        #                                                   жил в стояке и количества контактов.
        #                                                    Подключение абонентов с использованием 
        #                                                   этажного коммутатора  ELTIS KMF-4.1 или KMF-6.1 
        #                                                   и усилителя UD-SA-1}
                                              
                                             
        #                                        Если в запросе будет четко указано сколько стояков и сколько абонентских аудиотрубок, то нарисуй их все.
        #                                        Если не указано, нарисуй 2 стояка и по 4 трубки на стояк.                                                                                  
                                              
        #                                       . Добавь, что общую схему 
        #                                          подключения абонентских устройств можно посмотреть по ссылке 
        #                                          https://www.eltis.com/download/audiotrubki-varianty-kommutacii-abonentov.pdf 
        #                                          Эта ссылка должна быть кликабельна, пользователь должен попадать на сайт.''' + transcript)                                      

        print(f"Response from Claude: {response_text}")

        if not response_text.strip():
            await update.message.reply_text("Ответ от Claude AI пустой. Пожалуйста, попробуйте снова.")
        else:
            await update.message.reply_text(re.sub(r'\{[^}]*\}', '', response_text)) #just response_text

            # Process the DOT code response to generate diagrams
            generated_files = process_dot_code(response_text)

            # Attach each generated PNG file to the reply
            for file_path in generated_files:
                with open(file_path, 'rb') as file:
                    await update.message.reply_photo(photo=file)

    except Exception as e:
        print(f"Error in save_voice: {e}")
        await update.message.reply_text(
            "Извините, произошла ошибка при обработке вашего сообщения. Пожалуйста, попробуйте позже."
        )

def transcribe_audio(file_path):
    """Transcribe the audio file using AssemblyAI."""
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json'
    }

    # Upload the file
    upload_url = 'https://api.assemblyai.com/v2/upload'
    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, headers=headers, files={'file': f})
    
    if response.status_code != 200:
        raise Exception(f"Не удалось загрузить аудиофайл: {response.text}")
    
    audio_url = response.json().get('upload_url')
    if not audio_url:
        raise Exception("Не найден upload_url в ответе AssemblyAI.")

    # Request transcription with Russian language specification
    transcript_id = request_transcription(audio_url)

    # Poll for the transcription result
    polling_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    while True:
        poll_response = requests.get(polling_url, headers=headers)
        if poll_response.status_code != 200:
            raise Exception(f"Ошибка запроса транскрипции: {poll_response.text}")
        
        status = poll_response.json().get('status')
        if status == 'completed':
            return poll_response.json().get('text', '')
        elif status == 'failed':
            raise Exception('Транскрипция не удалась.')
        else:
            time.sleep(5)

def request_transcription(audio_url):
    """Request transcription from AssemblyAI with Russian language."""
    transcript_url = 'https://api.assemblyai.com/v2/transcript'
    transcript_request = {
        'audio_url': audio_url,
        'language_code': 'ru'  # Specify Russian language
    }
    headers = {
        'authorization': ASSEMBLYAI_API_KEY,
        'content-type': 'application/json'
    }
    response = requests.post(transcript_url, json=transcript_request, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    else:
        raise Exception(f"Ошибка запроса транскрипции: {response.json()}")

# Function to send text to Claude AI and get a response
def get_claude_response(text_to_send):
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    
    # Send message to Claude
    message = client.messages.create(
        model="claude-3-opus-20240229" , #claude-3-haiku-20240307"
        max_tokens=4096,
        messages=[
            {"role": "user", "content": text_to_send}
        ]
    )
    
    # Return the response text
    return message.content[0].text

def generate_graphviz_image(dot_code, output_file):
    # Create a Graphviz object
    graph = graphviz.Source(dot_code)
    
    # Render the graph to a file
    graph.render(output_file, format='png', cleanup=True)
    print(f"Image saved as {output_file}.png")

# Function to process and save diagrams from DOT code
import re


import os
from graphviz import Source

# Function to process and save diagrams from DOT code
def process_dot_code(dot_code_response):
    # Use regular expression to find all text blocks that start with digraph and end with the closing brace
    dot_parts = re.findall(r'digraph\s*{[^{}]*}', dot_code_response, re.DOTALL)
    
    generated_files = []  # List to store the paths of generated files
    
    # Generate and save images for each extracted block
    for i, dot_code in enumerate(dot_parts):
        # Clean the dot code (though it should already be complete)
        clean_dot_code = dot_code.strip()
        
        # Define the output filename
        output_file = f'diagram_{i + 1}'
        
        # Generate the image from the DOT code
        generate_graphviz_image(clean_dot_code, output_file)
        
        # Append the output file path to the list
        generated_files.append(f'{output_file}.png')
    
    return generated_files


# Example usage (not part of the function):
# response_text = "Some text {first DOT code} more text {second DOT code}"
# process_dot_code(response_text)

        
        

async def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, save_voice))

    # Optionally, add an error handler to log errors
    application.add_error_handler(error_handler)

    await application.run_polling()

async def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    # Log the error
    print(f"Update {update} caused error {context.error}")

    # Notify the user
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "Произошла непредвиденная ошибка. Пожалуйста, попробуйте позже."
        )

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

