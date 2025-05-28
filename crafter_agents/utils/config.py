import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('OPENAI_API_KEY')

if not API_KEY:
    raise ValueError(
        "No API key found. Please set the OPENAI_API_KEY environment variable "
        "or create a .env file with OPENAI_API_KEY=your_api_key_here"
    )