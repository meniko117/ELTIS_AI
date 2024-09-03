import requests
import time
from pydub import AudioSegment
import os
from datetime import date

# Check the status
#https://www.assemblyai.com/app/processing-queue 

# Your AssemblyAI API key
api_key = api_key

# Endpoint for uploading files
upload_url = 'https://api.assemblyai.com/v2/upload'

# Path to your local audio file
#audio_file_path = "C:\\Users\\134\\Downloads\\Элтис-Закрытие-месяцев-23.08.24-14-02-36-—-запись.mp3"




# Specify the folder path
folder_path = "C:\\Users\\134\\Documents\\Телемост\\"

# Get the list of files
file = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))][0]

try:
    # Load the .webm audio file
    audio = AudioSegment.from_file("C:\\Users\\134\\Documents\\Телемост\\" + file, format="webm")
    
    # Export as .mp3
    audio.export("C:\\Users\\134\\Documents\\ЭЛТИС\\Онлайн совещания\\output.mp3", format="mp3")
    

finally:
    # Explicitly delete the audio object to free up resources
    del audio

audio_file_path ="C:\\Users\\134\\Documents\\ЭЛТИС\\Онлайн совещания\\output.mp3"

# Upload the file
def upload_file(file_path):
    with open(file_path, 'rb') as f:
        response = requests.post(upload_url, headers={'authorization': api_key}, files={'file': f})
    if response.status_code == 200:
        return response.json()['upload_url']
    else:
        raise Exception(f"Error uploading file: {response.json()}")

# Request transcription
def request_transcription(audio_url):
    transcript_url = 'https://api.assemblyai.com/v2/transcript'
    transcript_request = {
        'audio_url': audio_url,
        'language_code': 'ru'  # Specify Russian language
    }
    headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }
    response = requests.post(transcript_url, json=transcript_request, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    else:
        raise Exception(f"Error requesting transcription: {response.json()}")

        
def poll_transcription(transcript_id):
    status_url = f'https://api.assemblyai.com/v2/transcript/{transcript_id}'
    headers = {
        'authorization': api_key
    }
    while True:
        response = requests.get(status_url, headers=headers)
        if response.status_code == 200:
            status_data = response.json()
            status = status_data['status']
            if status == 'completed':
                return status_data['text']
            elif status == 'failed':
                raise Exception(f"Transcription failed: {status_data.get('error', 'No error message')}")
            else:
                print('Waiting for transcription to complete...')
                time.sleep(10)
        else:
            raise Exception(f"Error checking transcription status: {response.json()}")


# Main process
def main():
    try:
        print("Uploading file...")
        audio_url = upload_file(audio_file_path)
        print(f"File uploaded. Audio URL: {audio_url}")
        
        print("Requesting transcription...")
        transcript_id = request_transcription(audio_url)
        print(f"Transcription requested. Transcript ID: {transcript_id}")
        
        print("Polling for transcription completion...")
        transcript_text = poll_transcription(transcript_id)
        print("Transcription completed!")
        print("Transcript:", transcript_text)
        
        formatted_date = date.today().strftime("%d_%m_%Y")
        
        # Define the file path and content
        file_path = fr"C:\\Users\\134\\Documents\\ЭЛТИС\\Онлайн совещания\\транскрипт_совещания_{formatted_date}.txt"

        # Open the file in write mode and save the content
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(transcript_text)

        
        
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the script
if __name__ == "__main__":
    main()
