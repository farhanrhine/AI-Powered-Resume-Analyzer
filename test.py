"""
test.py — Quick sanity-check for the Gemini API key.
Model  : gemini-2.5-flash (free tier, active as of July 2026)
SDK    : langchain-google-genai (already a project dependency)
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# ── Load API key ──────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=".env")          # reads the '.env' file in project root
api_key = os.getenv("Gemini_API_Key")

if not api_key:
    raise EnvironmentError(
        "Gemini_API_Key not found. "
        "Make sure it is set in the 'env' file at the project root."
    )

print(f"[OK]  API key loaded ({api_key[:8]}...)")

# ── Initialise model ──────────────────────────────────────────────────────────
MODEL = "gemini-3.5-flash"              # free-tier, active as of July 2026 (2.0-flash deprecated June 1 2026)

llm = ChatGoogleGenerativeAI(
    model=MODEL,
    google_api_key=api_key,
    temperature=0.7,
)

print(f"[OK]  Model initialised : {MODEL}\n")

# ── Send a test prompt ────────────────────────────────────────────────────────
prompt = "Say hello and tell me what you are in one sentence."

print(f"[>>]  Prompt  : {prompt}")
print("[..]  Waiting for response ...\n")

response = llm.invoke(prompt)

print("-" * 60)
print(f"[<<]  Response:\n{response.text}")
print("-" * 60)
print("\n[DONE]  Gemini API is working correctly!")
