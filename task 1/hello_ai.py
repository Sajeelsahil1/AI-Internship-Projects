import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    """
    Main function to run the 'Hello AI' script using Google Gemini.
    """

    # 1. Load environment variables
    load_dotenv()

    # 2. Get the Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables.")
        print("Please check your .env file or environment settings.")
        return

    # 3. Configure the Gemini client
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        print("✅ Connected to Gemini successfully!")
        print("💬 Type 'exit' or 'quit' to end the conversation.\n")

        # 4. Continuous chat loop
        while True:
            user_input = input("🤖 You: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Goodbye!")
                break

            print("\n🧠 Thinking...\n")

            # 5. Generate response
            response = model.generate_content(user_input)

            # 6. Display response
            if response and response.text:
                print(f"💡 Gemini: {response.text}\n")
            else:
                print("⚠️ No response received.\n")

    except Exception as e:
        print(f"⚠️ Error: {e}")
        print("Please check your API key, internet connection, or quota.")

if __name__ == "__main__":
    main()
