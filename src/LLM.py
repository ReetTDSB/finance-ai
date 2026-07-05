from groq import Groq
from dotenv import load_dotenv
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

def generate_report(prompt):
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "ERROR: GROQ_API_KEY not found in .env file"
        
        client = Groq(api_key=api_key)
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a finance analyst. Use ONLY the exact numbers provided in the prompt. Do not use prior knowledge about stock prices. Educational only, not financial advice."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Report generation failed: {e}"