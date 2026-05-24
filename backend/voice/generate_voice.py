import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

text = """
Shipment SH1024 appears delayed.
Please provide updated delivery status.
"""

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "text": text,
    "model_id": "eleven_multilingual_v2"
}

response = requests.post(
    url,
    json=data,
    headers=headers
)

with open("dispatcher_voice.mp3", "wb") as f:
    f.write(response.content)

print("Dispatcher voice generated.")