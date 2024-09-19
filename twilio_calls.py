# call_handler.py

from flask import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests

app = Flask(__name__)

@app.route("/incoming_call", methods=['POST'])
def handle_call():
    response = VoiceResponse()

    # Gather speech input from the user
    gather = Gather(input='speech', action='/process_speech', timeout=5)
    gather.say("Hello! Welcome to Tech Support. Please describe your issue.")
    response.append(gather)

    return str(response)

@app.route("/process_speech", methods=['POST'])
def process_speech():
    # Get the transcribed speech text from the Twilio request
    speech_text = request.form['SpeechResult']
    
    # Send the speech text to the NLP processor
    response_text = process_nlp(speech_text)
    
    # Convert the response text to speech
    speech_url = text_to_speech(response_text)
    
    # Create a response to play the generated speech
    response = VoiceResponse()
    response.play(speech_url)
    
    return str(response)

def process_nlp(text):
    # Send the text to the NLP processor (next script)
    response = requests.post('http://localhost:5001/generate_response', json={'text': text})
    return response.json().get('response')

def text_to_speech(text):
    # Send the text to the TTS processor (next script)
    response = requests.post('http://localhost:5002/generate_speech', json={'text': text})
    return response.json().get('speech_url')

if __name__ == "__main__":
    app.run(use_reloader=False)  # This disables the reloader that causes issues in interactive environments
    #app.run(host="0.0.0.0", port=5000, debug=True)
