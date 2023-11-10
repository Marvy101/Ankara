import json

with open('/Users/omdada/Documents/Code/Ankara/validVoices', 'r') as f:
    voices = json.load(f)

for voice in voices:
    print(voice['name'])
 