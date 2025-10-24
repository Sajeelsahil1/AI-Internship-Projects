import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Loads your .env file

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("🔍 Fetching available Gemini models...\n")

for model in genai.list_models():
    print(f"🧩 Model name: {model.name}")
    print(f"   Supported generation methods: {model.supported_generation_methods}\n")
