import requests
import os
response = requests.get(
    "https://api.murf.ai/v1/speech/voices",
    headers={"api-key": os.getenv("")}
)
#"ap2_ec86fbb2-c8ee-4cc0-845b-8396c807ac3c"
voices = response.json()
print(voices[0])
for voice in voices:
    if len(voice['supportedLocales'].keys())>21: 
        
        print(f"Voice ID: {voice['voiceId']}")
        print(f"Base Language: {voice['locale']}")
        print(f"Supported Locales: {', '.join(voice['supportedLocales'].keys())}")
        print(len(voice['supportedLocales'].keys()))
        print("\n\n")
    
    

