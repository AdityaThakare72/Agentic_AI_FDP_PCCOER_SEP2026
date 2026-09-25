"""
Creates the Gemini chat model used by every node in the graph.

Keeping this in one place means that if we ever want to switch models,
change the temperature, or add retries, there is exactly one line to edit.
"""

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# reads GOOGLE_API_KEY and TAVILY_API_KEY from the .env file into the environment
load_dotenv()

MODEL_NAME = "gemini-2.5-flash"


def get_model(temperature: float = 0.3):
    """Return a Gemini chat model. Lower temperature = more predictable output."""
    return ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=temperature)
