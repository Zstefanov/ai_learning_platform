import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv(dotenv_path=".env")
API_KEY = os.getenv("TOGETHER_API_KEY")

if not API_KEY:
    raise Exception("Missing TOGETHER_API_KEY in .env")

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3-8b-chat-hf"  # Interchangeable with any other model available on Together AI

async def ask_together_ai(message: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a helpful programming tutor."},
            {"role": "user", "content": message}
        ],
        "temperature": 0.7
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                TOGETHER_API_URL,
                headers=headers,
                json=json_data,
                timeout=15.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 429:
                print("Rate limit exceeded.")
                return "Too many requests. Please try again later."
            else:
                print(f"Together API error: {exc.response.status_code} - {exc.response.text}")
                return "An error occurred. Try again later."
        except Exception as e:
            print(f"General error: {str(e)}")
            return "An error occurred. Try again later."
