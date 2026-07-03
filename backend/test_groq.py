import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()
from groq import Groq

key = os.getenv("GROQ_API_KEY", "")
client = Groq(api_key=key)

# Try current models
models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

for m in models:
    try:
        resp = client.chat.completions.create(
            model=m,
            messages=[{"role":"user","content":"Say OK"}],
            max_tokens=5
        )
        print(f"  WORKS: {m}")
    except Exception as e:
        print(f"  FAIL:  {m} -> {str(e)[:80]}")
