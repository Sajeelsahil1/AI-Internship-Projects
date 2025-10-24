import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# Load environment variables
load_dotenv()
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Data for UI
COUNTRIES = {
    "United States": "us",
    "India": "in",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Australia": "au",
    "Pakistan": "pk",
    "Germany": "de"
}
CATEGORIES = ["world", "nation", "business", "technology", "entertainment", "sports", "science", "health"]

# ---------------- Fetch News Function (Unchanged) ----------------
def fetch_news(country, category):
    url = f"https://gnews.io/api/v4/top-headlines?country={country}&topic={category}&token={GNEWS_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return [article["title"] for article in articles[:5]] if articles else ["No news found."]
    else:
        return [f"Error fetching news: {response.status_code}"]

# ---------------- Summarize with Gemini (Unchanged) ----------------
def summarize_with_gemini(news_list):
    # NOTE: The model name "gemini-2.5-flash" might not exist.
    # The user should update this to a valid model like "gemini-1.5-flash".
    # For this example, I am keeping the user's original model name.
    model = genai.GenerativeModel("models/gemini-2.5-flash") 
    prompt = f"Summarize these latest news headlines in a short paragraph:\n{chr(10).join(news_list)}"
    response = model.generate_content(prompt)
    return response.text

# ---------------- UI Logic ----------------
def fetch_and_summarize():
    # Get the user-friendly name and map it to the API code
    country_name = country_var.get()
    country_code = COUNTRIES.get(country_name, "us") # Get code, default to 'us'
    category = category_var.get()

    news_display.config(state="normal")
    summary_display.config(state="normal")
    
    news_display.delete("1.0", tk.END)
    summary_display.delete("1.0", tk.END)
    news_display.insert(tk.END, "📰 Fetching latest news...\n")
    root.update_idletasks() # Force UI update

    headlines = fetch_news(country_code, category)
    news_display.delete("1.0", tk.END)
    news_display.insert(tk.END, "🌎 Latest Headlines:\n\n")
    for i, h in enumerate(headlines, 1):
        news_display.insert(tk.END, f"{i}. {h}\n\n")

    summary_display.insert(tk.END, "🤖 Summarizing with Gemini...\n")
    root.update_idletasks() # Force UI update

    try:
        summary = summarize_with_gemini(headlines)
        summary_display.delete("1.0", tk.END)
        summary_display.insert(tk.END, summary)
    except Exception as e:
        summary_display.delete("1.0", tk.END)
        messagebox.showerror("Gemini Error", f"Could not summarize: {e}")
        
    news_display.config(state="disabled")
    summary_display.config(state="disabled")


# ---------------- Tkinter UI ----------------
root = tk.Tk()
root.title("🌐 AI News Bot ")
root.geometry("900x700")
root.minsize(700, 600) # Set a minimum size

# --- Modern Styling ---
BG_COLOR = "#252526"
FG_COLOR = "#FFFFFF"
WIDGET_BG = "#3E3E42"
ACCENT_COLOR = "#007ACC" # Professional Blue
FONT_BOLD = ("Poppins", 13, "bold")
FONT_REGULAR = ("Poppins", 11)

root.configure(bg=BG_COLOR)

# --- Style Configuration ---
style = ttk.Style()
style.theme_use("clam")

# Global style for all widgets
style.configure(".",
                background=BG_COLOR,
                foreground=FG_COLOR,
                font=FONT_REGULAR,
                fieldbackground=WIDGET_BG,
                padding=5)

# Button Style
style.configure("TButton",
                font=FONT_BOLD,
                background=ACCENT_COLOR,
                foreground=FG_COLOR,
                borderwidth=0,
                padding=(20, 10)) # (horizontal, vertical)
style.map("TButton",
          background=[("active", "#005FA3")]) # Darker on click/hover

# Combobox Style
style.configure("TCombobox",
                arrowsize=15,
                fieldbackground=WIDGET_BG,
                background=WIDGET_BG,
                foreground=FG_COLOR)
# Style for the dropdown list itself
root.option_add("*TCombobox*Listbox*Background", WIDGET_BG)
root.option_add("*TCombobox*Listbox*Foreground", FG_COLOR)
root.option_add("*TCombobox*Listbox*selectBackground", ACCENT_COLOR)
root.option_add("*TCombobox*Listbox*selectForeground", FG_COLOR)

# Label Styles
style.configure("TLabel", font=FONT_REGULAR)
style.configure("Header.TLabel", font=FONT_BOLD) # A new style for headers
style.configure("TFrame", background=BG_COLOR)


# --- Main Layout Frames ---
# Using pack for the main sections, and grid inside the controls_frame
controls_frame = ttk.Frame(root, padding=(20, 20, 20, 10))
controls_frame.pack(fill="x", side="top", anchor="n")

output_frame = ttk.Frame(root, padding=(20, 10, 20, 20))
output_frame.pack(fill="both", expand=True, side="bottom")


# --- Controls Frame (Grid Layout) ---
controls_frame.grid_columnconfigure(1, weight=1) # Make combobox column expandable

# Row 0: Country
ttk.Label(controls_frame, text="🌎 Country:").grid(row=0, column=0, sticky="w", padx=(0, 10))
country_var = tk.StringVar(value="United States") # Default to display name
country_menu = ttk.Combobox(controls_frame, textvariable=country_var, values=list(COUNTRIES.keys()), state="readonly")
country_menu.grid(row=0, column=1, sticky="ew")

# Row 1: Category
ttk.Label(controls_frame, text="🗂️ Category:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=10)
category_var = tk.StringVar(value="world")
category_menu = ttk.Combobox(controls_frame, textvariable=category_var, values=CATEGORIES, state="readonly")
category_menu.grid(row=1, column=1, sticky="ew", pady=10)

# Row 0 & 1, Col 2: Button
fetch_button = ttk.Button(controls_frame, text="🚀 Fetch & Summarize", command=fetch_and_summarize)
fetch_button.grid(row=0, column=2, rowspan=2, sticky="ns", padx=(20, 0))


# --- Output Frame (Grid Layout) ---
output_frame.grid_rowconfigure(1, weight=1) # News text row
output_frame.grid_rowconfigure(3, weight=1) # Summary text row
output_frame.grid_columnconfigure(0, weight=1) # Single column

# News Header
ttk.Label(output_frame, text="📰 Latest News", style="Header.TLabel").grid(row=0, column=0, sticky="w", pady=(10, 5))

# News Display
news_display = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10,
                                         bg=WIDGET_BG, fg=FG_COLOR, font=FONT_REGULAR,
                                         relief="flat", borderwidth=0, 
                                         highlightthickness=1, # Subtle border
                                         highlightcolor=ACCENT_COLOR,
                                         padx=10, pady=10, state="disabled")
news_display.grid(row=1, column=0, sticky="nsew")

# Summary Header
ttk.Label(output_frame, text="🧠 AI Summary", style="Header.TLabel").grid(row=2, column=0, sticky="w", pady=(15, 5))

# Summary Display
summary_display = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, height=10,
                                            bg=WIDGET_BG, fg=FG_COLOR, font=FONT_REGULAR,
                                            relief="flat", borderwidth=0, 
                                            highlightthickness=1, # Subtle border
                                            highlightcolor=ACCENT_COLOR,
                                            padx=10, pady=10, state="disabled")
summary_display.grid(row=3, column=0, sticky="nsew")


root.mainloop()