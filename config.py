import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Φόρτωσε .env
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1").strip()
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()

# Ασφάλεια: αν λείπει το key, πέτα καθαρό μήνυμα από νωρίς
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Please set it in .env")

def get_llm():
    # Δίνουμε ρητά api_key & base_url στον ChatOpenAI client
    return ChatOpenAI(
        model=MODEL,
        api_key=API_KEY,
        base_url=BASE_URL,
        temperature=0.2,
        timeout=60,
        max_retries=2,
    )
