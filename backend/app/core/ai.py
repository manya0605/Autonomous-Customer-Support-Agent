import os

from dotenv import load_dotenv
from openai import OpenAI


# Load variables from the project-root .env
load_dotenv()


API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY is not configured.")


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

MODEL = "openrouter/free"