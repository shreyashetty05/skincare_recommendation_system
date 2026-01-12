import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyAWPIh-l0frWlUFUye5pSMb7zxY-yE4AhA")

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
