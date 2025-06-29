import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_URL = "https://api.openai.com/v1/chat/completions"

async def get_openai_response(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "Error: OPENAI_API_KEY not found. Ensure it is set in the .env file."

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for the VoidCat RDC venture."},
            {"role": "user", "content": prompt},
        ],
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, headers=headers, json=payload, timeout=30.0)
            
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        return f"Error: HTTP Status {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"