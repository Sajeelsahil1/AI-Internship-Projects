import os
import google.generativeai as genai
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

# --- Define Knowledge Base ---
COMPANY_FAQ = """
Project Phoenix — A fitness tracking mobile app using Flutter and Firebase.
Features:
- Workout tracking
- Calorie and nutrition logging
- Social sharing of achievements
- Personalized goal setting
Release: Public beta planned for Q4.
"""

# --- Define the System Prompt ---
SYSTEM_PROMPT = f"""
You are 'PhoenixBot', an FAQ assistant for Project Phoenix.

Rules:
1. Only answer using the information in the FAQ below.
2. If a question is not covered, reply:
   "I'm sorry, I don't have that information. My knowledge is limited to Project Phoenix FAQs."

FAQ:
{COMPANY_FAQ}
"""

def main():
    # --- Load API key ---
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    try:
        # --- Configure Gemini ---
        genai.configure(api_key=api_key)

        # ✅ Use one of your available models
        model_name = "models/gemini-2.5-flash"  # Fast and reliable
        model = genai.GenerativeModel(model_name)

        print(f"🤖 Hello! I'm PhoenixBot (Gemini 2.5 Edition: {model_name}).")
        print("Ask me about Project Phoenix! (Type 'quit' to exit)\n")

        # --- Continuous Chat Loop ---
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                print("👋 Goodbye! Thanks for chatting.")
                break

            prompt = f"{SYSTEM_PROMPT}\n\nUser Question: {user_input}"
            response = model.generate_content(prompt)

            print(f"\nPhoenixBot: {response.text}\n")

    except Exception as e:
        print(f"⚠️ Error: {e}")
        print("Please check your API key, internet connection, or quota.")

if __name__ == "__main__":
    main()
