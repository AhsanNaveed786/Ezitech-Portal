from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

print("API Key:", os.getenv("GROQ_API_KEY"))

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)