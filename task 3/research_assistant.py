# research_assistant.py
"""
AI Research Assistant
- Uses SerpAPI for web search (multiple engines)
- Uses Google Gemini (ChatGoogleGenerativeAI) for summarization
- Fetches top URLs, summarizes them, and produces a final report
- Saves results to outputs/ and provides download buttons
"""

import os
import re
from datetime import datetime
from dotenv import load_dotenv

import streamlit as st
import requests
from bs4 import BeautifulSoup

# LangChain
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

# Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
# This is the correct import for safety settings
from google.generativeai.types import HarmBlockThreshold, HarmCategory

# SerpAPI
from langchain_community.utilities import SerpAPIWrapper

# ==============================
# Load environment variables
# ==============================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not GOOGLE_API_KEY or not SERPAPI_API_KEY:
    raise RuntimeError("Missing GOOGLE_API_KEY or SERPAPI_API_KEY in your .env file")

# ==============================
# Utilities
# ==============================
def fetch_webpage_text(url: str, max_chars: int = 8000) -> str:
    """Fetch readable text from a URL using requests + BeautifulSoup"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        text = " ".join(paragraphs)
        return text[:max_chars]
    except Exception as e:
        return f"[Error fetching {url}]: {e}"

def safe_filename(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_-]', '_', s)[:50]

# ==============================
# Initialize LLM (Gemini)
# ==============================
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash", # <-- Using the model name you confirmed works
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3,
    safety_settings={  # <-- Re-adding safety settings to prevent hanging
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    },
)

# ==============================
# Conversation memory
# ==============================
memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True,
    input_key="query"  # <-- THE FIX: Specify the main input key
)

# ==============================
# Research Chain
# ==============================
prompt = PromptTemplate(
    input_variables=["query", "sources"],
    template=(
        "You are a research assistant. Summarize the following web data based on the query: {query}\n\n"
        "Sources:\n{sources}\n\n"
        "Write a concise and factual summary in under 250 words."
    ),
)

research_chain = LLMChain(llm=llm, prompt=prompt, memory=memory)

# ==============================
# Streamlit UI
# ==============================
st.set_page_config(page_title="AI Research Assistant", layout="wide")
st.title("🧠 AI Research Assistant")
st.write("Search the web, summarize findings, and save results — powered by Gemini & LangChain")

query = st.text_input("🔍 Enter your research topic or question:")

# Multiple search engines fallback
search_engines = ["google", "bing", "duckduckgo"]

if st.button("Run Research") and query:
    with st.spinner("Searching and summarizing... (This may take a minute or two)"):
        urls = []
        for engine in search_engines:
            st.info(f"Searching via {engine.capitalize()}...")
            try:
                # 1. Define the search parameters, including the engine
                search_params = {
                    "engine": engine,
                    "gl": "us", # Added for location consistency (US)
                    "hl": "en", # Added for language consistency (English)
                }

                # 2. Pass this dictionary to the 'params' argument
                searcher = SerpAPIWrapper(
                    serpapi_api_key=SERPAPI_API_KEY,
                    params=search_params
                )

                # 3. Now call .results() with only the query
                results_dict = searcher.results(query)
                
                # Get the list of organic results, default to empty list if key not found
                organic_results = results_dict.get("organic_results", [])
                
                engine_urls = []
                if organic_results:
                    for item in organic_results:
                        if "link" in item:
                            engine_urls.append(item["link"])
                
                # Use dict.fromkeys to get unique URLs while preserving order, then limit to 5
                if engine_urls:
                    engine_urls = list(dict.fromkeys(engine_urls))[:5]
                

                if engine_urls:
                    st.success(f"✅ Found {len(engine_urls)} URLs using {engine.capitalize()}")
                    urls = engine_urls
                    break # Found URLs, stop trying other engines
                else:
                    st.warning(f"No URLs found on {engine.capitalize()}. Trying next engine...")
                    
            except Exception as e:
                st.warning(f"Search failed on {engine.capitalize()}: {e}")

        if not urls:
            st.error("No URLs found using any search engine. Try a different query.")
        else:
            summaries = []
            st.info("Summarizing fetched content (this is the slow part)...")
            
            for i, url in enumerate(urls, start=1):
                st.info(f"📄 Fetching source {i}: {url}")
                text = fetch_webpage_text(url)
                
                if len(text) < 100: # Increased minimum content length
                    st.warning(f"Skipped {url}, too little content")
                    continue
                
                st.write(f"Summarizing source {i} (approx {len(text)} chars)...")
                try:
                    # Summarize each page individually
                    summary_prompt = f"Based on the query '{query}', please summarize the key information from the following text:\n\n{text}"
                    summary = llm.invoke(summary_prompt)
                    
                    st.write(f"✅ Summary complete for source {i}.")
                    
                    summaries.append(f"Source {i}: {url}\n{summary.content}\n")
                except Exception as e:
                    st.error(f"Error summarizing {url}: {e}")

            if not summaries:
                st.error("Could not fetch or summarize any content from the found URLs.")
            else:
                st.info("Combining summaries into a final report...")
                combined_sources = "\n\n".join(summaries)
                
                # Run the final research chain
                final_summary = research_chain.run({"query": query, "sources": combined_sources})

                st.success("🎉 Research complete!")
                st.subheader("🧩 Combined Summary")
                st.write(final_summary)

                # Save to file
                os.makedirs("outputs", exist_ok=True)
                filename = f"outputs/{safe_filename(query)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                file_content = f"Query: {query}\n\n--- Combined Summary ---\n{final_summary}\n\n--- Individual Sources ---\n{combined_sources}"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(file_content)

                st.success(f"✅ Saved summary to {filename}")
                
                # Re-read for download button
                with open(filename, "r", encoding="utf-8") as file:
                    st.download_button(
                        "⬇️ Download Summary", 
                        data=file.read(), # Pass the content directly
                        file_name=os.path.basename(filename)
                    )