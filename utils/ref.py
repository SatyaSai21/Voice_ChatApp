import requests
import os
response = requests.get(
    "https://api.murf.ai/v1/speech/voices",
    headers={"api-key": os.getenv("MURF_API_KEY")}
)

voices = response.json()
print(voices[0])
for voice in voices:
    if len(voice['supportedLocales'].keys())>21: 
        
        print(f"Voice ID: {voice['voiceId']}")
        print(f"Base Language: {voice['locale']}")
        print(f"Supported Locales: {', '.join(voice['supportedLocales'].keys())}")
        print(len(voice['supportedLocales'].keys()))
        print("\n\n")
    
    

